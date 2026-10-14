"""Autostrada a due corsie con la sinistra che chiude: simulazione del traffico (IDM) e disegno dall'alto.

La strada corre verso nord (in alto sullo schermo). x = metri lungo la strada, 0 = fine della corsia
sinistra. Due modi di immettersi:
- early:  appena visto il cartello si passa a destra; la sinistra resta vuota e la coda è su una corsia sola
- zipper: si usano entrambe le corsie fino alla fine e lì si entra a turno (una macchina per parte)

Le due simulazioni partono vuote con la stessa domanda e lo stesso seed: a parità di tempo
si confronta la lunghezza della coda.
"""

import math
from dataclasses import dataclass, field

import numpy as np
import skia

from .gfx import mix, rgba

DT = 0.1
SPAWN_X, EXIT_X = -6000.0, 500.0
X_END = 0.0              # fine della corsia sinistra
TAPER = 70.0             # lunghezza dello smusso dei coni
STOP_X = X_END - 22.0    # chi è in corsia sinistra si ferma qui se non riesce a entrare
SIGN_X = -1600.0         # "LEFT LANE CLOSED 1 MILE"
WZ_V = 6.5               # velocità media nel cantiere: è lui il collo di bottiglia, come nella realtà
WZ_WAVE = (4.5, 30.0)    # ...ma pulsa (mezzi che entrano ed escono): la coda diventa stop-and-go, fitta
LANE_W = 3.6
LANE_Y = (1.8, -1.8)     # centro corsia (x mondo): 0 = destra (continua), 1 = sinistra (chiude)
LANE_CHANGE = 2.6        # secondi per spostarsi di corsia

# Intelligent Driver Model
A_MAX, B_COMF, S0, T_HEAD = 1.3, 2.0, 1.7, 1.2


def idm(v, v0, gap, dv):
    s_star = S0 + np.maximum(0.0, v * T_HEAD + v * dv / (2 * math.sqrt(A_MAX * B_COMF)))
    return A_MAX * (1 - (v / v0) ** 4 - (s_star / np.maximum(gap, 0.1)) ** 2)


@dataclass
class Car:
    id: int
    x: float
    v: float
    lane: int
    v0: float
    length: float
    shade: float           # 0 scuro .. 1 chiaro (le macchine sono in scala di grigi)
    kind: str = "car"      # car | hero | late
    merge_x: float = 0.0   # da qui prova a entrare a destra
    lane_t: float = -99.0  # quando ha iniziato il cambio corsia
    yield_t: float = -99.0  # quando ha fatto entrare qualcuno l'ultima volta (uno a testa, poi tocca a chi segue)
    a: float = 0.0


@dataclass
class Recording:
    """Stato a ogni passo nella finestra registrata: per ogni passo, array ordinati per id."""
    t0: float
    steps: list = field(default_factory=list)   # (ids, x, lat, v, a, length, shade, kind)
    honks: list = field(default_factory=list)   # (t, id)
    backup: list = field(default_factory=list)  # (t, metri di coda)
    hero: int = -1

    def frame(self, t):
        """Stato interpolato al tempo t (dentro la finestra)."""
        k = (t - self.t0) / DT
        i = int(np.clip(math.floor(k), 0, len(self.steps) - 2))
        u = float(np.clip(k - i, 0, 1))
        a, b = self.steps[i], self.steps[i + 1]
        common, ia, ib = np.intersect1d(a[0], b[0], return_indices=True)
        out = [common]
        for j in range(1, 5):
            out.append(a[j][ia] * (1 - u) + b[j][ib] * u)
        out += [a[5][ia], a[6][ia], a[7][ia]]
        return out

    def backup_at(self, t):
        ts = np.array([b[0] for b in self.backup])
        return float(np.interp(t, ts, [b[1] for b in self.backup]))

    def hero_x(self, t):
        ids, x = self.frame(t)[:2]
        k = np.nonzero(ids == self.hero)[0]
        return float(x[k[0]]) if len(k) else 0.0


