"""What If: "e se tutti facessero X?" raccontato come un effetto farfalla, poi il twist vero.

Struttura (presa dai video virali del genere):
1. hook: la domanda, sopra la scena già in movimento
2. scena reale: luogo, ora, un protagonista colorato in mezzo a una folla grigia
3. escalation: lo zoom esce di potenze di dieci (strada, città, paese, globo, spazio) e a ogni
   salto le conseguenze diventano più grandi e più assurde
4. rewind: si torna indietro di colpo
5. twist: il dato reale, con fonte, che ribalta la premessa
6. chiusura sulla stessa inquadratura dell'inizio: il video ricomincia senza stacchi

Una storia è una lista di Beat: ogni beat cambia solo quello che gli serve (didascalia, camera,
orologio, KPI...), il resto prosegue dal beat prima. Tutto vive su un piano unico in metri
centrato sull'origine della storia (vedi geo.py).
"""

import datetime as dt
import math
from dataclasses import dataclass, field

import numpy as np
import skia

from . import geo, gfx
from .base import FPS, H, W
from .gfx import INK, draw_text, ease_in_out, ease_out, rgba

AMBER = (242, 196, 120)
SPACE = (7, 8, 10)
SEA = (22, 25, 29)
LAND = (37, 41, 47)
BORDER = (66, 72, 82)
GROUND = (28, 32, 30)
MOON_POS = (2.47e8, 2.94e8)
R_MOON = 1_737_000.0

MARGIN = 64
PIVOT_Y = H * 0.56     # punto fisso dell'inclinazione prospettica
FOCAL = 1.25 * H
LOOP_FADE = 0.5
CPS = 38.0             # caratteri al secondo della macchina da scrivere
CAPTION_Y = 520


@dataclass
class Beat:
    at: float
    text: str = None          # didascalia ('' la toglie)
    sub: str = None
    hook: bool = False        # la domanda iniziale, grande e centrata
    point: str = None         # linea dalla didascalia a un'ancora della scena (es. "hero")
    cam: dict = None          # {"w": metri di larghezza, "c": (x, y) | "hero" | "moon", "pitch": gradi, "dy": metri}
    move: float = 1.8
    place: str = None
    when: dt.datetime = None
    live: bool = False        # l'orologio scorre in tempo reale da qui
    tag: str = None           # riga in ambra sotto la data (None = automatica)
    jump: str = None          # "+3 MONTHS" sopra la didascalia
    kpi: float = None
    kpi_label: str = None
    kpi_base: float = None    # riferimento per la variazione %
    kpi2: tuple = None        # (etichetta, valore) oppure () per toglierlo
    spread: float = None      # raggio (km) dell'effetto che si allarga sulla mappa
    hatch: tuple = None       # (("states", "all"), ("countries", ["Canada"]), ...)
    scene: tuple = None       # (registrazione, tempo sim a inizio beat[, "earth" | "moon"])
    split: float = None       # confronto affiancato tra due registrazioni (0..1)
    fx: str = None            # "rewind" | "hit" (colpo basso nell'audio)
    fx_dur: float = 1.8


@dataclass
class Story:
    name: str
    start: dt.datetime        # l'istante "zero" della storia (per DAY n, YEAR n)
    origin: tuple             # (lat, lon)
    duration: float
    beats: list
    kpi_base: float
    kpi_format: object        # valore -> stringa
    units: str = "imperial"
    labels: tuple = ()        # (testo, lat, lon, w_min, w_max, (dx, dy))
    copy: dict = field(default_factory=dict)
    sources: tuple = ()


# ---------- tracce ----------

def _steps(beats, attr):
    return [(b.at, getattr(b, attr)) for b in beats if getattr(b, attr) is not None]


def _last(track, t, default=None):
    out = default
    for tt, v in track:
        if tt <= t:
            out = v
        else:
            break
    return out


def _segment(track, t, default):
    """(t del keyframe corrente, valore corrente, valore precedente); prima del primo keyframe vale default."""
    prev, cur, t0 = default, default, -1e9
    for tt, v in track:
        if tt <= t:
            prev, cur, t0 = cur, v, tt
        else:
            break
    return t0, cur, prev


