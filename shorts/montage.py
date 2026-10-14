"""Montaggio a inquadrature: tagli frequenti, transizioni, punch-in, didascalie cinetiche sopra a tutto.

Un video è una lista di Shot (inquadrature) che si susseguono, più una traccia di didascalie e di
eventi (punch, shake, flash) indipendente dai tagli. Ogni shot sa disegnarsi dato il suo tempo locale:
il render di un frame non dipende dai frame precedenti, quindi si può renderizzare in parallelo.

Transizioni d'ingresso di uno shot:
- cut:    taglio secco
- flash:  taglio con lampo bianco
- whip:   l'inquadratura precedente scappa di lato con scia, la nuova entra
- zoom:   la nuova entra da più vicino e si assesta
- glitch: due-tre frame con i canali di colore sfasati
"""

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import skia

from . import kinetic as K
from .base import FPS, H, W
from .gfx import ease_in_out, ease_out, rgba

TRANS = {"cut": 0.0, "flash": 0.0, "whip": 0.22, "zoom": 0.35, "glitch": 0.12}


@dataclass
class Shot:
    t0: float
    t1: float
    draw: Callable            # draw(canvas, t_locale, progresso 0..1, t_video)
    enter: str = "cut"


@dataclass
class Caption:
    t0: float
    t1: float
    text: str
    y: float = 620
    size: int = 84
    accent: tuple = (255, 214, 10)
    per_word: float = 0.11
    sub: str = None


@dataclass
class Event:
    t: float
    kind: str                 # punch | shake | flash | redflash
    amount: float = 1.0