class Sim:
    def __init__(self, mode, seed, demand=2350.0, left_share=0.42):
        self.mode = mode
        self.rng = np.random.default_rng(seed)
        self.rate = demand / 3600.0
        self.left_share = left_share
        self.cars = []
        self.t = 0.0
        self.next_id = 0
        self.pending = [0, 0]
        self.switch_t = None  # da qui tutti entrano subito (early)

    # ---------- comportamento ----------

    def _merge_x(self, kind):
        # Anche quando la regola è lo zipper, metà dei guidatori si immette presto per abitudine.
        zipper = self.mode == "zipper" and self.rng.random() < 0.5
        if kind in ("hero", "late") or zipper:
            return X_END - TAPER + self.rng.uniform(0, 25)
        return SIGN_X + self.rng.uniform(-150, 250)

    def new_car(self, x, v, lane, kind="car", v0=None):
        c = Car(self.next_id, x, v, lane,
                v0=v0 or float(self.rng.normal(25.5, 1.6)),
                length=float(self.rng.choice([4.4, 4.7, 4.9, 5.4], p=[0.3, 0.35, 0.2, 0.15])),
                shade=float(self.rng.uniform(0.0, 1.0)), kind=kind)
        c.merge_x = self._merge_x(kind)
        self.next_id += 1
        self.cars.append(c)
        return c

    def _spawn(self):
        for lane in (0, 1):
            share = self.left_share if lane else 1 - self.left_share
            if self.rng.random() < self.rate * share * DT:
                self.pending[lane] += 1
            if not self.pending[lane]:
                continue
            last = min((c for c in self.cars if c.lane == lane), key=lambda c: c.x, default=None)
            if last is None or last.x - last.length - SPAWN_X > S0 + T_HEAD * last.v + 4:
                v = 24.0 if last is None else min(24.0, last.v + 2)
                self.new_car(SPAWN_X, v, lane)
                self.pending[lane] -= 1

    def step(self):
        cars = self.cars
        n = len(cars)
        x = np.array([c.x for c in cars])
        v = np.array([c.v for c in cars])
        lane = np.array([c.lane for c in cars])
        length = np.array([c.length for c in cars])
        v0 = np.array([c.v0 for c in cars])
        wz = WZ_V + WZ_WAVE[0] * math.sin(2 * math.pi * self.t / WZ_WAVE[1])
        v0 = np.minimum(v0, np.interp(x, [X_END - 320, X_END - 90], [40.0, max(1.5, wz)]))
        acc = np.full(n, A_MAX)

        order = {}
        for ln in (0, 1):
            idx = np.nonzero(lane == ln)[0]
            idx = idx[np.argsort(x[idx])]
            order[ln] = idx
            if len(idx) > 1:
                me, lead = idx[:-1], idx[1:]
                acc[me] = idm(v[me], v0[me], x[lead] - length[lead] - x[me], v[me] - v[lead])
            if len(idx):
                top = idx[-1]
                acc[top] = idm(v[top], v0[top], 1e4, 0.0)
        # La corsia sinistra finisce: ostacolo fermo a STOP_X.
        left = order[1]
        if len(left):
            acc[left] = np.minimum(acc[left], idm(v[left], v0[left], STOP_X - x[left], v[left]))

        # Chi vuole entrare a destra: controlla il varco, altrimenti chiede strada a chi sta dietro.
        right = order[0]
        rx = x[right]
        merges = []
        for i in left[::-1]:
            c = cars[i]
            if self.switch_t is not None and self.t >= self.switch_t:
                c.merge_x = min(c.merge_x, c.x)
            k = np.searchsorted(rx, c.x, side="right")
            lead = right[k] if k < len(right) else None
            foll = right[k - 1] if k > 0 else None
            # Chi si immette presto lo fa anche appena vede la coda accanto (prima del cartello).
            if (c.merge_x < X_END - TAPER - 30 and c.kind == "car" and lead is not None
                    and v[lead] < 8.0 and x[lead] - c.x < 80):
                c.merge_x = min(c.merge_x, c.x)
            if c.x < c.merge_x:
                continue
            gap_f = x[lead] - length[lead] - c.x if lead is not None else 1e4
            gap_b = c.x - c.length - x[foll] if foll is not None else 1e4
            ok = gap_f > 1.0 + 0.4 * c.v and gap_b > 1.0 + 0.6 * max(0.0, v[foll] - c.v if foll is not None else 0)
            if ok and foll is not None:
                ok = idm(v[foll], v0[foll], gap_b, v[foll] - c.v) > -3.5
            if ok:
                merges.append(i)
                continue
            if lead is not None:  # si allinea al varco davanti
                acc[i] = min(acc[i], idm(c.v, c.v0, gap_f + 2.5, c.v - v[lead]))
            # Zipper: ognuno fa entrare una sola macchina (alternanza stretta). Early: i cortesi cedono di nuovo dopo un po'.
            cool = 10.0 if self.mode == "early" else 1e9
            if foll is not None and self.t - cars[foll].yield_t > cool:
                acc[foll] = min(acc[foll], idm(v[foll], v0[foll], max(gap_b, 0.3), v[foll] - c.v))

        for i in merges:
            c = cars[i]
            c.lane, c.lane_t = 0, self.t
            k = np.searchsorted(rx, c.x, side="right")
            if k > 0:
                cars[right[k - 1]].yield_t = self.t

        acc = np.clip(acc, -8.0, A_MAX)
        v_new = np.maximum(0.0, v + acc * DT)
        x_new = x + (v + v_new) / 2 * DT
        for j, c in enumerate(cars):
            c.v, c.x, c.a = float(v_new[j]), float(x_new[j]), float(acc[j])
        self.cars = [c for c in cars if c.x < EXIT_X]
        self._spawn()
        self.t += DT

    def lat(self, c):
        """Posizione laterale (x mondo) con il cambio corsia addolcito."""
        k = min(1.0, (self.t - c.lane_t) / LANE_CHANGE)
        k = k * k * (3 - 2 * k)
        if k >= 1:
            return LANE_Y[c.lane]
        return LANE_Y[1] + (LANE_Y[0] - LANE_Y[1]) * k

    def backup(self):
        """Metri di coda: dalla fine della corsia indietro finché le macchine lente sono contigue."""
        slow = sorted((c.x for c in self.cars if c.v < 8.0 and c.x < X_END + 30), reverse=True)
        tail = X_END
        for x in slow:
            if x < tail - 120:
                break
            tail = min(tail, x)
        return X_END - tail

    def snapshot(self):
        cars = sorted(self.cars, key=lambda c: c.id)
        kinds = {"car": 0, "hero": 1, "late": 2}
        return (np.array([c.id for c in cars]), np.array([c.x for c in cars]),
                np.array([self.lat(c) for c in cars]), np.array([c.v for c in cars]),
                np.array([c.a for c in cars]), np.array([c.length for c in cars]),
                np.array([c.shade for c in cars]), np.array([kinds[c.kind] for c in cars]))


