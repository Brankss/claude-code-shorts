"""Dormitorio di notte, visto dal soffitto: un ragazzo a letto che scrolla. Scena per What If (TikTok).

Coordinate in metri (y verso nord), origine al centro della stanza. Il ragazzo è a letto a sinistra,
testa verso l'alto, telefono sul petto con lo schermo verso la camera. Uscendo con lo zoom:
stanza -> piano del dormitorio (15 stanze per lato, tutti a letto col telefono) -> campus -> griglia
delle strade di Chicago (la mappa vera la disegna il renderer).

Modalità (primo elemento di Beat.scene):
- "dorm":  la notte, con il tempo della scena che decide video, cancellazione dell'app e luci spente
- "study": infografica dello studio vero (1.000 studenti) sopra la stanza in penombra
- "moon":  allunaggio (si disegna attorno a MOON_POS)
"""

import math

import numpy as np
import skia

from . import gfx
from . import kinetic as K
from .gfx import mix, rgba

# --- tempi della scena (secondi di "tempo scena", non di video) ---
T_HOME = 12.0      # esce dall'app: schermata home
T_DIALOG = 12.45   # "Delete app?"
T_TAP = 12.95      # tocca Delete
T_GONE = 13.15     # l'icona sparisce
T_OFF = 13.45      # schermo spento
T_DOWN = 14.1      # appoggia il telefono
T_SLEEP = 15.4     # chiude gli occhi
T_ALL = 17.0       # tutti gli altri telefoni si spengono insieme
K3 = 0.25          # finta altezza degli oggetti (metri di spostamento per metro di altezza)

PHONE = (-1.10, -0.36)
PH_W, PH_H = 0.074, 0.156
BED = (-1.62, -1.95, -0.58, 0.25)
HERO = (242, 184, 75)
BLUE = (88, 170, 255)
WARM = (255, 196, 120)
ASTRO = (-2.4, -3.2)   # l'astronauta che filma, rispetto al modulo lunare

VIDEOS = ["dance", "cat", "balls", "meme", "food", "game", "sunset", "balls", "cat", "dance", "meme", "game"]
DURS = [1.15, 0.85, 1.35, 0.95, 1.1, 0.8, 1.25, 0.9, 1.05, 0.75, 1.2, 0.95]
SWIPE = 0.2
VIDEO_TINT = {"dance": (200, 90, 255), "cat": (60, 210, 200), "balls": (90, 150, 255), "meme": (190, 200, 230),
              "food": (255, 170, 70), "game": (90, 230, 120), "sunset": (255, 120, 90)}
CAPTIONS = {"dance": "new trend?? 😭", "cat": "he understood the assignment", "balls": "wait for it...",
            "meme": "", "food": "3am snack hits different", "game": "level 99 parkour", "sunset": "pov: summer"}


def video_at(s):
    """(indice del video, tempo dentro il video, avanzamento dello swipe 0..1 o None) al tempo scena s."""
    period = sum(DURS)
    s = s % period
    t = 0.0
    for i, d in enumerate(DURS):
        if s < t + d:
            local = s - t
            sw = (local - (d - SWIPE)) / SWIPE if local > d - SWIPE else None
            return i, local, sw
        t += d
    return 0, 0.0, None


def _paint(col, a=1.0, **kw):
    return skia.Paint(AntiAlias=True, Color=rgba(col, a), **kw)


def _rr(c, x0, y0, x1, y1, r, col, a=1.0):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r), _paint(col, a))


def _glow(c, x, y, r, col, a, blend=skia.BlendMode.kPlus):
    sh = skia.GradientShader.MakeRadial((x, y), r, [rgba(col, a), rgba(col, a * 0.35), rgba(col, 0)], [0, 0.35, 1])
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=sh, BlendMode=blend))


FONTS = {"text": lambda: gfx.text(48), "bold": lambda: K.bold(48), "heavy": lambda: K.heavy(48),
         "mono": lambda: gfx.mono(48, "SemiBold"), "glyph": lambda: gfx.glyph(48)}


def _text(c, s, x, y, size, col, a=1.0, align="left", kind="text"):
    """Testo in coordinate mondo (y verso nord), alto size metri: il font resta a 48 px e si scala il canvas."""
    if not s or a <= 0:
        return
    f = FONTS[kind]()
    k = size / 48.0
    w = f.measureText(s) * k
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    c.save()
    c.translate(x, y)
    c.scale(k, -k)
    c.drawString(s, 0, 0, f, _paint(col, a))
    c.restore()