@dataclass
class Montage:
    duration: float
    shots: list
    captions: list = field(default_factory=list)
    events: list = field(default_factory=list)
    overlay: Callable = None  # overlay(canvas, t_video): HUD, barra di avanzamento... sopra la scena, sotto le didascalie
    loop_fade: float = 0.4

    def __post_init__(self):
        self.shots.sort(key=lambda s: s.t0)
        self.n_frames = int(self.duration * FPS)
        self.buf = np.zeros((H, W, 4), np.uint8)
        self.surface = skia.Surface(self.buf)
        self.aux = skia.Surface(W, H)
        self.frame0 = None
        self._ev = {}
        for k in ("punch", "shake", "flash", "redflash"):
            ev = sorted((e.t, e.amount) for e in self.events if e.kind == k)
            self._ev[k] = (np.array([e[0] for e in ev]), np.array([e[1] for e in ev]))

    def shot_at(self, t):
        cur = None
        for i, s in enumerate(self.shots):
            if s.t0 <= t:
                cur = i
        return cur

    def _draw_shot(self, c, i, t):
        s = self.shots[i]
        lt = t - s.t0
        s.draw(c, lt, min(1.0, max(0.0, lt / max(1e-6, s.t1 - s.t0))), t)

    def _event_age(self, kind, t):
        return K.last_event(self._ev[kind][0], t)

    def _amount(self, kind, t):
        """Intensità dell'ultimo evento di quel tipo prima di t."""
        ts, amt = self._ev[kind]
        j = int(np.searchsorted(ts, t, side="right")) - 1
        return float(amt[j]) if j >= 0 else 1.0

    def render(self, f):
        t = f / FPS
        c = self.surface.getCanvas()
        c.clear(rgba((0, 0, 0)))
        i = self.shot_at(t)
        s = self.shots[i]
        age_in = t - s.t0
        dur = TRANS.get(s.enter, 0.0)

        # Punch e shake applicati a tutta la scena (non alle didascalie).
        pa = self._event_age("punch", t)
        sa = self._event_age("shake", t)
        zoom = K.punch(pa, 0.07 * self._amount("punch", t))
        dx, dy = K.shake(sa, 16 * self._amount("shake", t), seed=int(t * 7))
        if s.enter == "zoom" and age_in < dur:
            zoom *= 1 + 0.25 * (1 - ease_out(age_in / dur))

        c.save()
        K.around(c, W / 2, H / 2, zoom, dx, dy)
        if s.enter == "whip" and age_in < dur and i > 0:
            self._whip(c, i, t, age_in / dur)
        else:
            self._draw_shot(c, i, t)
        c.restore()

        if s.enter == "glitch" and age_in < dur:
            self._glitch(c, age_in / dur)
        if s.enter == "flash":
            K.flash(c, age_in, strength=0.75)
        K.flash(c, self._event_age("flash", t), strength=0.8)
        K.flash(c, self._event_age("redflash", t), color=(255, 40, 40), strength=0.45, decay=5)

        if self.overlay:
            self.overlay(c, t)
        for cap in self.captions:
            if cap.t0 <= t < cap.t1:
                out = 1 - ease_in_out((t - (cap.t1 - 0.15)) / 0.15)
                y = K.caption(c, cap.text, t - cap.t0, W / 2, cap.y, size=cap.size, accent=cap.accent,
                              per_word=cap.per_word, alpha=out)
                if cap.sub:
                    ka = ease_in_out((t - cap.t0 - K.duration(cap.text, cap.per_word)) / 0.3) * out
                    K.caption(c, cap.sub, 99, W / 2, y + 10, size=int(cap.size * 0.55), alpha=ka, upper=False)

        if self.frame0 is not None and t > self.duration - self.loop_fade:
            k = ease_in_out((t - (self.duration - self.loop_fade)) / self.loop_fade)
            c.drawImage(self.frame0, 0, 0, skia.SamplingOptions(), skia.Paint(Alphaf=k))
        if f == 0:
            self.frame0 = skia.Image.fromarray(self.buf.copy())
        return self.buf

    def _whip(self, c, i, t, k):
        """Lo shot precedente scappa a sinistra con scia, il nuovo arriva da destra."""
        e = ease_in_out(k)
        ac = self.aux.getCanvas()
        ac.clear(rgba((0, 0, 0)))
        self._draw_shot(ac, i - 1, self.shots[i].t0 - 1e-3)
        old = self.aux.makeImageSnapshot()
        ac.clear(rgba((0, 0, 0)))
        self._draw_shot(ac, i, t)
        new = self.aux.makeImageSnapshot()
        off = e * W
        for j in range(5):  # scia: copie sfalsate e trasparenti
            a = 0.35 if j else 1.0
            c.drawImage(old, -off - j * 40 * math.sin(math.pi * k), 0, skia.SamplingOptions(), skia.Paint(Alphaf=a))
            c.drawImage(new, W - off + j * 40 * math.sin(math.pi * k), 0, skia.SamplingOptions(), skia.Paint(Alphaf=a))

    def _glitch(self, c, k):
        """Canali R e B sfalsati (ricomposti senza schiarire) e qualche fascia spostata."""
        snap = self.surface.makeImageSnapshot()
        amt = 26 * (1 - k)
        ac = self.aux.getCanvas()
        ac.clear(rgba((0, 0, 0)))
        for ch, ox in ((0, -amt), (1, 0.0), (2, amt)):
            mat = [0.0] * 20
            mat[ch * 5 + ch] = 1.0
            mat[18] = 1.0
            ac.drawImage(snap, ox, 0, skia.SamplingOptions(), skia.Paint(
                ColorFilter=skia.ColorFilters.Matrix(mat), BlendMode=skia.BlendMode.kPlus))
        comp = self.aux.makeImageSnapshot()
        c.drawImage(comp, 0, 0)
        rng = np.random.default_rng(int(k * 100))
        for _ in range(5):
            y = float(rng.uniform(0, H))
            hgt = float(rng.uniform(10, 60))
            c.save()
            c.clipRect(skia.Rect(0, y, W, y + hgt))
            c.drawImage(comp, float(rng.uniform(-60, 60)), 0)
            c.restore()