def run(mode, seed, t_rec0, t_rec1, hero_at=None, switch_t=None, late_at=()):
    """Simula fino a t_rec1 e registra la finestra [t_rec0, t_rec1].

    hero_at = (t, x): l'eroe (corsia sinistra, prudente) entra in scena a quel tempo e posizione.
    late_at = tempi in cui spuntano altri "furbi" in corsia sinistra. switch_t: da qui tutti entrano subito.
    """
    sim = Sim(mode, seed)
    sim.switch_t = switch_t
    rec = Recording(t_rec0)
    late = sorted(late_at)
    passed = {}
    while sim.t < t_rec1 + DT:
        if hero_at and rec.hero < 0 and sim.t >= hero_at[0]:
            rec.hero = sim.new_car(hero_at[1], 13.5, 1, "hero", v0=13.5).id
        while late and sim.t >= late[0][0]:
            sim.new_car(late.pop(0)[1], 13.5, 1, "late", v0=14.0)
        sim.step()
        if sim.t >= t_rec0 - 1e-9:
            rec.steps.append(sim.snapshot())
            if int(round(sim.t / DT)) % 5 == 0:
                rec.backup.append((sim.t, sim.backup()))
            _honks(sim, rec, passed)
    return rec


def _honks(sim, rec, passed):
    """Chi viene sorpassato da un furbo in corsia sinistra ogni tanto suona il clacson."""
    furbi = [c for c in sim.cars if c.lane == 1 and c.kind in ("hero", "late") and c.v > 5]
    if not furbi:
        return
    queue = [c for c in sim.cars if c.lane == 0 and c.v < 6]
    for f in furbi:
        for q in queue:
            key = (f.id, q.id)
            if key in passed:
                continue
            if q.x - q.length < f.x - f.length < q.x:
                passed[key] = True
                if sim.rng.random() < 0.22:
                    rec.honks.append((sim.t, q.id))


