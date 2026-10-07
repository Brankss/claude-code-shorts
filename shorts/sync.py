"""Sync: pallini su orbite concentriche a velocità diverse; ogni colpo suona una nota.

L'orbita i compie (C0 + i) cicli in TOTAL secondi, quindi all'inizio e alla fine sono
tutti allineati: il loop è perfetto e il riallineamento finale è il payoff.
Due varianti che si alternano: archi (vanno e vengono su semicerchi) e anelli (girano in tondo).
"""

import math
from dataclasses import dataclass

import numpy as np
import skia

from . import audio as A
from . import gfx
from .base import FPS, TOTAL, W, BaseRenderer
from .gfx import INK, WHITE, draw_text, mix, rgba
from .themes import _hex

PALETTES = [
    ("#4FC8F5", "#A66CFF"), ("#21D4B4", "#FFD23F"), ("#FF5A50", "#FFD23F"),
    ("#FF74B6", "#3F82FF"), ("#43C463", "#4FC8F5"), ("#FF953A", "#FF74B6"),
]
SCALES = {
    "major pentatonic": [0, 2, 4, 7, 9],
    "minor pentatonic": [0, 3, 5, 7, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
}
CX, CY = 540.0, 1130.0
# Il video non parte dall'allineamento (il momento più piatto) ma da un pattern già sparpagliato:
# l'allineamento arriva a SYNC_AT secondi. Il periodo resta TOTAL, quindi il loop è sempre perfetto.
SYNC_AT = 20.0
OFFSET = TOTAL - SYNC_AT


def cycle_time(vt):
    """Tempo nel ciclo dell'animazione (0 = tutti allineati) per un istante del video."""
    return (vt + OFFSET) % TOTAL
R_MIN, R_MAX = 70.0, 470.0


@dataclass
class Params:
    variant: str      # "arcs" | "rings"
    n: int
    c0: int
    palette: tuple
    scale: str
    root: int         # nota MIDI più grave

    @property
    def cycles(self):
        return [self.c0 + i for i in range(self.n)]

    def colors(self):
        a, b = _hex(self.palette[0]), _hex(self.palette[1])
        return [mix(a, b, i / max(1, self.n - 1)) for i in range(self.n)]

    def notes(self):
        sc = SCALES[self.scale]
        return [self.root + 12 * (i // len(sc)) + sc[i % len(sc)] for i in range(self.n)]

    def radius(self, i):
        return R_MIN + (R_MAX - R_MIN) * i / max(1, self.n - 1)


def params(episode):
    rng = np.random.default_rng(episode * 7919)
    variant = "arcs" if episode % 2 else "rings"
    return Params(
        variant=variant,
        n=int(rng.choice([12, 14, 16])),
        c0=int(rng.choice([3, 4, 5])) if variant == "arcs" else int(rng.choice([6, 7, 8])),
        palette=PALETTES[int(rng.integers(len(PALETTES)))],
        scale=str(rng.choice(list(SCALES))),
        root=int(rng.choice([45, 48, 50])),
    )


def angle(p, i, t):
    """Posizione angolare del pallino i al tempo t (radianti, 0 = destra, antiorario verso l'alto)."""
    ph = (t * p.cycles[i] / TOTAL) % 1.0
    if p.variant == "arcs":
        tri = 1 - abs(1 - 2 * ph)          # 0 -> 1 -> 0: da sinistra a destra e ritorno
        return math.pi * (1 - tri)
    return math.pi / 2 - 2 * math.pi * ph  # parte in alto e gira in senso orario


def hits(p):
    """Tutti i colpi (tempo, orbita) in [0, TOTAL): estremi degli archi o passaggio in cima agli anelli."""
    out = []
    for i, cyc in enumerate(p.cycles):
        per = 2 if p.variant == "arcs" else 1
        for k in range(cyc * per):
            out.append((k * TOTAL / (cyc * per), i))
    out.sort()
    return out


class Renderer(BaseRenderer):
    def __init__(self, p, title_lines, subtitle):
        super().__init__(title_lines, subtitle)
        self.p = p
        self.colors = p.colors()
        self.hits = hits(p)
        self.hit_t = np.array([h[0] for h in self.hits])

    def _last_hit(self, t):
        """Per ogni orbita: da quanto tempo ha colpito l'ultima volta (con il wrap del loop)."""
        age = np.full(self.p.n, 99.0)
        lo = np.searchsorted(self.hit_t, t - 1.0)
        hi = np.searchsorted(self.hit_t, t, side="right")
        for k in range(lo, hi):
            ht, i = self.hits[k]
            age[i] = min(age[i], t - ht)
        if t < 1.0:  # i colpi a fine video "continuano" nel loop
            for k in range(np.searchsorted(self.hit_t, TOTAL - 1.0 + t), len(self.hits)):
                ht, i = self.hits[k]
                age[i] = min(age[i], t + TOTAL - ht)
        return age

    def draw(self, c, f, vt):
        p = self.p
        tau = cycle_time(vt)
        age = self._last_hit(tau)
        glow = np.exp(-age / 0.35)
        if p.variant == "arcs":
            self._arcs(c, tau, glow)
        else:
            self._rings(c, tau, glow)
        self._hud(c, vt)

    def _arcs(self, c, t, glow):
        p = self.p
        c.drawLine(CX - R_MAX - 30, CY, CX + R_MAX + 30, CY,
                   skia.Paint(AntiAlias=True, StrokeWidth=2, Color=rgba(INK, 0.3)))
        for i in range(p.n):
            r, col = p.radius(i), self.colors[i]
            rect = skia.Rect(CX - r, CY - r, CX + r, CY + r)
            for sign, base in ((1, 1.0), (-1, 0.3)):  # arco e riflesso
                c.drawArc(rect, 180 if sign > 0 else 0, 180, False, skia.Paint(
                    AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4,
                    Color=rgba(mix(col, WHITE, 0.3 * glow[i]), (0.38 + 0.55 * glow[i]) * base)))
            a = angle(p, i, t)
            x, y = CX + r * math.cos(a), CY - r * math.sin(a)
            c.drawCircle(x, y, 15, skia.Paint(AntiAlias=True, Color=rgba(col)))
            c.drawCircle(x, 2 * CY - y, 15, skia.Paint(AntiAlias=True, Color=rgba(col, 0.3)))
            for ex in (CX - r, CX + r):
                c.drawCircle(ex, CY, 4 + 3 * glow[i], skia.Paint(AntiAlias=True, Color=rgba(col, 0.35 + 0.6 * glow[i])))

    def _rings(self, c, t, glow):
        p = self.p
        cy = CY - 130
        c.drawLine(CX, cy - R_MAX - 30, CX, cy - R_MIN + 30,
                   skia.Paint(AntiAlias=True, StrokeWidth=2, Color=rgba(INK, 0.3)))
        for i in range(p.n):
            r, col = p.radius(i), self.colors[i]
            c.drawCircle(CX, cy, r, skia.Paint(
                AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4,
                Color=rgba(mix(col, WHITE, 0.3 * glow[i]), 0.34 + 0.55 * glow[i])))
            a = angle(p, i, t)
            c.drawCircle(CX + r * math.cos(a), cy - r * math.sin(a), 15, skia.Paint(AntiAlias=True, Color=rgba(col)))

    def _hud(self, c, vt):
        k = self.header(c, vt)
        if k <= 0:
            return
        # Tempo al prossimo allineamento: a SYNC_AT nel video, poi di nuovo dopo il loop.
        left = (SYNC_AT - vt) % TOTAL
        y = 330
        if abs(vt - SYNC_AT) < 1.2:
            s = "Sync"
        else:
            s = f"Next sync in 0:{int(math.ceil(left)):02d}"
        draw_text(c, s, gfx.text(34), W / 2, y, color=INK, alpha=0.75 * k)
        # Linea di avanzamento sottile verso il sync.
        bx, bw = 290.0, 500.0
        c.drawLine(bx, y + 34, bx + bw, y + 34, skia.Paint(AntiAlias=True, StrokeWidth=3, Color=rgba(INK, 0.12 * k)))
        c.drawLine(bx, y + 34, bx + bw * (1 - left / TOTAL), y + 34,
                   skia.Paint(AntiAlias=True, StrokeWidth=3, Color=rgba(self.colors[-1], 0.9 * k)))


def build_audio(p):
    mx = A.Mixer(TOTAL)
    notes = p.notes()
    gain = 0.5 / math.sqrt(p.n)
    for tau, i in hits(p):
        t = (tau - OFFSET) % TOTAL
        pan = (p.radius(i) / R_MAX) * (0.5 if (i % 2) else -0.5)
        mx.add(t, A.kalimba(A.note(notes[i] + 12)), gain, pan=pan, reverb=0.5)
    # Bordone molto basso sulla tonica, per tutto il video.
    # La coda del rilascio rientra all'inizio (loop_tail) e fa da dissolvenza con l'attacco.
    mx.add(0.0, A.pad([A.note(p.root - 12), A.note(p.root - 5)], TOTAL - 0.5, attack=1.0, release=1.5,
                      cutoff=600), 0.35, reverb=0.2)
    return mx.master()