def fmt_dist(m, units):
    if units == "imperial":
        mi = m / 1609.344
        if mi < 0.1:
            return f"{m * 3.281:,.0f} FT"
        return f"{mi:,.1f} MI" if mi < 10 else f"{mi:,.0f} MI"
    if m < 1000:
        return f"{m:,.0f} M"
    return f"{m / 1000:,.1f} KM" if m < 10_000 else f"{m / 1000:,.0f} KM"


def _nice(v):
    """1, 2, 5 x 10^k più vicino per difetto."""
    e = 10 ** math.floor(math.log10(v))
    for k in (5, 2, 1):
        if k * e <= v:
            return k * e
    return e


class Camera:
    """Vista corrente: larghezza (m), centro (m) e inclinazione prospettica (gradi)."""

    def __init__(self, w, cx, cy, pitch):
        self.w, self.cx, self.cy, self.pitch = w, cx, cy, pitch
        s = W / w
        th = math.radians(pitch)
        tilt = np.array([[1, 0, 0], [0, math.cos(th), 0], [0, -math.sin(th) / FOCAL, 1]])
        self.m = (np.array([[1, 0, W / 2], [0, 1, PIVOT_Y], [0, 0, 1]]) @ tilt
                  @ np.array([[s, 0, 0], [0, -s, 0], [0, 0, 1]]))

    @property
    def px(self):
        """Metri per pixel al centro."""
        return self.w / W

    def matrix(self, ox=0.0, oy=0.0):
        """Matrice skia per disegnare in metri attorno a (ox, oy): calcolata in float64, così anche
        lontano dall'origine (la Luna) non perde precisione."""
        m = self.m @ np.array([[1, 0, ox - self.cx], [0, 1, oy - self.cy], [0, 0, 1]])
        m = m / m[2, 2]
        return skia.Matrix.MakeAll(*(float(v) for v in m.ravel()))

    def to_screen(self, x, y):
        p = self.m @ np.array([x - self.cx, y - self.cy, 1.0])
        return p[0] / p[2], p[1] / p[2]

    def to_world(self, sx, sy):
        p = np.linalg.solve(self.m, np.array([sx, sy, 1.0]))
        return p[0] / p[2] + self.cx, p[1] / p[2] + self.cy

    def visible_y(self, margin=0.15):
        ys = [self.to_world(sx, sy)[1] for sx in (0, W) for sy in (0, H)]
        span = max(ys) - min(ys)
        return min(ys) - margin * span, max(ys) + margin * span

    def near(self, x, y, r):
        return math.hypot(self.cx - x, self.cy - y) < r + self.w * 1.5