# ---------- disegno ----------

@dataclass(frozen=True)
class Skin:
    ground: tuple
    road: tuple
    shoulder: tuple
    line: tuple
    edge: tuple
    trees: bool = True


EARTH = Skin(ground=(27, 31, 28), road=(46, 48, 54), shoulder=(54, 56, 62), line=(214, 216, 222),
             edge=(222, 186, 92))
MOON = Skin(ground=(92, 92, 96), road=(54, 54, 58), shoulder=(64, 64, 68), line=(200, 200, 205),
            edge=(200, 200, 205), trees=False)

HERO = (242, 184, 75)
ORANGE = (238, 120, 40)
TAIL = (255, 60, 50)


def _hash(i, k=0):
    return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1.0


def draw_road(c, y0, y1, skin, px=1.0, alpha=1.0):
    """Strada tra y0 e y1 (metri). px = metri per pixel a schermo, per i dettagli adattivi.
    Il terreno intorno lo stende chi chiama, su tutto lo schermo."""

    def P(col, a=1.0):
        return skia.Paint(AntiAlias=True, Color=rgba(col, a * alpha))

    # Carreggiata opposta (sud) oltre lo spartitraffico.
    c.drawRect(skia.Rect(-27.0, y0, -14.0, y1), P(skin.road))
    c.drawRect(skia.Rect(-5.6, y0, 5.4, y1), P(skin.shoulder))
    c.drawRect(skia.Rect(-LANE_W, y0, LANE_W, y1), P(skin.road))
    # Zona chiusa oltre la fine della corsia: più scura.
    if y1 > X_END:
        c.drawRect(skia.Rect(-LANE_W, max(y0, X_END), 0.0, y1), P(mix(skin.road, (0, 0, 0), 0.25)))
    if px > 2.5:
        return
    lw = max(0.14, px * 1.2)
    line = skia.Paint(AntiAlias=True, Color=rgba(skin.line, 0.85 * alpha), StrokeWidth=lw,
                      Style=skia.Paint.kStroke_Style)
    edge = skia.Paint(AntiAlias=True, Color=rgba(skin.edge, 0.85 * alpha), StrokeWidth=lw,
                      Style=skia.Paint.kStroke_Style)
    c.drawLine(LANE_W, y0, LANE_W, y1, line)
    c.drawLine(-14.6, y0, -14.6, y1, edge)
    # Bordo sinistro: dritto fino allo smusso, poi diagonale verso il centro.
    taper0 = X_END - TAPER
    if y0 < taper0:
        c.drawLine(-LANE_W, y0, -LANE_W, min(y1, taper0), edge)
    if y1 > taper0:
        c.drawLine(-LANE_W, taper0, 0.0, X_END, edge)
        if y1 > X_END:
            c.drawLine(0.0, X_END, 0.0, y1, edge)
    # Tratteggio centrale (3 m pieni, 9 vuoti) fino allo smusso; sulla carreggiata sud due tratteggi.
    if px < 0.6:
        k0 = int(math.floor(y0 / 12.0))
        for k in range(k0, int(math.ceil(y1 / 12.0)) + 1):
            yy = k * 12.0
            if yy < taper0:
                c.drawLine(0.0, yy, 0.0, yy + 3.0, line)
            c.drawLine(-20.5, yy + 6, -20.5, yy + 9.0, line)
    # Coni lungo lo smusso e barili nella zona chiusa.
    cone = P(ORANGE)
    for k in range(int(TAPER / 7) + 1):
        yy = taper0 + k * 7.0
        if y0 - 5 < yy < y1 + 5:
            c.drawCircle(-LANE_W + LANE_W * k * 7.0 / TAPER, yy, 0.36, cone)
    for k in range(0, 40):
        yy = X_END + 6 + k * 14.0
        if y0 - 5 < yy < y1 + 5:
            c.drawCircle(-LANE_W / 2, yy, 0.5, cone)
            c.drawCircle(-LANE_W / 2, yy, 0.22, P((245, 240, 230)))
    # Alberi sui bordi (posizioni fisse da hash, così non sfarfallano).
    if skin.trees and px < 1.2:
        for k in range(int(y0 // 9) - 1, int(y1 // 9) + 2):
            for side, base in ((1, 9.5), (-1, -9.8)):
                h = _hash(k, side)
                if h < 0.55:
                    continue
                tx = base + side * _hash(k, side + 3) * (14 if side > 0 else 2.5)
                ty = k * 9.0 + _hash(k, side + 7) * 6
                r = 1.6 + _hash(k, side + 11) * 1.8
                c.drawCircle(tx + 0.5, ty - 0.6, r, P((12, 14, 12), 0.5))
                c.drawCircle(tx, ty, r, P(mix(skin.ground, (60, 84, 58), 0.6 + 0.4 * _hash(k, side + 5))))
    # Crateri sulla Luna.
    if not skin.trees and px < 1.2:
        for k in range(int(y0 // 23) - 1, int(y1 // 23) + 2):
            for side in (-1, 1):
                h = _hash(k, side + 20)
                tx = side * (12 + 60 * _hash(k, side + 21))
                ty = k * 23.0 + 10 * _hash(k, side + 22)
                r = 1.2 + 5 * h ** 3
                c.drawCircle(tx, ty, r, P((70, 70, 74)))
                c.drawCircle(tx + 0.25 * r, ty - 0.25 * r, r * 0.8, P((82, 82, 86)))


def draw_signs(c, font, y0, y1, px, alpha=1.0):
    """Cartelli arancioni di cantiere sul bordo destro."""
    if px > 0.5:
        return
    for sy, lines in ((SIGN_X, ("LEFT LANE", "CLOSED", "1 MILE")), (X_END - 450, ("LEFT LANE", "CLOSED", "AHEAD")),
                      (X_END - 130, ("MERGE", "", ""))):
        if not (y0 - 10 < sy < y1 + 10):
            continue
        cx, cy = 7.6, sy
        c.drawRect(skia.Rect(cx - 0.08, cy - 0.1, cx + 0.08, cy + 2.2), skia.Paint(Color=rgba((90, 90, 90), alpha)))
        c.save()
        c.translate(cx, cy + 1.8)
        c.rotate(45)
        c.drawRect(skia.Rect(-1.1, -1.1, 1.1, 1.1), skia.Paint(AntiAlias=True, Color=rgba(ORANGE, alpha)))
        c.restore()
        c.save()
        c.translate(cx, cy + 1.8)
        c.scale(1, -1)
        for k, s in enumerate(l for l in lines if l):
            w = font.measureText(s)
            c.drawString(s, -w / 2, -0.25 + k * 0.42 - 0.2 * (len([l for l in lines if l]) - 2),
                         font, skia.Paint(AntiAlias=True, Color=rgba((20, 20, 20), alpha)))
        c.restore()


def draw_cars(c, st, px, alpha=1.0, hero_glow=0.0, honk=None, blink=0.0):
    """Macchine viste dall'alto. st = Recording.frame(t). Da lontano diventano puntini."""
    ids, x, lat, v, a, length, shade, kind = st
    if px > 0.9:
        # Da lontano (macchina sotto i 5 px) solo puntini: rossi se frenano o sono in coda, bianchi se scorrono.
        pts_slow = [skia.Point(lat[i], x[i]) for i in range(len(ids)) if v[i] < 7]
        pts_fast = [skia.Point(lat[i], x[i]) for i in range(len(ids)) if v[i] >= 7]
        r = px * 3.6
        c.drawPoints(skia.Canvas.kPoints_PointMode, pts_slow,
                     skia.Paint(AntiAlias=True, StrokeWidth=r * 3, StrokeCap=skia.Paint.kRound_Cap,
                                Color=rgba(TAIL, 0.25 * alpha),
                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, px * 3)))
        c.drawPoints(skia.Canvas.kPoints_PointMode, pts_fast,
                     skia.Paint(AntiAlias=True, StrokeWidth=r, StrokeCap=skia.Paint.kRound_Cap,
                                Color=rgba((235, 235, 240), 0.8 * alpha)))
        c.drawPoints(skia.Canvas.kPoints_PointMode, pts_slow,
                     skia.Paint(AntiAlias=True, StrokeWidth=r, StrokeCap=skia.Paint.kRound_Cap,
                                Color=rgba(TAIL, 0.95 * alpha)))
        return
    detail = px < 0.5
    shadow = skia.Paint(AntiAlias=True, Color=rgba((0, 0, 0), 0.45 * alpha),
                        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 0.35) if detail else None)
    glow = skia.Paint(AntiAlias=True, Color=rgba(TAIL, 0.55 * alpha),
                      MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 0.9))
    for i in range(len(ids)):
        L, Wd = length[i], 1.86
        cx, cy = lat[i], x[i] - L / 2
        hero = kind[i] == 1
        base = HERO if hero else mix((70, 72, 78), (222, 223, 228), shade[i])
        c.save()
        c.translate(cx, cy)
        # Durante il cambio corsia il muso punta un po' a destra (verso est = rotazione oraria).
        prog = (lat[i] - LANE_Y[1]) / (LANE_Y[0] - LANE_Y[1])
        if 0.0 < prog < 1.0:
            c.rotate(-11.0 * math.sin(math.pi * prog))
        if hero and hero_glow > 0:
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-Wd, -L * 0.85, Wd, L * 0.85), 1.6, 1.6),
                        skia.Paint(AntiAlias=True, Color=rgba(HERO, 0.35 * hero_glow * alpha),
                                   MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 1.4)))
        body = skia.RRect.MakeRectXY(skia.Rect(-Wd / 2, -L / 2, Wd / 2, L / 2), 0.55, 0.55)
        c.save()
        c.translate(0.22, -0.32)
        c.drawRRect(body, shadow)
        c.restore()
        c.drawRRect(body, skia.Paint(AntiAlias=True, Color=rgba(base, alpha)))
        if detail:
            dark = mix(base, (12, 14, 18), 0.78)
            # parabrezza (davanti = verso nord = y positivo), lunotto, tetto
            ws = skia.Path()
            ws.moveTo(-0.78, L / 2 - 0.95)
            ws.lineTo(0.78, L / 2 - 0.95)
            ws.lineTo(0.68, L / 2 - 1.55)
            ws.lineTo(-0.68, L / 2 - 1.55)
            ws.close()
            c.drawPath(ws, skia.Paint(AntiAlias=True, Color=rgba(dark, alpha)))
            c.drawRect(skia.Rect(-0.7, -L / 2 + 0.55, 0.7, -L / 2 + 0.95), skia.Paint(AntiAlias=True, Color=rgba(dark, alpha)))
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-0.66, -L / 2 + 1.0, 0.66, L / 2 - 1.6), 0.2, 0.2),
                        skia.Paint(AntiAlias=True, Color=rgba(mix(base, (255, 255, 255), 0.12), alpha)))
        # Luci posteriori: si accendono quando frena o è ferma.
        brake = 1.0 if (a[i] < -0.4 or v[i] < 0.3) else 0.0
        tail = skia.Paint(AntiAlias=True, Color=rgba(mix((120, 20, 20), TAIL, brake), alpha))
        c.drawRect(skia.Rect(-Wd / 2 + 0.1, -L / 2, -Wd / 2 + 0.55, -L / 2 + 0.16), tail)
        c.drawRect(skia.Rect(Wd / 2 - 0.55, -L / 2, Wd / 2 - 0.1, -L / 2 + 0.16), tail)
        if brake:
            c.drawCircle(0, -L / 2 - 0.3, 1.25, glow)
        # Freccia: l'eroe mette la freccia a destra quando sta per entrare.
        if hero and blink > 0 and (blink * 2.4) % 1.0 < 0.55:
            c.drawCircle(Wd / 2 - 0.15, L / 2 - 0.2, 0.32,
                         skia.Paint(AntiAlias=True, Color=rgba((255, 170, 40), alpha),
                                    MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 0.25)))
            c.drawCircle(Wd / 2 - 0.15, -L / 2 + 0.2, 0.32, skia.Paint(AntiAlias=True, Color=rgba((255, 170, 40), alpha)))
        c.restore()
        if honk is not None and ids[i] in honk:
            # Clacson: tre archi a sinistra (verso chi sorpassa) che si allargano e svaniscono.
            k = honk[ids[i]]
            for j in range(3):
                kk = k * 1.6 - j * 0.22
                if 0 < kk < 1:
                    r = 1.4 + kk * 3.2
                    c.drawArc(skia.Rect(cx - r, x[i] - 1.2 - r, cx + r, x[i] - 1.2 + r), 145, 70, False, skia.Paint(
                        AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=0.2, StrokeCap=skia.Paint.kRound_Cap,
                        Color=rgba((255, 255, 255), (1 - kk) * 0.9 * alpha)))