class DormScene:
    near_log10 = 1.0   # sotto ~10 m di inquadratura si sente la stanza
    point_r = {"phone": 0.13, "hero": 0.3}

    def __init__(self, seed=3):
        rng = np.random.default_rng(seed)
        # Le altre stanze del piano: centro x, fila (0 = la nostra, 1 = di fronte), grigio della felpa, fase.
        self.rooms = []
        for k in range(-7, 8):
            for row in (0, 1):
                if k == 0 and row == 0:
                    continue
                self.rooms.append((3.4 * k, row, float(rng.uniform(0.25, 0.7)), float(rng.uniform(0, 6.28)),
                                   bool(rng.random() < 0.88)))
        # Campus: edifici attorno (x0, y0, x1, y1, luci) in metri; il nostro è al centro.
        self.campus = []
        for i in range(170):
            cx, cy = rng.uniform(-1000, 1000, 2)
            if abs(cx) < 70 and abs(cy) < 45:
                continue
            w, h = rng.uniform(25, 80), rng.uniform(15, 40)
            if rng.random() < 0.5:
                w, h = h, w
            self.campus.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, rng.random()))
        self.trees = [(float(x), float(y), float(r)) for x, y, r in
                      zip(rng.uniform(-900, 900, 900), rng.uniform(-900, 900, 900), rng.uniform(3, 7, 900))]
        self.near_trees = [(float(x + rng.uniform(-1.2, 1.2)), float(y + rng.uniform(-0.8, 0.8)), float(rng.uniform(1.4, 2.4)))
                           for x in np.arange(-33, 34, 5.5) for y in (-7.5, 13.5)]
        self.atlas = None
        self.stars = None

    def bind(self, renderer):
        self.atlas = renderer.atlas

    # ---------- ancore per la camera ----------

    def anchor(self, name, vt, tl):
        from .whatif import MOON_POS
        if name == "phone":
            return PHONE[0], PHONE[1] - 0.75 * K3

        if name == "hero":
            return -1.10, -0.15
        if name == "room":
            return 0.0, 0.0
        if name == "building":
            return 0.0, 3.05
        if name == "lander":
            return MOON_POS[0], MOON_POS[1]
        if name == "astronaut":
            return MOON_POS[0] + ASTRO[0], MOON_POS[1] + ASTRO[1]
        return 0.0, 0.0

    # ---------- disegno ----------

    def draw(self, c, cam, vt, tl, alpha, ground=1.0):
        from .whatif import MOON_POS
        mode, s, where = tl.scene_state(vt)
        if where == "moon" or mode == "moon":
            if cam.near(*MOON_POS, 5000):
                c.save()
                c.concat(cam.matrix(*MOON_POS))
                self._moon(c, s, cam.px)
                c.restore()
            return
        if not cam.near(0, 0, 30000):
            return
        k3 = K3
        px = cam.px
        if ground > 0:
            c.drawRect(skia.Rect(0, 0, 1080, 1920), _paint((10, 12, 18), alpha * ground))
        c.save()
        c.concat(cam.matrix())
        state = "dorm" if mode != "study" else "study"
        s_eff = s if state == "dorm" else 5.0
        if cam.w > 120:
            self._city(c, cam, s_eff, alpha)
        if cam.w > 14:
            self._campus(c, cam, s_eff, alpha)
        if cam.w < 400:
            self._floor(c, cam, s_eff, alpha, k3)
        if cam.w < 14:
            self._room(c, s_eff, alpha, k3, px)
        c.restore()
        if state == "study":
            self._study(c, s, alpha)

    # --- stanza ---

    def _room(self, c, s, a, k3, px):
        phone_on = s < T_OFF
        tint = self._tint(s)
        # pavimento e assi
        c.drawRect(skia.Rect(-1.7, -2.1, 1.7, 2.1), _paint((33, 29, 37), a))
        line = _paint((40, 35, 45), a, StrokeWidth=max(0.006, px), Style=skia.Paint.kStroke_Style)
        for i in range(-12, 13):
            c.drawLine(i * 0.14, -2.1, i * 0.14, 2.1, line)
        # luce della luna dalla finestra in alto
        moon = skia.Path()
        moon.addPoly([skia.Point(-0.55, 2.05), skia.Point(0.85, 2.05), skia.Point(1.15, 0.55), skia.Point(-0.2, 0.55)],
                     True)
        c.drawPath(moon, _paint((120, 150, 210), 0.09 * a))
        # tappeto
        c.drawOval(skia.Rect(-0.35, -1.0, 1.15, 0.35), _paint((58, 40, 62), a))
        c.drawOval(skia.Rect(-0.2, -0.88, 1.0, 0.22), _paint((66, 46, 70), a, Style=skia.Paint.kStroke_Style,
                                                             StrokeWidth=0.03))
        # scrivania con portatile, libri, lampada spenta, tazza
        self._box(c, 0.95, -0.45, 1.62, 1.35, 0.75, (74, 54, 42), (52, 38, 30), a, k3)
        d = 0.75 * k3
        _rr(c, 1.08, 0.55 - d, 1.48, 0.86 - d, 0.02, (58, 62, 70), a)
        _rr(c, 1.0, -0.3 - d, 1.25, -0.02 - d, 0.01, (120, 60, 60), a)
        _rr(c, 1.03, -0.27 - d, 1.27, 0.0 - d, 0.01, (60, 90, 130), a)
        c.drawCircle(1.48, 1.15 - d, 0.09, _paint((90, 90, 96), a))
        c.drawCircle(1.42, 0.25 - d, 0.045, _paint((200, 200, 205), a))
        c.drawCircle(1.42, 0.25 - d, 0.032, _paint((60, 40, 30), a))
        # sedia
        self._box(c, 0.55, 0.15, 0.9, 0.55, 0.45, (40, 40, 46), (28, 28, 32), a, k3)
        # comodino con sveglia (2:47 in rosso) e lattina
        self._box(c, -0.52, -0.08, -0.14, 0.3, 0.55, (70, 52, 40), (48, 36, 28), a, k3)
        d = 0.55 * k3
        _rr(c, -0.46, 0.08 - d, -0.24, 0.2 - d, 0.015, (20, 20, 22), a)
        _glow(c, -0.35, 0.14 - d, 0.18, (255, 40, 40), 0.18 * a)
        _text(c, "2:47", -0.35, 0.115 - d, 0.07, (255, 70, 60), a, "center", kind="mono")
        c.drawCircle(-0.21, -0.0 - d, 0.033, _paint((150, 210, 90), a))
        c.drawCircle(-0.21, -0.0 - d, 0.022, _paint((200, 200, 205), a))
        # vestiti per terra e scarpe
        for (x, y, rx, ry, col) in ((0.15, -1.55, 0.28, 0.16, (70, 75, 95)), (0.45, -1.7, 0.22, 0.12, (110, 40, 40)),
                                    (-0.25, -1.75, 0.12, 0.06, (230, 230, 230)), (-0.05, -1.8, 0.12, 0.06, (230, 230, 230))):
            c.drawOval(skia.Rect(x - rx, y - ry, x + rx, y + ry), _paint(col, 0.8 * a))
        # pianta e minifrigo vicino alla finestra
        self._box(c, 1.05, 1.55, 1.55, 2.0, 0.85, (190, 192, 198), (140, 142, 150), a, k3)
        c.drawCircle(-1.35, 1.75, 0.16, _paint((60, 50, 40), a))
        for j in range(7):
            ang = j * 0.9
            c.drawOval(skia.Rect(-1.35 + 0.12 * math.cos(ang) - 0.07, 1.75 + 0.12 * math.sin(ang) - 0.035,
                                 -1.35 + 0.12 * math.cos(ang) + 0.07, 1.75 + 0.12 * math.sin(ang) + 0.035),
                       _paint((50, 110, 70), a))
        # letto
        self._bed(c, s, a, k3, px, tint, phone_on)
        # muri (pianta in sezione) e finestra
        wall = _paint((14, 14, 18), a)
        for r in ((-1.85, -2.25, 1.85, -2.1), (-1.85, 2.1, 1.85, 2.25), (-1.85, -2.25, -1.7, 2.25), (1.7, -2.25, 1.85, 2.25)):
            c.drawRect(skia.Rect(*r), wall)
        c.drawRect(skia.Rect(-0.6, 2.1, 0.9, 2.25), _paint((150, 180, 230), 0.55 * a))
        c.drawRect(skia.Rect(0.6, -2.25, 1.5, -2.1), _paint((60, 48, 40), a))  # porta
        # luce del telefono: si spegne quando cancella l'app
        light = self._light(s)
        if light > 0:
            bx, by = PHONE[0], PHONE[1] + 0.75 * k3
            _glow(c, bx, by, 2.2, tint, 0.20 * light * a)
            _glow(c, bx, by + 0.25, 0.55, tint, 0.35 * light * a)
        # buio dopo che si è addormentato: una velatura blu notte
        if s > T_OFF:
            dark = min(1.0, (s - T_OFF) / 1.2)
            c.drawRect(skia.Rect(-1.9, -2.3, 1.9, 2.3), _paint((5, 8, 20), 0.35 * dark * a))
        if s > T_SLEEP:
            kz = (s - T_SLEEP) % 1.6 / 1.6
            for j, dz in enumerate((0.0, 0.33)):
                kk = (kz + dz) % 1.0
                _text(c, "z", -0.9 + kk * 0.25, 0.35 + kk * 0.35 + 0.55 * k3, 0.08 + 0.05 * kk, (220, 225, 255),
                      a * math.sin(math.pi * kk) * 0.9, kind="bold")

    def _box(self, c, x0, y0, x1, y1, h, top, side, a, k3):
        """Mobile con finto volume: faccia laterale verso la camera e piano spostato in su."""
        d = h * k3
        if d > 0.001:
            c.drawRect(skia.Rect(x0, y0 - d, x1, y0), _paint(side, a))
        c.drawRect(skia.Rect(x0, y0 - d, x1, y1 - d), _paint(top, a))

    def _light(self, s):
        if s < T_OFF:
            return 1.0
        return max(0.0, 1 - (s - T_OFF) / 0.35)

    def _tint(self, s):
        if s >= T_HOME:
            return (120, 150, 255)
        i, local, sw = video_at(s)
        col = VIDEO_TINT[VIDEOS[i]]
        if sw is not None:
            col = mix(col, VIDEO_TINT[VIDEOS[(i + 1) % len(VIDEOS)]], sw)
        return mix(col, (150, 190, 255), 0.35)

    def _bed(self, c, s, a, k3, px, tint, phone_on):
        x0, y0, x1, y1 = BED
        h = 0.5
        d = h * k3
        self._box(c, x0, y0, x1, y1, h, (64, 46, 36), (44, 32, 26), a, k3)
        c.drawRect(skia.Rect(x0 + 0.04, y0 + 0.04 - d, x1 - 0.04, y1 - 0.04 - d), _paint((176, 178, 188), a))
        c.drawRect(skia.Rect(x0, y1 - d, x1, y1 + 0.07 - d), _paint((52, 38, 30), a))  # testiera
        _rr(c, -1.47, -0.1 - d, -0.73, 0.2 - d, 0.07, (205, 207, 215), a)               # cuscino
        dh = d + 0.06 * k3
        sleep = gfx.ease_in_out((s - T_SLEEP) / 0.8) if s > T_SLEEP else 0.0
        hood = mix(HERO, (0, 0, 0), 0.22)
        hx, hy = -1.10, 0.0 - dh
        # cappuccio sotto la testa, poi il busto con un po' di volume
        c.drawOval(skia.Rect(hx - 0.15, hy - 0.08, hx + 0.15, hy + 0.15), _paint(hood, a))
        torso = skia.RRect.MakeRectXY(skia.Rect(-1.34, -0.8 - dh, -0.86, -0.08 - dh), 0.13, 0.13)
        sh = skia.GradientShader.MakeLinear([(-1.34, 0), (-0.86, 0)], [rgba(mix(HERO, (0, 0, 0), 0.3), a),
                                                                       rgba(mix(HERO, (255, 255, 255), 0.08), a),
                                                                       rgba(mix(HERO, (0, 0, 0), 0.3), a)])
        c.drawRRect(torso, skia.Paint(AntiAlias=True, Shader=sh))
        for side in (-1, 1):
            c.drawLine(hx + side * 0.03, -0.11 - dh, hx + side * 0.035, -0.26 - dh,
                       _paint((235, 235, 235), 0.8 * a, StrokeWidth=0.008, StrokeCap=skia.Paint.kRound_Cap))
        # testa: capelli dietro, viso, frangia, orecchie
        skin = (206, 160, 128)
        c.drawOval(skia.Rect(hx - 0.088, hy - 0.035, hx + 0.088, hy + 0.118), _paint((46, 33, 26), a))
        for side in (-1, 1):
            c.drawOval(skia.Rect(hx + side * 0.079 - 0.018, hy - 0.035, hx + side * 0.079 + 0.018, hy + 0.012),
                       _paint(mix(skin, (0, 0, 0), 0.12), a))
        c.drawOval(skia.Rect(hx - 0.074, hy - 0.1, hx + 0.074, hy + 0.062), _paint(skin, a))
        fringe = skia.Path()
        fringe.moveTo(hx - 0.08, hy + 0.035)
        fringe.cubicTo(hx - 0.04, hy + 0.075, hx + 0.02, hy + 0.02, hx + 0.08, hy + 0.04)
        fringe.lineTo(hx + 0.085, hy + 0.1)
        fringe.lineTo(hx - 0.085, hy + 0.1)
        fringe.close()
        c.drawPath(fringe, _paint((46, 33, 26), a))
        # luce dello schermo sul viso
        if phone_on:
            _glow(c, hx, hy - 0.05, 0.16, tint, 0.28 * a)
        ink = (40, 28, 26)
        line = _paint(ink, a, StrokeWidth=0.006, StrokeCap=skia.Paint.kRound_Cap, Style=skia.Paint.kStroke_Style)
        for ex in (-0.03, 0.03):
            c.drawLine(hx + ex - 0.016, hy + 0.012, hx + ex + 0.012, hy + 0.016, line)   # sopracciglia
            if sleep < 0.5:
                c.drawOval(skia.Rect(hx + ex - 0.011, hy - 0.022, hx + ex + 0.011, hy - 0.006), _paint(ink, a))
                c.drawCircle(hx + ex + 0.004, hy - 0.012, 0.0035, _paint(mix(tint, (255, 255, 255), 0.5), a))
            else:
                p = skia.Path()
                p.moveTo(hx + ex - 0.012, hy - 0.012)
                p.quadTo(hx + ex, hy - 0.02, hx + ex + 0.012, hy - 0.012)
                c.drawPath(p, line)
        c.drawLine(hx, hy - 0.03, hx - 0.006, hy - 0.05, _paint(mix(skin, (0, 0, 0), 0.25), a, StrokeWidth=0.006,
                                                                StrokeCap=skia.Paint.kRound_Cap))
        c.drawLine(hx - 0.016, hy - 0.072, hx + 0.016, hy - 0.072, line)
        # coperta (sopra le gambe), con pieghe
        bl = skia.Path()
        bl.moveTo(x0 + 0.02, -0.62 - d)
        bl.cubicTo(-1.3, -0.55 - d, -0.9, -0.7 - d, x1 - 0.02, -0.6 - d)
        bl.lineTo(x1 - 0.02, y0 + 0.02 - d)
        bl.lineTo(x0 + 0.02, y0 + 0.02 - d)
        bl.close()
        c.drawPath(bl, _paint((44, 66, 104), a))
        fold = _paint((34, 52, 84), a, StrokeWidth=0.02, Style=skia.Paint.kStroke_Style)
        for fy in (-0.95, -1.25, -1.6):
            p = skia.Path()
            p.moveTo(x0 + 0.1, fy - d)
            p.cubicTo(-1.3, fy + 0.08 - d, -0.95, fy - 0.08 - d, x1 - 0.1, fy + 0.03 - d)
            c.drawPath(p, fold)
        # telefono e mani
        self._phone(c, s, a, k3, px)

    def _phone(self, c, s, a, k3, px):
        down = gfx.ease_in_out((s - T_DOWN) / 0.7) if s > T_DOWN else 0.0
        hgt = 0.75 * k3 * (1 - 0.4 * down)
        cx, cy = PHONE[0], PHONE[1] - hgt + 0.0
        cy -= 0.18 * down
        skin = (206, 160, 128)
        # braccia (felpa) che salgono verso il telefono
        arm = _paint(mix(HERO, (0, 0, 0), 0.25), a, StrokeWidth=0.075, StrokeCap=skia.Paint.kRound_Cap,
                     Style=skia.Paint.kStroke_Style)
        for side in (-1, 1):
            p = skia.Path()
            p.moveTo(-1.10 + side * 0.22, -0.2 - 0.06 * k3)
            p.quadTo(-1.10 + side * 0.26, -0.55 - 0.3 * k3, cx + side * 0.05, cy - 0.04)
            c.drawPath(p, arm)
        self._night(c, s, a, k3, px)
        c.save()
        c.translate(cx, cy)
        hw, hh = PH_W / 2, PH_H / 2
        if down > 0.5:
            # appoggiato a faccia in giù: si vede il retro
            _rr(c, -hw, -hh, hw, hh, 0.011, (30, 30, 34), a)
            _rr(c, -hw + 0.008, hh - 0.04, -hw + 0.035, hh - 0.008, 0.008, (50, 50, 56), a)
        else:
            _rr(c, -hw - 0.003, -hh - 0.003, hw + 0.003, hh + 0.003, 0.013, (18, 18, 20), a)
            sr = skia.RRect.MakeRectXY(skia.Rect(-hw + 0.003, -hh + 0.003, hw - 0.003, hh - 0.003), 0.010, 0.010)
            c.save()
            c.clipRRect(sr, True)
            self._screen(c, s, a, hw - 0.003, hh - 0.003)
            c.restore()
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-0.012, hh - 0.012, 0.012, hh - 0.006), 0.003, 0.003),
                        _paint((0, 0, 0), a))
        c.restore()
        # mani: palmo ai lati, quattro dita che avvolgono il bordo, pollice che spinge su quando scorre
        i, local, sw = video_at(s)
        thumb = 0.0 if sw is None or s >= T_HOME else math.sin(math.pi * sw) * 0.045
        shade = mix(skin, (0, 0, 0), 0.18)
        if down < 0.5:
            for side in (-1, 1):
                ex = cx + side * (PH_W / 2)
                c.drawOval(skia.Rect(ex + side * 0.012 - 0.022, cy - 0.075, ex + side * 0.012 + 0.022, cy - 0.005),
                           _paint(shade, a))
                for j in range(4 if side > 0 else 1):
                    fy = cy - 0.06 + j * 0.019
                    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(ex - side * 0.004 - 0.009, fy, ex - side * 0.004 + 0.009,
                                                                fy + 0.014), 0.007, 0.007), _paint(skin, a))
            tx, ty = cx - 0.012, cy - 0.052 + thumb
            # il pollice va su "Delete" e torna giù
            reach = gfx.ease_in_out((s - (T_TAP - 0.35)) / 0.3) * (1 - gfx.ease_in_out((s - T_GONE) / 0.3))
            tx += (cx - 0.003 - tx) * reach
            ty += (cy - 0.0275 - ty) * reach
            c.save()
            c.translate(tx, ty)
            c.rotate(-25)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-0.0095, -0.03, 0.0095, 0.012), 0.009, 0.009),
                        _paint(mix(skin, (255, 255, 255), 0.06), a))
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-0.006, 0.0, 0.006, 0.01), 0.004, 0.004),
                        _paint(mix(skin, (255, 255, 255), 0.35), 0.8 * a))
            c.restore()
        else:
            for side in (-1, 1):
                c.drawOval(skia.Rect(cx + side * 0.03 - 0.022, cy - 0.03, cx + side * 0.03 + 0.022, cy + 0.03),
                           _paint(skin, a))

    def _night(self, c, s, a, k3, px):
        """Primo piano: fuori dalla luce dello schermo è notte, e la felpa prende il colore del video."""
        close = min(1.0, max(0.0, (1.3 - px * 1080) / 0.9))
        if close <= 0:
            return
        pcx, pcy = PHONE[0], PHONE[1] - 0.75 * k3
        dark = (5, 7, 15)
        sh = skia.GradientShader.MakeRadial((pcx, pcy), 0.3, [rgba(dark, 0), rgba(dark, 0), rgba(dark, 0.5 * close * a),
                                                              rgba(dark, 0.84 * close * a)], [0, 0.2, 0.5, 1])
        c.drawRect(skia.Rect(pcx - 2, pcy - 2, pcx + 2, pcy + 2), skia.Paint(AntiAlias=True, Shader=sh))
        on = self._light(s)
        if on > 0:
            _glow(c, pcx, pcy, 0.2, self._tint(s), 0.3 * on * close * a)

    # --- schermo del telefono ---

    def _screen(self, c, s, a, hw, hh):
        """Schermo in coordinate locali del telefono (metri, y verso nord)."""
        light = self._light(s)
        if s >= T_OFF:
            c.drawRect(skia.Rect(-hw, -hh, hw, hh), _paint((4, 4, 6), a))
            if light > 0:
                c.drawRect(skia.Rect(-hw, -hh, hw, hh), _paint((255, 255, 255), 0.12 * light * a))
            return
        if s >= T_HOME:
            self._home(c, s, a, hw, hh)
            return
        i, local, sw = video_at(s)
        off = (sw if sw is not None else 0.0)
        off = gfx.ease_in_out(off) * 2 * hh
        for j, dy in ((i, off), ((i + 1) % len(VIDEOS), off - 2 * hh)):
            if -2 * hh < dy < 2 * hh:
                c.save()
                c.translate(0, dy)
                self._video(c, VIDEOS[j], local if j == i else 0.0, a, hw, hh, j)
                c.restore()
        self._ui(c, VIDEOS[i], a, hw, hh, i, off)

    def _video(self, c, kind, t, a, hw, hh, idx):
        if kind == "dance":
            sh = skia.GradientShader.MakeLinear([(0, hh), (0, -hh)], [rgba((255, 90, 160), a), rgba((110, 60, 255), a)])
            c.drawRect(skia.Rect(-hw, -hh, hw, hh), skia.Paint(Shader=sh))
            b = abs(math.sin(t * 7.0)) * 0.012
            c.drawOval(skia.Rect(-0.02, -hh + 0.012, 0.02, -hh + 0.02), _paint((40, 0, 60), 0.4 * a))
            c.drawLine(0, -hh + 0.02 + b, 0, -hh + 0.07 + b, _paint((255, 255, 255), a, StrokeWidth=0.012,
                                                                    StrokeCap=skia.Paint.kRound_Cap))
            for side in (-1, 1):
                ang = math.sin(t * 7 + side) * 0.9
                c.drawLine(0, -hh + 0.06 + b, side * 0.025 * math.cos(ang), -hh + 0.06 + b + 0.025 * math.sin(ang),
                           _paint((255, 255, 255), a, StrokeWidth=0.007, StrokeCap=skia.Paint.kRound_Cap))
            c.drawCircle(0, -hh + 0.085 + b, 0.011, _paint((255, 255, 255), a))
        elif kind == "cat":
            sh = skia.GradientShader.MakeLinear([(0, hh), (0, -hh)], [rgba((40, 200, 190), a), rgba((20, 110, 140), a)])
            c.drawRect(skia.Rect(-hw, -hh, hw, hh), skia.Paint(Shader=sh))
            c.save()
            c.rotate(math.sin(t * 5) * 12)
            c.drawCircle(0, 0, 0.022, _paint((245, 150, 60), a))
            for side in (-1, 1):
                ear = skia.Path()
                ear.addPoly([skia.Point(side * 0.008, 0.017), skia.Point(side * 0.022, 0.035),
                             skia.Point(side * 0.022, 0.012)], True)
                c.drawPath(ear, _paint((245, 150, 60), a))
                c.drawCircle(side * 0.008, 0.003, 0.004, _paint((20, 30, 20), a))
            c.restore()
        elif kind == "balls":
            c.drawRect(skia.Rect(-hw, -hh, hw, hh), _paint((16, 16, 26), a))
            r = 0.026
            gap = t * 2.4
            ring = skia.Path()
            ring.addArc(skia.Rect(-r, -r, r, r), math.degrees(gap) + 25, 310)
            c.drawPath(ring, _paint((255, 255, 255), a, Style=skia.Paint.kStroke_Style, StrokeWidth=0.0025))
            bx, by = math.cos(t * 9.1) * 0.015, math.sin(t * 6.3) * 0.015
            for k in range(6):
                c.drawCircle(bx * (1 - k * 0.12), by * (1 - k * 0.12), 0.004,
                             _paint(mix((255, 80, 160), (80, 200, 255), k / 5), a * (1 - k * 0.15)))
        elif kind == "meme":
            c.drawRect(skia.Rect(-hw, -hh, hw, hh), _paint((10, 10, 12), a))
            for j, line in enumerate(("POV: IT'S 3AM", "AND YOU SAID", "\"ONE MORE\"")):
                _text(c, line, 0, 0.03 - j * 0.014, 0.0095, (255, 255, 255), a, "center", kind="heavy")
        elif kind == "food":
            sh = skia.GradientShader.MakeRadial((0, 0), hh, [rgba((255, 190, 90), a), rgba((200, 90, 30), a)])
            c.drawRect(skia.Rect(-hw, -hh, hw, hh), skia.Paint(Shader=sh))
            sc = 1 + 0.15 * math.sin(t * 3)
            c.save()
            c.scale(sc, sc)
            tri = skia.Path()
            tri.addPoly([skia.Point(-0.022, 0.02), skia.Point(0.022, 0.02), skia.Point(0, -0.03)], True)
            c.drawPath(tri, _paint((255, 214, 90), a))
            c.drawRect(skia.Rect(-0.024, 0.02, 0.024, 0.027), _paint((200, 120, 50), a))
            for px_, py_ in ((-0.008, 0.008), (0.009, 0.01), (0.0, -0.008)):
                c.drawCircle(px_, py_, 0.004, _paint((200, 50, 40), a))
            c.restore()
        elif kind == "game":
            c.drawRect(skia.Rect(-hw, -hh, hw, hh), _paint((110, 180, 255), a))
            for k in range(8):
                x = ((k * 0.02 - t * 0.04) % 0.16) - 0.08
                c.drawRect(skia.Rect(x, -hh, x + 0.012, -hh + 0.02 + 0.01 * (k % 3)), _paint((80, 200, 90), a))
            jump = abs(math.sin(t * 6)) * 0.02
            c.drawRect(skia.Rect(-0.005, -hh + 0.03 + jump, 0.005, -hh + 0.042 + jump), _paint((255, 230, 80), a))
        else:  # sunset
            sh = skia.GradientShader.MakeLinear([(0, hh), (0, -hh)], [rgba((255, 140, 80), a), rgba((80, 40, 120), a)])
            c.drawRect(skia.Rect(-hw, -hh, hw, hh), skia.Paint(Shader=sh))
            c.drawCircle(0, -0.005 + t * 0.004, 0.018, _paint((255, 230, 150), a))
            c.drawRect(skia.Rect(-hw, -hh, hw, -0.02), _paint((40, 20, 60), a))

    def _ui(self, c, kind, a, hw, hh, i, off):
        """Interfaccia da app di video verticali (generica): icone a destra, nome e didascalia in basso."""
        w = (255, 255, 255)
        _text(c, "Following   For You", 0, hh - 0.012, 0.0055, w, 0.9 * a, "center", kind="bold")
        c.drawRect(skia.Rect(0.004, hh - 0.0155, 0.017, hh - 0.0145), _paint(w, a))
        x = hw - 0.009
        y = 0.01
        c.drawCircle(x, y + 0.02, 0.0065, _paint((220, 220, 225), a))
        c.drawCircle(x, y + 0.0125, 0.0022, _paint((255, 60, 90), a))
        icons = [("♥", "1.2M" if i % 2 else "842K"), ("●", "8,412"), ("▲", "21K")]
        for j, (ic, cnt) in enumerate(icons):
            yy = y - j * 0.019
            if j == 0:
                heart = skia.Path()
                heart.moveTo(x, yy - 0.0045)
                heart.cubicTo(x - 0.009, yy + 0.001, x - 0.004, yy + 0.008, x, yy + 0.003)
                heart.cubicTo(x + 0.004, yy + 0.008, x + 0.009, yy + 0.001, x, yy - 0.0045)
                c.drawPath(heart, _paint((255, 255, 255), 0.95 * a))
            else:
                c.drawCircle(x, yy, 0.0045, _paint((255, 255, 255), 0.95 * a))
            _text(c, cnt, x, yy - 0.0095, 0.0032, w, 0.9 * a, "center", kind="bold")
        _text(c, "@" + ("dailyloops", "catdaddy", "simulations", "memesx", "latecravings", "speedrun", "summerpov",
                        "simulations", "catdaddy", "dailyloops", "memesx", "speedrun")[i], -hw + 0.005, -hh + 0.028,
              0.0045, w, a, kind="bold")
        _text(c, CAPTIONS[kind].replace("😭", ""), -hw + 0.005, -hh + 0.019, 0.0038, w, 0.85 * a)
        c.drawRect(skia.Rect(-hw, -hh + 0.004, hw, -hh + 0.0052), _paint(w, 0.25 * a))

    def _home(self, c, s, a, hw, hh):
        """Schermata home: le icone tremano, appare 'Delete app?', tocca Delete, l'icona sparisce."""
        sh = skia.GradientShader.MakeLinear([(0, hh), (0, -hh)], [rgba((40, 60, 120), a), rgba((90, 40, 110), a)])
        c.drawRect(skia.Rect(-hw, -hh, hw, hh), skia.Paint(Shader=sh))
        cols = [(90, 200, 120), (255, 200, 60), (80, 160, 255), (255, 110, 90), (170, 120, 255), (60, 210, 220),
                (255, 150, 200), (230, 230, 235)]
        size = 0.0115
        gx = [-0.024, -0.008, 0.008, 0.024]
        target = (1, 2)
        for r in range(5):
            for col in range(4):
                x, y = gx[col], hh - 0.03 - r * 0.021
                wig = math.sin(s * 30 + r * 2 + col) * 4 if s > T_HOME + 0.2 else 0.0
                c.save()
                c.translate(x, y)
                c.rotate(wig)
                if (r, col) == target:
                    k = 1 - gfx.ease_in_out((s - T_TAP) / (T_GONE - T_TAP)) if s > T_TAP else 1.0
                    if k > 0:
                        c.scale(k, k)
                        _rr(c, -size / 2, -size / 2, size / 2, size / 2, 0.0028, (12, 12, 14), a)
                        for dx, dy, nc in ((-0.0006, 0.0005, (37, 244, 238)), (0.0006, -0.0005, (254, 44, 85)),
                                           (0, 0, (255, 255, 255))):
                            _text(c, "♪", dx, -0.003 + dy, 0.008, nc, a, "center", kind="glyph")
                    elif s < T_GONE + 0.4:
                        # l'icona esplode: schegge nei due colori della nota e un anello
                        kk = gfx.ease_out((s - T_GONE) / 0.4)
                        for j in range(14):
                            ang = j * math.pi / 7 + 0.3
                            d = (0.016 + 0.008 * (j % 3)) * kk
                            c.drawCircle(math.cos(ang) * d, math.sin(ang) * d, 0.0024 * (1 - kk),
                                         _paint(((37, 244, 238), (254, 44, 85), (255, 255, 255))[j % 3], a))
                        c.drawCircle(0, 0, 0.004 + 0.016 * kk, _paint((255, 255, 255), (1 - kk) * 0.8 * a,
                                                                      Style=skia.Paint.kStroke_Style, StrokeWidth=0.0012))
                else:
                    _rr(c, -size / 2, -size / 2, size / 2, size / 2, 0.0028, cols[(r * 4 + col) % len(cols)], a)
                c.restore()
        if T_DIALOG < s < T_GONE:
            k = min(1.0, (s - T_DIALOG) / 0.12)
            c.drawRect(skia.Rect(-hw, -hh, hw, hh), _paint((0, 0, 0), 0.5 * k * a))
            c.save()
            sc = 0.8 + 0.2 * K.back_out((s - T_DIALOG) / 0.2)
            c.scale(sc, sc)
            _rr(c, -0.03, -0.024, 0.03, 0.021, 0.006, (246, 246, 248), 0.98 * k * a)
            _text(c, "Delete app?", 0, 0.0085, 0.0068, (14, 14, 18), k * a, "center", kind="heavy")
            _text(c, "This can't be undone.", 0, 0.0005, 0.0034, (110, 110, 118), k * a, "center", kind="bold")
            c.drawLine(-0.03, -0.0065, 0.03, -0.0065, _paint((205, 205, 210), k * a, StrokeWidth=0.0007))
            _text(c, "Delete", 0, -0.018, 0.0066, (240, 40, 50), k * a, "center", kind="heavy")
            if s > T_TAP - 0.15:
                kt = (s - (T_TAP - 0.15)) / 0.3
                c.drawCircle(0, -0.0155, 0.005 + 0.006 * kt, _paint((255, 60, 60), max(0, 0.45 * (1 - kt)) * a))
            c.restore()

    # --- piano del dormitorio ---

    def _floor(self, c, cam, s, a, k3):
        """Tutte le stanze del piano: letti, persone in grigio e il bagliore blu dei telefoni."""
        detail = cam.w < 60
        lvl = a * (1 - gfx.ease_in_out((math.log10(cam.w) - math.log10(150)) / 0.35))
        if lvl <= 0:
            return
        c.drawRect(skia.Rect(-31, -2.25, 31, 8.35), _paint((22, 22, 28), lvl))
        c.drawRect(skia.Rect(-27.2, 2.1, 27.2, 4.0), _paint((40, 40, 46), lvl))      # corridoio
        for i in range(-8, 9):
            for yy in ((-2.1, 2.1), (4.0, 8.2)):
                c.drawRect(skia.Rect(3.4 * i - 1.7 - 0.06, yy[0], 3.4 * i - 1.7 + 0.06, yy[1]), _paint((12, 12, 16), lvl))
        others_on = s < T_ALL
        for x, row, grey, ph, uses in self.rooms:
            flip = 1 if row == 0 else -1
            oy = 0.0 if row == 0 else 6.1
            if abs(x) < 0.1 and row == 0:
                continue
            c.drawRect(skia.Rect(x - 1.64, oy - 2.04, x + 1.64, oy + 2.04), _paint((30, 27, 34), lvl))
            bx0, bx1 = x - 1.62, x - 0.58
            by0, by1 = (oy - 1.95, oy + 0.25) if flip > 0 else (oy - 0.25, oy + 1.95)
            c.drawRect(skia.Rect(bx0, by0, bx1, by1), _paint((150, 152, 160), lvl))
            c.drawRect(skia.Rect(bx0, (by0 if flip > 0 else by0), bx1, (by0 + 1.3) if flip > 0 else (by1 - 1.3)),
                       _paint((50, 60, 80), lvl))
            hy = oy + 0.02 * flip
            c.drawCircle(x - 1.1, hy, 0.12, _paint(mix((90, 90, 96), (200, 200, 205), grey), lvl))
            c.drawRect(skia.Rect(x - 1.34, (hy - 0.78) if flip > 0 else (hy + 0.1), x - 0.86,
                                 (hy - 0.1) if flip > 0 else (hy + 0.78)), _paint(mix((70, 70, 76), (170, 170, 176), grey), lvl))
            if detail:
                c.drawRect(skia.Rect(x + 0.95, oy - 0.45, x + 1.62, oy + 1.35), _paint((60, 46, 36), lvl))
            if uses:
                k = 1.0 if others_on else max(0.0, 1 - (s - T_ALL) / 0.15)
                if k > 0:
                    fl = 0.8 + 0.2 * math.sin(s * 9 + ph)
                    _glow(c, x - 1.1, oy - 0.36 * flip, 3.6, BLUE, 0.55 * k * fl * lvl)
                    c.drawRect(skia.Rect(x - 1.14, oy - 0.36 * flip - 0.08, x - 1.06, oy - 0.36 * flip + 0.08),
                               _paint((180, 220, 255), k * lvl))
        # la nostra stanza vista da lontano (quando il dettaglio non c'è)
        if cam.w >= 14:
            c.drawRect(skia.Rect(-1.64, -2.04, 1.64, 2.04), _paint((33, 29, 37), lvl))
            c.drawRect(skia.Rect(-1.62, -1.95, -0.58, 0.25), _paint((150, 152, 160), lvl))
            c.drawRect(skia.Rect(-1.62, -1.95, -0.58, -0.65), _paint((44, 66, 104), lvl))
            c.drawRect(skia.Rect(-1.34, -0.78, -0.86, -0.1), _paint(HERO, lvl))
            c.drawCircle(-1.1, 0.02, 0.12, _paint((196, 150, 118), lvl))
            if s < T_OFF:
                _glow(c, -1.1, -0.36, 2.0, BLUE, 0.25 * lvl)

    # --- campus e città ---

    def _campus(self, c, cam, s, a):
        # prato, vialetti, alberi e lampioni ci sono già attorno all'edificio; gli altri edifici compaiono uscendo
        ground = a * (1 - gfx.ease_in_out((math.log10(cam.w) - math.log10(5000)) / 0.5))
        lvl = ground * gfx.ease_in_out((math.log10(cam.w) - math.log10(90)) / 0.4)
        if ground <= 0:
            return
        px = cam.px
        c.drawRect(skia.Rect(-1300, -1300, 1300, 1300), _paint((24, 34, 30), ground))
        # vialetti e prati
        path_p = _paint((70, 72, 80), ground, StrokeWidth=max(3.0, px * 1.8), Style=skia.Paint.kStroke_Style)
        for k in range(-6, 7):
            c.drawLine(k * 160, -1200, k * 160, 1200, path_p)
            c.drawLine(-1200, k * 140, 1200, k * 140, path_p)
        for x, y, r in self.trees:
            if abs(x) < 40 and abs(y) < 30:
                continue
            c.drawCircle(x, y, r, _paint((30, 52, 38), ground))
        if cam.w < 400:
            # siepe e alberi lungo il nostro edificio, con un lampione davanti all'ingresso
            for x, y, r in self.near_trees:
                c.drawCircle(x + 0.6, y - 0.8, r, _paint((8, 10, 12), 0.5 * ground))
                c.drawCircle(x, y, r, _paint((34, 58, 42), ground))
                c.drawCircle(x - r * 0.25, y + r * 0.25, r * 0.55, _paint((44, 72, 52), ground))
            for lx in (-12.0, 12.0):
                _glow(c, lx, -5.0, 7.0, WARM, 0.5 * ground)
                c.drawCircle(lx, -5.0, 0.25, _paint((255, 230, 190), ground))
        if lvl <= 0:
            return
        for x0, y0, x1, y1, lr in self.campus:
            c.drawRect(skia.Rect(x0 + 2, y0 - 4, x1 + 2, y1 - 4), _paint((10, 12, 14), 0.55 * lvl))   # ombra
            c.drawRect(skia.Rect(x0, y0, x1, y1), _paint((58, 58, 68), lvl))
            c.drawRect(skia.Rect(x0 + 2.0, y0 + 2.0, x1 - 2.0, y1 - 2.0), _paint((70, 70, 82), lvl))
            if cam.w < 700:
                n = int((x1 - x0) / 5)
                for j in range(n):
                    if (j * 7 + int(lr * 50)) % 3 != 0:
                        c.drawRect(skia.Rect(x0 + 2 + j * 5, y0 - 0.6, x0 + 4 + j * 5, y0 + 0.4),
                                   _paint(WARM if s > T_ALL else BLUE, 0.85 * lvl))
        # il nostro edificio: tetto che sostituisce la pianta quando si esce
        roof = gfx.ease_in_out((math.log10(cam.w) - math.log10(120)) / 0.35)
        if roof > 0:
            c.drawRect(skia.Rect(-31, -2.25, 31, 8.35), _paint((60, 58, 68), roof * lvl))
            c.drawRect(skia.Rect(-29, -0.2, 29, 6.3), _paint((70, 68, 78), roof * lvl))
        # lampioni lungo i vialetti
        lamp = WARM
        for k in range(-7, 8):
            for j in range(-9, 10):
                _glow(c, k * 160, j * 140, max(10.0, px * 9), lamp, 0.45 * lvl)

    def _city(self, c, cam, s, a):
        """Griglia di Chicago: una strada grande ogni miglio, una piccola ogni ottavo; niente strade nel lago."""
        lw = math.log10(cam.w)
        lvl = a * gfx.ease_in_out((lw - 2.6) / 0.5) * (1 - gfx.ease_in_out((lw - 4.45) / 0.35))
        if lvl <= 0:
            return
        px = cam.px
        c.save()
        if self.atlas is not None:
            c.clipPath(self.atlas.lakes, skia.ClipOp.kDifference, True)
        R = 26000
        minor = _paint((60, 62, 70), 0.5 * lvl * min(1.0, 300 / cam.w * 4), StrokeWidth=max(4.0, px * 0.8),
                       Style=skia.Paint.kStroke_Style)
        major = _paint((255, 176, 90), 0.55 * lvl, StrokeWidth=max(12.0, px * 1.6), Style=skia.Paint.kStroke_Style)
        if cam.w < 6000:
            step = 201.0
            n = int(min(R, cam.w * 1.5) / step)
            x0 = round(cam.cx / step)
            y0 = round(cam.cy / step)
            for k in range(-n, n + 1):
                c.drawLine((x0 + k) * step, cam.cy - cam.w * 1.5, (x0 + k) * step, cam.cy + cam.w * 1.5, minor)
                c.drawLine(cam.cx - cam.w * 1.5, (y0 + k) * step, cam.cx + cam.w * 1.5, (y0 + k) * step, minor)
        mile = 1609.0
        for k in range(-16, 17):
            c.drawLine(k * mile, -R, k * mile, R, major)
            c.drawLine(-R, k * mile, R, k * mile, major)
        c.restore()

    # --- Luna ---

    def _moon(self, c, s, px):
        """Allunaggio visto dall'alto: modulo, bandiera, astronauti, impronte. Uno filma in orizzontale."""
        c.drawCircle(0, 0, 40, _paint((112, 112, 117)))
        for j in range(40):
            x = -14 + j * 0.55
            y = -6 + math.sin(j * 0.6) * 1.2
            c.drawOval(skia.Rect(x - 0.12, y - 0.07, x + 0.12, y + 0.07), _paint((90, 90, 95)))
        # modulo lunare
        for ang in (45, 135, 225, 315):
            r = math.radians(ang)
            c.drawLine(0, 0, math.cos(r) * 3.2, math.sin(r) * 3.2, _paint((180, 180, 186), StrokeWidth=0.18))
            c.drawCircle(math.cos(r) * 3.2, math.sin(r) * 3.2, 0.45, _paint((150, 150, 156)))
        oct_ = skia.Path()
        oct_.addPoly([skia.Point(math.cos(math.radians(22.5 + 45 * k)) * 2.1, math.sin(math.radians(22.5 + 45 * k)) * 2.1)
                      for k in range(8)], True)
        c.drawPath(oct_, _paint((214, 170, 70)))
        c.drawCircle(0, 0, 1.2, _paint((225, 225, 230)))
        # bandiera (la Terra, niente nazioni)
        c.drawLine(5.5, 2.0, 5.5, 4.2, _paint((220, 220, 225), StrokeWidth=0.08))
        _rr(c, 5.5, 3.2, 7.3, 4.2, 0.05, (40, 90, 170))
        c.drawCircle(6.4, 3.7, 0.33, _paint((80, 160, 110)))
        # astronauti: uno vicino alla bandiera, l'altro in primo piano che filma con la telecamera in ORIZZONTALE
        self._astronaut(c, 4.0, -1.6, 0.0, False, s)
        self._astronaut(c, ASTRO[0], ASTRO[1], 12.0, True, s)

    def _astronaut(self, c, x, y, rot, filming, s=0.0):
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.drawOval(skia.Rect(-0.42, -0.55, 0.42, 0.25), _paint((0, 0, 0), 0.25))            # ombra
        _rr(c, -0.3, -0.05, 0.3, 0.5, 0.12, (200, 200, 205))                                 # zaino
        _rr(c, -0.36, -0.42, 0.36, 0.2, 0.18, (238, 238, 242))                               # tuta
        c.drawCircle(0, 0.08, 0.24, _paint((245, 245, 248)))                                 # casco
        c.drawOval(skia.Rect(-0.17, -0.06, 0.17, 0.12), _paint((214, 170, 70)))              # visiera dorata
        c.drawOval(skia.Rect(-0.1, 0.03, -0.02, 0.09), _paint((255, 240, 200), 0.7))
        if filming:
            # braccia avanti e telecamera larga, orizzontale, con il puntino rosso REC
            for side in (-1, 1):
                c.drawLine(side * 0.3, -0.15, side * 0.22, -0.55, _paint((232, 232, 236), StrokeWidth=0.13,
                                                                        StrokeCap=skia.Paint.kRound_Cap))
            # telecamera 16:9 larga, con l'inquadratura: orizzonte lunare e la Terra
            _rr(c, -0.5, -0.95, 0.5, -0.38, 0.06, (28, 28, 32))
            c.save()
            c.clipRect(skia.Rect(-0.45, -0.9, 0.45, -0.43))
            c.drawRect(skia.Rect(-0.45, -0.9, 0.45, -0.43), _paint((4, 6, 14)))
            c.drawRect(skia.Rect(-0.45, -0.9, 0.45, -0.76), _paint((120, 120, 126)))
            c.drawCircle(0.12, -0.6, 0.085, _paint((60, 120, 220)))
            c.drawOval(skia.Rect(0.07, -0.62, 0.15, -0.56), _paint((80, 170, 110)))
            c.restore()
            if (s * 1.6) % 1 < 0.6:
                c.drawCircle(-0.38, -0.48, 0.028, _paint((255, 50, 50)))
            _text(c, "REC", -0.34, -0.495, 0.045, (255, 255, 255), 0.9, kind="mono")
        c.restore()

    # --- infografica dello studio ---

    def _study(self, c, s, a):
        """1.000 telefoni (gli studenti): da soli non smettono; se smettono tutti, pagherebbero per farlo."""
        W, H = 1080, 1920
        c.drawRect(skia.Rect(0, 0, W, H), _paint((6, 8, 16), 0.86 * a))
        cols, rows = 40, 25
        x0, y0, cw, ch = 92, 840, 22.5, 37.5
        rng = np.random.default_rng(11)
        order = rng.random(cols * rows)
        flip_center = (cols / 2, rows / 2)
        for idx in range(cols * rows):
            i, j = idx % cols, idx // cols
            appear = order[idx] * 0.8
            k = min(1.0, max(0.0, (s - appear) / 0.25))
            if k <= 0:
                continue
            x, y = x0 + i * cw, y0 + j * ch
            dist = math.hypot(i - flip_center[0], (j - flip_center[1]) * 1.6) / 28
            off = min(1.0, max(0.0, (s - 6.6 - dist * 1.1) / 0.18))
            col = mix(BLUE, WARM, off)
            if s > 9.8:
                # waffle: i primi 58 su 100 (riga per riga dall'alto) restano accesi, gli altri si spengono
                fill = min(0.58, (s - 9.8) / 0.7 * 0.58)
                if idx < fill * cols * rows:
                    col = mix(WARM, (255, 240, 215), 0.45)
                else:
                    col = mix(WARM, (46, 46, 56), min(1.0, (s - 9.8) / 0.5))
            single = (i, j) == (20, 12) and 3.2 < s < 6.6
            _rr(c, x, y, x + 14, y + 26, 3.5, col, k * a)
            c.drawRect(skia.Rect(x + 2, y + 3, x + 12, y + 21), _paint(mix(col, (255, 255, 255), 0.25), 0.5 * k * a))
            if single:
                c.drawCircle(x + 7, y + 13, 30, _paint((255, 255, 255), a, Style=skia.Paint.kStroke_Style,
                                                     StrokeWidth=3))
        # cartellino del numero grande
        big = gfx.mono(150, "SemiBold")
        if 3.2 < s < 6.6:
            v = min(55.0, (s - 3.2) / 0.7 * 55)
            K.rolling_number(c, v, W / 2, 760, big, color=(255, 255, 255), alpha=a, fmt="+${:,.0f}")
            gfx.draw_text(c, "TO QUIT ALONE", gfx.mono(34, "Medium"), W / 2, 805, color=(200, 205, 220), alpha=a,
                          tracking=2)
        elif 6.6 <= s < 9.8:
            v = min(24.0, (s - 6.6) / 0.7 * 24)
            K.rolling_number(c, v, W / 2, 760, big, color=WARM, alpha=a, fmt="-${:,.0f}")
            gfx.draw_text(c, "THEY'D PAY, IF EVERYONE QUIT", gfx.mono(34, "Medium"), W / 2, 805, color=WARM,
                          alpha=a, tracking=2)
        elif s >= 9.8:
            v = min(58.0, max(0.0, (s - 9.8) / 0.7 * 58))
            K.rolling_number(c, v, W / 2, 760, big, color=(255, 255, 255), alpha=a, fmt="{:,.0f}%")
            gfx.draw_text(c, "PREFER A WORLD WITHOUT IT", gfx.mono(34, "Medium"), W / 2, 805,
                          color=(200, 205, 220), alpha=a, tracking=2)

    # ---------- audio ----------

    def audio(self, mx, r, ts, near, rng):
        """Stanza: ronzio leggero, musica ovattata dal telefono che cambia a ogni video, swipe, poi silenzio."""
        from . import audio as A
        from . import whatif_audio as WA
        tl = r.tl
        n = mx.n

        def room(m, rng):
            x = WA._lp(rng.normal(0, 1, m), 180) * 0.6
            return x + 0.08 * np.sin(2 * np.pi * 60 * np.arange(m) / WA.SR)

        mx.add(0.0, WA.loop_bed(room, n, ts, near, rng) * 0.25, reverb=0.05)
        # musica dal telefono, campionata dalla timeline
        dt = 0.02
        last_i = None
        for k, vt in enumerate(ts[:-1]):
            mode, s, where = tl.scene_state(vt)
            if mode != "dorm" or near[k] < 0.05 or s >= T_HOME:
                last_i = None
                continue
            i, local, sw = video_at(s)
            if i != last_i:
                # nuovo video: swipe e un loop di musica diversa
                mx.add(vt, WA.whoosh(0.16, rng, up=True), 0.05 * near[k], reverb=0.05)
                dur = DURS[i] - local
                mx.add(vt, self._phone_music(VIDEOS[i], dur, rng) * near[k], 0.22, pan=-0.1, reverb=0.08)
            last_i = i
        # cancellazione: tap, "poof", schermo spento; tutti i telefoni spenti insieme: colpo basso
        for k, vt in enumerate(ts[:-1]):
            mode, s, where = tl.scene_state(vt)
            mode2, s2, _ = tl.scene_state(vt + dt)
            if mode != "dorm" or mode2 != "dorm" or s2 < s or s2 - s > 0.1:
                continue
            for te, snd, g in ((T_TAP, WA.click(1800, 0.03), 0.3), (T_GONE, WA.tick(rng), 0.4),
                               (T_OFF, WA.click(900, 0.05), 0.35)):
                if s < te <= s2:
                    mx.add(vt, snd, g, reverb=0.25)
        # infografica: ticchettii mentre compaiono i telefoni, whoosh quando si spengono
        for t0, val in tl.scene_tr:
            if val[0] == "study":
                for j in range(14):
                    mx.add(t0 + j * 0.055, WA.tick(rng), 0.05, pan=rng.uniform(-0.5, 0.5), reverb=0.1)
                mx.add(t0 + 6.6, WA.whoosh(1.1, rng, up=False), 0.25, reverb=0.3)
                mx.add(t0 + 3.2, A.bell(A.note(69), 1.5), 0.3, reverb=0.4)
                mx.add(t0 + 6.6, A.bell(A.note(62), 2.0), 0.35, reverb=0.5)
                mx.add(t0 + 9.8, A.bell(A.note(74), 2.0), 0.3, reverb=0.5)

    @staticmethod
    def _phone_music(kind, dur, rng):
        """Un paio di battute dal piccolo altoparlante: cassa, charleston e un accordo, filtrati."""
        from . import audio as A
        from . import whatif_audio as WA
        sr = WA.SR
        bpm = {"dance": 124, "cat": 100, "balls": 90, "meme": 140, "food": 96, "game": 150, "sunset": 84}[kind]
        root = {"dance": 57, "cat": 62, "balls": 60, "meme": 55, "food": 59, "game": 64, "sunset": 53}[kind]
        nn = int(dur * sr)
        x = np.zeros(nn)
        beat = 60.0 / bpm
        t = np.arange(nn) / sr
        for b in range(int(dur / beat) + 1):
            i0 = int(b * beat * sr)
            if i0 >= nn:
                break
            kk = np.arange(min(int(0.18 * sr), nn - i0)) / sr
            x[i0:i0 + len(kk)] += np.sin(2 * np.pi * (50 + 80 * np.exp(-kk * 30)) * kk) * np.exp(-kk * 18)
            j0 = int((b + 0.5) * beat * sr)
            if j0 < nn:
                hh = rng.normal(0, 1, min(int(0.04 * sr), nn - j0)) * np.exp(-np.arange(min(int(0.04 * sr), nn - j0)) / sr * 90)
                x[j0:j0 + len(hh)] += 0.3 * hh
        for semi in (0, 4, 7):
            x += 0.18 * np.sign(np.sin(2 * np.pi * A.note(root + semi) * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * t / beat))
        x = WA._bp(x, 350, 2600)
        fade = np.minimum(1, np.minimum(t / 0.01, (dur - t) / 0.03))
        return x * fade / (np.abs(x).max() + 1e-9)