class Timeline:
    """Stato di ogni elemento a ogni istante, ricavato dai beat."""

    def __init__(self, story, scene):
        self.story = story
        self.scene = scene
        b = sorted(story.beats, key=lambda x: x.at)
        self.beats = b
        self.cam = [(x.at, x.cam, x.move) for x in b if x.cam is not None]
        self.clock = [(x.at, x.move, (x.when - story.start).total_seconds(), x.live) for x in b if x.when is not None]
        self._clock_v0 = []
        for i, (t, *_rest) in enumerate(self.clock):
            self._clock_v0.append(self.clock[0][2] if i == 0 else self._clock_at(i - 1, t))
        self.kpi = _steps(b, "kpi")
        self.kpi_label = _steps(b, "kpi_label")
        self.kpi_base = _steps(b, "kpi_base")
        self.kpi2 = _steps(b, "kpi2")
        self.place = _steps(b, "place")
        self.tag = [(x.at, x.tag) for x in b if x.tag is not None or x.when is not None]
        self.jump = _steps(b, "jump")
        self.spread = _steps(b, "spread")
        self.hatch = _steps(b, "hatch")
        self.scene_tr = _steps(b, "scene")
        self.split = _steps(b, "split")
        self.fx = [(x.at, x.fx, x.fx_dur) for x in b if x.fx]
        self.hud_on = min((x.at for x in b if x.place), default=0.0)

        # Didascalie: dall'inizio fino al beat che ne mette un'altra (o la toglie).
        caps = [x for x in b if x.text is not None]
        self.captions = []
        for i, x in enumerate(caps):
            end = caps[i + 1].at if i + 1 < len(caps) else story.duration + 1
            if x.text:
                cam = _last([(t, spec) for t, spec, _ in self.cam], x.at + 0.01)
                layout = "hook" if x.hook else ("left" if cam and cam["w"] > 1500 else "center")
                self.captions.append(dict(t0=x.at, t1=end, text=x.text, sub=x.sub, layout=layout, point=x.point,
                                          jump=x.jump))

    # --- camera ---

    def _resolve(self, spec, vt):
        c = spec.get("c", (0.0, 0.0))
        if isinstance(c, str):
            x, y = self.scene.anchor(c, vt, self)
        else:
            x, y = c
        return spec["w"], x, y + spec.get("dy", 0.0), spec.get("pitch", 0.0)

    def camera(self, vt):
        prev = cur = None
        t0, dur = 0.0, 1.0
        for tt, spec, mv in self.cam:
            if tt <= vt:
                prev, cur, t0, dur = cur, spec, tt, mv
        if cur is None:
            cur, prev = self.cam[0][1], None
        w1, x1, y1, p1 = self._resolve(cur, vt)
        k = ease_in_out((vt - t0) / dur) if prev is not None else 1.0
        if k >= 1.0:
            return Camera(w1, x1, y1, p1)
        w0, x0, y0, p0 = self._resolve(prev, vt)
        w = math.exp(math.log(w0) + (math.log(w1) - math.log(w0)) * k)
        if abs(math.log(w1 / w0)) > 0.3:
            # Zoom attorno al punto d'arrivo: resta in vista e scivola al centro mentre si zooma.
            u = (w - w1) / (w0 - w1)
            x, y = x1 + (x0 - x1) * u, y1 + (y0 - y1) * u
        else:
            x, y = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
        return Camera(w, x, y, p0 + (p1 - p0) * k)

    # --- orologio e numeri ---

    def _clock_at(self, i, vt):
        t0, mv, target, live = self.clock[i]
        if live:
            return target + max(0.0, vt - t0)
        v0 = self._clock_v0[i]
        v = v0 + (target - v0) * ease_in_out((vt - t0) / mv)
        if target > v0:  # dopo il salto il tempo continua a scorrere piano (DAY 99, 100, 101...)
            v += max(0.0, vt - t0 - mv) * (target - v0) * 0.04
        return v

    def clock_s(self, vt):
        """Secondi dall'inizio della storia mostrati dall'orologio: durante i movimenti di camera gira veloce."""
        i = max((j for j, kf in enumerate(self.clock) if kf[0] <= vt), default=0)
        return self._clock_at(i, vt)

    def is_live(self, vt):
        return _last([(kf[0], kf[3]) for kf in self.clock], vt, True)

    def kpi_value(self, vt):
        t0, cur, prev = _segment(self.kpi, vt, self.story.kpi_base)
        return prev + (cur - prev) * ease_out((vt - t0) / 0.9)

    def spread_km(self, vt):
        t0, cur, prev = _segment(self.spread, vt, 0.0)
        if cur <= 0.0:
            return 0.0
        prev = max(prev, 0.1)
        k = ease_in_out((vt - t0) / 2.6)
        return math.exp(math.log(prev) + (math.log(max(cur, 0.1)) - math.log(prev)) * k)

    def scene_state(self, vt):
        st = _last(self.scene_tr, vt)
        t0 = max((tt for tt, _ in self.scene_tr if tt <= vt), default=0.0)
        rec, sim0 = st[0], st[1]
        where = st[2] if len(st) > 2 else "earth"
        return rec, sim0 + (vt - t0), where

    def split_k(self, vt):
        t0, cur, prev = _segment(self.split, vt, 0.0)
        return prev + (cur - prev) * ease_in_out((vt - t0) / 1.8)

    def fx_k(self, vt, kind):
        for t0, k, d in self.fx:
            if k == kind and t0 <= vt < t0 + d:
                return (vt - t0) / d
        return None