def draw_oncoming(c, t, y0, y1, px, alpha=1.0):
    """Traffico scorrevole sulla carreggiata sud: solo atmosfera, nessuna simulazione."""
    if px > 3.0:
        return
    for lane_x, speed, gap, off in ((-17.6, 27.0, 61.0, 0.0), (-23.2, 24.0, 47.0, 21.0)):
        k0 = int(math.floor((y0 + speed * t - off) / gap)) - 1
        for k in range(k0, k0 + int((y1 - y0) / gap) + 3):
            y = k * gap - speed * t + off + 9 * _hash(k, lane_x)
            if not (y0 - 6 < y < y1 + 6):
                continue
            shade = _hash(k, lane_x + 1)
            base = mix((70, 72, 78), (222, 223, 228), shade)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(lane_x - 0.93, y - 2.3, lane_x + 0.93, y + 2.3), 0.55, 0.55),
                        skia.Paint(AntiAlias=True, Color=rgba(base, alpha)))
            c.drawCircle(lane_x, y - 3.4, 1.4, skia.Paint(
                AntiAlias=True, Color=rgba((255, 240, 200), 0.25 * alpha),
                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 0.9)))


# ---------- scena per What If ----------

SPLIT_D = 700.0  # metri tra le due strade nel confronto affiancato


class HighwayScene:
    """Collega le registrazioni al renderer di What If.

    recs: {"A": Recording, "B": Recording}. Il confronto affiancato mette A a sinistra e B a destra;
    labels = (etichetta A, etichetta B).
    """

    def __init__(self, recs, units, labels=("MERGE EARLY", "ZIPPER MERGE"), tags=(), switch_sim=None):
        self.recs = recs
        self.units = units
        self.labels = labels
        self.tags = tags              # finestre (t0, t1) in cui mostrare le velocità
        self.switch_sim = switch_sim  # quando l'eroe mette la freccia (tempo sim)

    def _origin(self, where):
        from .whatif import MOON_POS
        return MOON_POS if where == "moon" else (0.0, 0.0)

    def anchor(self, name, vt, tl):
        rec, t, where = tl.scene_state(vt)
        ox, oy = self._origin(where)
        r = self.recs[rec]
        if name == "hero" and r.hero >= 0:
            st = r.frame(t)
            k = np.nonzero(st[0] == r.hero)[0]
            if len(k):
                return ox + float(st[2][k[0]]), oy + float(st[1][k[0]]) - float(st[5][k[0]]) / 2
        return ox, oy - 300.0

    def honks(self, rec, t, window=0.7):
        return {cid: (t - ht) / window for ht, cid in self.recs[rec].honks if 0 <= t - ht < window}

    def draw(self, c, cam, vt, tl, alpha, ground=1.0):
        from . import gfx
        rec, t, where = tl.scene_state(vt)
        ox, oy = self._origin(where)
        if not cam.near(ox, oy, 8000):
            return
        skin = MOON if where == "moon" else EARTH
        if where == "earth" and ground > 0:
            c.drawRect(skia.Rect(0, 0, 1080, 1920), skia.Paint(Color=rgba(skin.ground, alpha * ground)))
        y0, y1 = cam.visible_y()
        y0, y1 = max(y0 - oy, SPAWN_X), min(y1 - oy, EXIT_X + 200)
        px = cam.px
        split = tl.split_k(vt)
        sign_font = gfx.title(0.36)
        jobs = [(rec, 0.0, 1.0)]
        if split > 0.001:
            jobs = [("A", -SPLIT_D * split, 1.0), ("B", SPLIT_D * split, split)]
        for name, dx, a in jobs:
            r = self.recs[name]
            st = r.frame(t)
            c.save()
            c.concat(cam.matrix(ox + dx, oy))
            draw_road(c, y0, y1, skin, px, alpha * a)
            draw_signs(c, sign_font, y0, y1, px, alpha * a)
            if where == "earth":
                draw_oncoming(c, t, y0, y1, px, alpha * a)
            blink = 0.0
            if self.switch_sim is not None and name == "A" and self.switch_sim - 0.3 < t < self.switch_sim + 3.8:
                blink = t - self.switch_sim + 0.3
            draw_cars(c, st, px, alpha * a, hero_glow=1.0, honk=self.honks(name, t) if where == "earth" else None,
                      blink=blink)
            c.restore()
        if split > 0.5:
            self._compare(c, cam, t, (split - 0.5) * 2 * alpha)
        for t0, t1 in self.tags:
            if t0 <= vt < t1:
                k = min(1.0, (vt - t0) / 0.5, (t1 - vt) / 0.5) * alpha
                self._speeds(c, cam, rec, t, ox, oy, k)

    def _speeds(self, c, cam, rec, t, ox, oy, a):
        """Velocità dell'eroe e della coda accanto, in piccolo vicino alle macchine."""
        from . import gfx
        from .gfx import INK, draw_text
        st = self.recs[rec].frame(t)
        ids, x, lat, v = st[:4]
        k = np.nonzero(ids == self.recs[rec].hero)[0]
        if not len(k):
            return
        k = k[0]
        near = np.nonzero((lat > 1.7) & (np.abs(x - x[k]) < 25))[0]
        f, fs = gfx.mono(40, "Medium"), gfx.mono(22)
        mph = 2.23694 if self.units == "imperial" else 3.6
        unit = "MPH" if self.units == "imperial" else "KM/H"
        hx, hy = cam.to_screen(ox + lat[k] - 2.4, oy + x[k] - 1)
        draw_text(c, f"{v[k] * mph:.0f}", f, hx - 30, hy, color=(255, 255, 255), alpha=a, align="right")
        draw_text(c, unit, fs, hx - 30, hy + 28, color=INK, alpha=0.8 * a, align="right", tracking=1)
        if len(near):
            q = near[np.argmin(np.abs(x[near] - x[k]))]
            qx, qy = cam.to_screen(ox + lat[q] + 2.4, oy + x[q] - 1)
            draw_text(c, f"{v[q] * mph:.0f}", f, qx + 30, qy, color=(255, 255, 255), alpha=a, align="left")
            draw_text(c, unit, fs, qx + 30, qy + 28, color=INK, alpha=0.8 * a, align="left", tracking=1)

    def _compare(self, c, cam, t, a):
        """Confronto affiancato: etichetta sopra ogni strada e graffa lungo la coda con la lunghezza."""
        from . import gfx
        from .gfx import INK, draw_text
        from .whatif import AMBER, fmt_dist
        f, fb = gfx.mono(26, "Medium"), gfx.mono(34, "SemiBold")
        for (name, label), side in zip(zip(("A", "B"), self.labels), (-1, 1)):
            q = self.recs[name].backup_at(t)
            dx = side * SPLIT_D
            top = cam.to_screen(dx, X_END)
            bot = cam.to_screen(dx, X_END - q)
            lw = gfx.text_width(label, f, 1.5)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(top[0] - lw / 2 - 12, top[1] - 82, top[0] + lw / 2 + 12, top[1] - 38),
                                              6, 6), skia.Paint(AntiAlias=True, Color=rgba((14, 16, 19), 0.92 * a)))
            draw_text(c, label, f, top[0], top[1] - 60, color=INK, alpha=a, tracking=1.5, vcenter=True)
            bx = top[0] + side * 46
            p = skia.Paint(AntiAlias=True, StrokeWidth=2.2, Color=rgba(AMBER, a))
            c.drawLine(bx, top[1], bx, bot[1], p)
            c.drawLine(bx, top[1], bx - side * 14, top[1], p)
            c.drawLine(bx, bot[1], bx - side * 14, bot[1], p)
            draw_text(c, fmt_dist(q, self.units), fb, bx + side * 16, (top[1] + bot[1]) / 2, color=AMBER, alpha=a,
                      align="left" if side > 0 else "right", vcenter=True)