class Renderer:
    def __init__(self, story, scene):
        self.story = story
        self.scene = scene
        self.tl = Timeline(story, scene)
        self.atlas = geo.Atlas(*story.origin)
        self.n_frames = int(story.duration * FPS)
        self.buf = np.zeros((H, W, 4), np.uint8)
        self.surface = skia.Surface(self.buf)
        self.frame0 = None
        rng = np.random.default_rng(3)
        self.stars = [(float(rng.uniform(0, W)), float(rng.uniform(0, H)), float(rng.uniform(0.6, 2.2)),
                       float(rng.uniform(0, 6.28))) for _ in range(220)]
        self.labels = [(txt, *self.atlas.at(lat, lon), wmin, wmax, off)
                       for txt, lat, lon, wmin, wmax, off in story.labels]
        self._region_d = {}
        for kind in ("states", "countries"):
            for name, p in getattr(self.atlas, kind).items():
                r = p.getBounds()
                self._region_d[(kind, name)] = math.hypot(r.centerX(), r.centerY()) / 1000

    # ---------- frame ----------

    def render(self, f):
        vt = f / FPS
        c = self.surface.getCanvas()
        c.clear(rgba(SPACE))
        cam = self.tl.camera(vt)
        lw = math.log10(cam.w)
        # La scena resta visibile fino a ~20 km (strada sottile e puntini); il terreno sfuma prima e scopre la mappa.
        scene_a = 1 - ease_in_out((lw - math.log10(6000)) / (math.log10(20000) - math.log10(6000)))
        map_a = ease_in_out((lw - math.log10(1500)) / (math.log10(5000) - math.log10(1500)))
        space_a = ease_in_out((lw - 7.3) / 0.6)

        self._stars(c, vt, space_a)
        if cam.near(0, 0, geo.R_EARTH) and map_a > 0:
            self._earth(c, cam, vt, map_a)
        if cam.near(*MOON_POS, R_MOON):
            self._moon(c, cam)
        if scene_a > 0:
            self.scene.draw(c, cam, vt, self.tl, scene_a, ground=1 - map_a)
        if space_a > 0:
            self._space_marks(c, cam, space_a)
        self._map_labels(c, cam, map_a)
        self._shade(c)
        self._hud(c, cam, vt)
        self._captions(c, cam, vt)
        self._rewind(c, vt)
        if self.frame0 is not None and vt > self.story.duration - LOOP_FADE:
            k = ease_in_out((vt - (self.story.duration - LOOP_FADE)) / LOOP_FADE)
            c.drawImage(self.frame0, 0, 0, skia.SamplingOptions(), skia.Paint(Alphaf=k))
        if f == 0:
            self.frame0 = skia.Image.fromarray(self.buf.copy())
        return self.buf

    # ---------- livelli ----------

    def _stars(self, c, vt, a):
        if a <= 0:
            return
        for x, y, r, ph in self.stars:
            tw = 0.55 + 0.45 * math.sin(vt * 1.7 + ph)
            c.drawCircle(x, y, r * 0.7, skia.Paint(AntiAlias=True, Color=rgba(INK, a * 0.5 * tw)))

    def _earth(self, c, cam, vt, a):
        at = self.atlas
        px = cam.px
        M = cam.matrix()
        c.save()
        c.concat(M)
        c.drawCircle(0, 0, geo.R_EARTH, skia.Paint(AntiAlias=True, Color=rgba(SEA, a)))
        c.drawPath(at.land, skia.Paint(AntiAlias=True, Color=rgba(LAND, a)))
        border = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=px * 1.6,
                            Color=rgba(BORDER, a))
        for p in at.countries.values():
            c.drawPath(p, border)
        if cam.w < 9e6:
            sa = a * min(1.0, 1.4 - math.log10(cam.w) / 7)
            dash = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=px * 1.3,
                              Color=rgba(BORDER, sa), PathEffect=skia.DashPathEffect.Make([px * 7, px * 6], 0))
            for p in at.states.values():
                c.drawPath(p, dash)
        c.restore()

        # Regioni tratteggiate: si accendono quando l'onda (spread) le raggiunge. Quelle già accese
        # finiscono in un path solo (un clip e un tratteggio invece di uno per regione).
        spread = self.tl.spread_km(vt)
        for kind, names in _last(self.tl.hatch, vt, ()) or ():
            regions = getattr(at, kind)
            full = skia.Path()
            full.setFillType(skia.PathFillType.kEvenOdd)
            for name in (regions if names == "all" else names):
                d = self._region_d[(kind, name)]
                k = min(1.0, max(0.0, (spread - d) / (0.25 * spread + 50)))
                if k >= 1.0:
                    full.addPath(regions[name])
                elif k > 0:
                    self._hatch(c, M, regions[name], a * k, px)
            if not full.isEmpty():
                self._hatch(c, M, full, a, px)

        # Puntini accesi entro il raggio dell'onda e bagliore sull'origine.
        n = int(np.searchsorted(at.dots[1], spread))
        if n:
            c.save()
            c.concat(M)
            c.drawPoints(skia.Canvas.kPoints_PointMode, at.dots[0][:n], skia.Paint(
                AntiAlias=True, StrokeWidth=px * 3.4, StrokeCap=skia.Paint.kRound_Cap, Color=rgba(AMBER, 0.8 * a)))
            c.restore()
        ox, oy = cam.to_screen(0, 0)
        if spread > 0 and cam.w > 2500 and -200 < ox < W + 200 and -200 < oy < H + 200:
            pulse = 0.75 + 0.25 * math.sin(vt * 3)
            c.drawCircle(ox, oy, 38, skia.Paint(AntiAlias=True, Color=rgba(AMBER, 0.35 * a * pulse),
                                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16)))
            c.drawCircle(ox, oy, 9, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2,
                                               Color=rgba(AMBER, a)))
            c.drawCircle(ox, oy, 4, skia.Paint(AntiAlias=True, Color=rgba(AMBER, a)))
        if cam.w > 6e6:
            # alone dell'atmosfera sul bordo del globo
            r = geo.R_EARTH / cam.px
            gx, gy = cam.to_screen(0, 0)
            c.drawCircle(gx, gy, r, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3,
                                               Color=rgba((150, 175, 210), 0.35 * a),
                                               MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6)))

    def _hatch(self, c, M, path, a, px):
        c.save()
        c.concat(M)
        c.drawPath(path, skia.Paint(AntiAlias=True, Color=rgba(AMBER, 0.08 * a)))
        c.drawPath(path, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=px * 2.0,
                                    Color=rgba(AMBER, 0.75 * a)))
        c.clipPath(path, doAntiAlias=True)
        c.resetMatrix()
        p = skia.Paint(AntiAlias=True, StrokeWidth=2.2, Color=rgba(AMBER, 0.42 * a))
        for k in range(-H, W + H, 15):
            c.drawLine(k, 0, k + H, H, p)
        c.restore()

    def _moon(self, c, cam):
        mx, my = MOON_POS
        px = cam.px
        c.save()
        c.concat(cam.matrix(mx, my))
        c.drawCircle(0, 0, R_MOON, skia.Paint(AntiAlias=True, Color=rgba((112, 112, 117))))
        # Crateri a più scale attorno al punto d'atterraggio: a ogni zoom ce n'è qualcuno.
        rng = np.random.default_rng(42)
        for size in (2e5, 2e4, 2e3, 200.0, 20.0):
            pts = rng.uniform(-1, 1, (40, 2)) * size * 8
            rs = size * (0.2 + 0.8 * rng.random(40) ** 3)
            if not (px * 3 < size < cam.w * 3):
                continue
            # Cratere: conca appena più scura, ombra sul bordo in alto a sinistra, orlo chiaro in basso a destra.
            for (x, y), r in zip(pts, rs):
                x, y, r = float(x), float(y), float(r)
                if math.hypot(x, y) + r > R_MOON or (size < 300 and abs(x) < 30):
                    continue
                c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color=rgba((104, 104, 109))))
                c.drawArc(skia.Rect(x - r, y - r, x + r, y + r), 100, 160, False, skia.Paint(
                    AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.16, Color=rgba((88, 88, 93))))
                c.drawArc(skia.Rect(x - r, y - r, x + r, y + r), 280, 160, False, skia.Paint(
                    AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.1, Color=rgba((128, 128, 133))))
        c.restore()

    def _space_marks(self, c, cam, a):
        if cam.w < 5e6:
            return
        ex, ey = cam.to_screen(0, 0)
        mx, my = cam.to_screen(*MOON_POS)
        r = math.hypot(*MOON_POS) / cam.px
        if cam.w > 3e7:
            c.drawCircle(ex, ey, r, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.6,
                                               Color=rgba(INK, 0.22 * a)))
        f = gfx.mono(26)
        for name, (x, y), rr in (("EARTH", (ex, ey), geo.R_EARTH / cam.px), ("MOON", (mx, my), R_MOON / cam.px)):
            if rr < 60 and -50 < x < W + 50 and -50 < y < H + 50:
                c.drawCircle(x, y, max(rr, 5), skia.Paint(AntiAlias=True, Color=rgba(
                    (120, 150, 190) if name == "EARTH" else (170, 170, 175), a)))
                c.drawLine(x + 10, y - 10, x + 52, y - 52, skia.Paint(AntiAlias=True, StrokeWidth=1.5,
                                                                      Color=rgba(INK, 0.6 * a)))
                draw_text(c, name, f, x + 60, y - 52, color=INK, alpha=0.85 * a, align="left", vcenter=True,
                          tracking=1)

    def _map_labels(self, c, cam, a):
        if a <= 0 or cam.w > 2e7:
            return
        f = gfx.mono(27, "Medium")
        lw = math.log10(cam.w)
        for txt, x, y, wmin, wmax, (dx, dy) in self.labels:
            k = a * min(ease_in_out((lw - math.log10(wmin)) * 3), ease_in_out((math.log10(wmax) - lw) * 3))
            if k <= 0:
                continue
            sx, sy = cam.to_screen(x, y)
            if not (-100 < sx < W + 100 and -100 < sy < H + 100):
                continue
            c.drawLine(sx, sy, sx + dx * 0.85, sy + dy * 0.85,
                       skia.Paint(AntiAlias=True, StrokeWidth=1.6, Color=rgba(INK, 0.55 * k)))
            c.drawCircle(sx, sy, 5, skia.Paint(AntiAlias=True, Color=rgba(AMBER, k)))
            draw_text(c, txt, f, sx + dx, sy + dy, color=AMBER, alpha=k, align="left" if dx >= 0 else "right",
                      vcenter=True, tracking=1.5)

    def _shade(self, c):
        """Sfumatura scura in alto: l'HUD si legge su qualunque sfondo."""
        sh = skia.GradientShader.MakeLinear([(0, 0), (0, 720)], [rgba(SPACE, 0.78), rgba(SPACE, 0.0)])
        c.drawRect(skia.Rect(0, 0, W, 720), skia.Paint(Shader=sh))

    # ---------- HUD ----------

    def _hud(self, c, cam, vt):
        tl, st = self.tl, self.story
        a = ease_in_out((vt - tl.hud_on) / 0.5)
        if a <= 0:
            return
        x0, x1 = MARGIN, W - MARGIN
        small, big = gfx.mono(30), gfx.mono(78, "Medium")
        draw_text(c, _last(tl.place, vt, ""), small, x0, 140, color=INK, alpha=0.88 * a, align="left", tracking=1.5)
        secs = tl.clock_s(vt)
        now = st.start + dt.timedelta(seconds=secs)
        live = tl.is_live(vt)
        draw_text(c, now.strftime("%H:%M:%S" if live else "%H:%M"), big, x0 - 4, 226, color=INK, alpha=a,
                  align="left")
        draw_text(c, now.strftime("%a %d %b %Y").upper(), small, x0, 276, color=INK, alpha=0.88 * a, align="left",
                  tracking=1)
        tag = _last(tl.tag, vt)
        if tag is None:
            days = secs / 86400
            if live or abs(days) < 1:
                s = int(round(secs))
                tag = f"T+{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 0 else ""
            elif days < 400:
                tag = f"DAY {int(days)}"
            else:
                tag = f"YEAR {int(days / 365.25)}"
        draw_text(c, tag, gfx.mono(28), x0, 318, color=AMBER, alpha=a, align="left", tracking=1)
        c.drawLine(x0, 346, x0 + 340, 346, skia.Paint(AntiAlias=True, StrokeWidth=1.5, Color=rgba(INK, 0.3 * a)))

        # KPI principale a destra, con la variazione rispetto alla base.
        label = _last(tl.kpi_label, vt, "")
        draw_text(c, label, small, x1, 140, color=INK, alpha=0.88 * a, align="right", tracking=1.5)
        val = tl.kpi_value(vt)
        s = st.kpi_format(val)
        draw_text(c, s, big, x1, 226, color=INK, alpha=a, align="right")
        base = _last(tl.kpi_base, vt, st.kpi_base)
        pct = (val - base) / base * 100 if base else 0
        if abs(pct) >= 0.5:
            ptxt = f"{abs(pct):.0f}%"
            pf = gfx.mono(30, "Medium")
            vx = x1 - gfx.text_width(s, big) - 22
            draw_text(c, ptxt, pf, vx, 222, color=AMBER, alpha=a, align="right")
            tx = vx - gfx.text_width(ptxt, pf) - 26
            tri = skia.Path()
            if pct > 0:
                tri.addPoly([skia.Point(tx - 9, 214), skia.Point(tx + 9, 214), skia.Point(tx, 198)], True)
            else:
                tri.addPoly([skia.Point(tx - 9, 200), skia.Point(tx + 9, 200), skia.Point(tx, 216)], True)
            c.drawPath(tri, skia.Paint(AntiAlias=True, Color=rgba(AMBER, a)))
        k2 = _last(tl.kpi2, vt)
        if k2:
            t2 = max(tt for tt, v in tl.kpi2 if tt <= vt)
            n = int((vt - t2) * CPS * 1.4)
            lab, v2 = k2
            lab = lab[:n]
            v2 = v2[:max(0, n - len(k2[0]))]
            lw = gfx.text_width(lab, small, 1)
            draw_text(c, lab, small, x1, 276, color=INK, alpha=0.88 * a, align="right", tracking=1)
            if lab:
                ax = x1 - lw - 22
                c.drawLine(ax - 26, 266, ax, 266, skia.Paint(AntiAlias=True, StrokeWidth=2.2, Color=rgba(AMBER, a)))
                arr = skia.Path()
                arr.addPoly([skia.Point(ax + 2, 266), skia.Point(ax - 8, 259), skia.Point(ax - 8, 273)], True)
                c.drawPath(arr, skia.Paint(AntiAlias=True, Color=rgba(AMBER, a)))
            draw_text(c, v2, gfx.mono(38, "SemiBold"), x1, 326, color=AMBER, alpha=a, align="right", tracking=1)

        # Barra di scala (solo in vista dall'alto).
        if cam.pitch < 3 and cam.w > 150:
            m = _nice(cam.px * 190) if st.units == "metric" else None
            if st.units == "imperial":
                feet = cam.px * 190 * 3.281
                m = _nice(feet / 5280) * 1609.344 if feet > 2000 else _nice(feet) / 3.281
            L = m / cam.px
            sa = a * min(1.0, (cam.w - 150) / 200)
            p = skia.Paint(AntiAlias=True, StrokeWidth=1.8, Color=rgba(INK, 0.8 * sa))
            y = 384
            c.drawLine(x0, y, x0 + L, y, p)
            c.drawLine(x0, y - 8, x0, y, p)
            c.drawLine(x0 + L, y - 8, x0 + L, y, p)
            draw_text(c, fmt_dist(m, st.units), gfx.mono(26), x0 + L + 16, y + 2, color=INK, alpha=0.85 * sa,
                      align="left", vcenter=True, tracking=1)

    # ---------- didascalie ----------

    def _captions(self, c, cam, vt):
        for cap in self.tl.captions:
            t0, t1 = cap["t0"], cap["t1"]
            if not (t0 <= vt < t1 + 0.4):
                continue
            out = 1 - ease_in_out((vt - (t1 - 0.3)) / 0.3)
            if cap["layout"] == "left":
                self._caption_left(c, cap, vt - t0, out)
            else:
                self._caption_center(c, cam, cap, vt - t0, out)

    def _caption_left(self, c, cap, age, out):
        x0 = MARGIN
        y = CAPTION_Y - 70
        if cap["jump"]:
            n = int(age * CPS * 1.5)
            draw_text(c, cap["jump"][:n], gfx.mono(34, "Medium"), x0, y, color=AMBER, alpha=out, align="left",
                      tracking=1.5)
        y += 76
        n = int(max(0.0, age - 0.25) * CPS)
        font = gfx.title(58)
        shown = 0
        for line in _wrap(cap["text"], font, W - 2 * MARGIN):
            part = line[:max(0, n - shown)]
            shown += len(line) + 1
            draw_text(c, part, font, x0, y, color=(255, 255, 255), alpha=out, align="left")
            y += 72
        if cap["sub"]:
            ka = ease_in_out((age - 0.35 - len(cap["text"]) / CPS) / 0.4) * out
            for line in _wrap(cap["sub"], gfx.text(38), W - 2 * MARGIN):
                draw_text(c, line, gfx.text(38), x0, y + 6, color=INK, alpha=0.85 * ka, align="left")
                y += 50

    def _caption_center(self, c, cam, cap, age, out):
        hook = cap["layout"] == "hook"
        # La domanda iniziale è piena già al primo frame (è anche la miniatura); le altre entrano in dissolvenza.
        k_in = 1.0 if hook else ease_out(age / 0.45)
        k = k_in * out
        if k <= 0:
            return
        font = gfx.title(76 if hook else 60)
        lines = _wrap(cap["text"], font, W - 2 * MARGIN - (40 if hook else 0))
        lh = 90 if hook else 74
        y = (250 if hook else CAPTION_Y) + (1 - k_in) * 14
        shadow = skia.Paint(AntiAlias=True, Color=rgba((0, 0, 0), 0.6 * k),
                            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9))
        for line in lines:
            w = font.measureText(line)
            c.drawString(line, W / 2 - w / 2, y + 3, font, shadow)
            draw_text(c, line, font, W / 2, y, color=(255, 255, 255), alpha=k)
            y += lh
        if cap["sub"]:
            ks = ease_in_out((age - 0.6) / 0.4) * out
            sf = gfx.text(40)
            for line in _wrap(cap["sub"], sf, W - 2 * MARGIN):
                w = sf.measureText(line)
                c.drawString(line, W / 2 - w / 2, y + 2, sf, shadow)
                draw_text(c, line, sf, W / 2, y - 6, color=INK, alpha=0.9 * ks)
                y += 52
        if cap["point"]:
            sx, sy = cam.to_screen(*self.scene.anchor(cap["point"], cap["t0"] + age, self.tl))
            kp = ease_in_out((age - 0.5) / 0.5) * out
            rr = 3.4 / cam.px  # cerchio un po' più grande di una macchina
            if kp > 0 and 0 < sx < W and y < sy - rr < H:
                p = skia.Paint(AntiAlias=True, StrokeWidth=2, Color=rgba((255, 255, 255), 0.85 * kp))
                top = y - 20
                end = top + (sy - rr - top) * kp
                c.drawLine(W / 2, top, W / 2 + (sx - W / 2) * (end - top) / max(1, sy - rr - top), end, p)
                c.drawCircle(sx, sy, rr, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.5,
                                                    Color=rgba((255, 255, 255), 0.85 * kp)))

    # ---------- effetti ----------

    def _rewind(self, c, vt):
        k = self.tl.fx_k(vt, "rewind")
        if k is None:
            return
        env = math.sin(math.pi * k)
        rng = np.random.default_rng(int(vt * FPS))
        for _ in range(7):
            y = float(rng.uniform(0, H))
            c.drawRect(skia.Rect(0, y, W, y + float(rng.uniform(2, 9))),
                       skia.Paint(Color=rgba((255, 255, 255), 0.10 * env)))
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=rgba((255, 255, 255), 0.05 * env)))
        # ◀◀ in alto al centro
        cx, cy = W / 2, 470
        for dx in (-26, 6):
            tri = skia.Path()
            tri.addPoly([skia.Point(cx + dx + 22, cy - 20), skia.Point(cx + dx + 22, cy + 20),
                         skia.Point(cx + dx - 6, cy)], True)
            c.drawPath(tri, skia.Paint(AntiAlias=True, Color=rgba((255, 255, 255), 0.9 * env)))


def _wrap(text, font, max_w):
    """A capo con righe bilanciate: stesso numero di righe del metodo greedy, ma lunghezze simili."""
    out = []
    for para in text.split("\n"):
        lines = _greedy(para, font, max_w)
        lo, hi = max_w * 0.4, max_w
        while hi - lo > 4:
            mid = (lo + hi) / 2
            if len(_greedy(para, font, mid)) <= len(lines):
                hi = mid
            else:
                lo = mid
        out += _greedy(para, font, hi)
    return out


def _greedy(text, font, max_w):
    out, line = [], ""
    for word in text.split(" "):
        cand = (line + " " + word).strip()
        if font.measureText(cand) <= max_w or not line:
            line = cand
        else:
            out.append(line)
            line = word
    out.append(line)
    return out
