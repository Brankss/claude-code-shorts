"""Parti comuni a tutti i format: canvas, hook iniziale, header, loop finale."""

import numpy as np
import skia

from . import gfx
from .gfx import BG, INK, draw_text, ease_in_out, rgba

W, H = 1080, 1920
FPS = 60
TOTAL = 40.0
HOOK_END = 1.8     # la domanda grande resta ~1s, poi lascia il posto all'header
LOOP_FADE = 0.45   # dissolvenza finale sul primo frame: il loop non ha stacchi
WORLD_TOP = 404    # sopra questa riga c'è solo l'HUD


class BaseRenderer:
    n_frames = int(TOTAL * FPS)

    def __init__(self, title_lines, subtitle):
        self.title_lines = title_lines
        self.subtitle = subtitle
        self.buf = np.zeros((H, W, 4), np.uint8)
        self.surface = skia.Surface(self.buf)
        self.frame0 = None

    def draw(self, c, f, vt):
        raise NotImplementedError

    def render(self, f):
        c = self.surface.getCanvas()
        vt = f / FPS
        c.clear(rgba(BG))
        self.draw(c, f, vt)
        self._hook(c, vt)
        if self.frame0 is not None and vt > TOTAL - LOOP_FADE:
            k = ease_in_out((vt - (TOTAL - LOOP_FADE)) / LOOP_FADE)
            c.drawImage(self.frame0, 0, 0, skia.SamplingOptions(), skia.Paint(Alphaf=k))
        if f == 0:
            self.frame0 = skia.Image.fromarray(self.buf.copy())
        return self.buf

    def header_alpha(self, vt):
        return ease_in_out((vt - (HOOK_END - 0.4)) / 0.4)

    def header(self, c, vt):
        k = self.header_alpha(vt)
        if k > 0:
            draw_text(c, " ".join(self.title_lines), gfx.fit_font(gfx.title, " ".join(self.title_lines), 960, 50),
                      W / 2, 196, color=INK, alpha=k)
            draw_text(c, self.subtitle, gfx.text(28), W / 2, 246, color=INK, alpha=0.5 * k)
        return k

    def _hook(self, c, vt):
        """Primi frame: la domanda grande nello spazio in alto, poi dissolve nell'header."""
        if vt >= HOOK_END:
            return
        al = 1 - ease_in_out((vt - (HOOK_END - 0.8)) / 0.4)
        if al <= 0:
            return
        l1, l2 = self.title_lines
        f = gfx.fit_font(gfx.title, max(l1, l2, key=len), 980, 92)
        draw_text(c, l1, f, W / 2, 262, color=INK, alpha=al)
        draw_text(c, l2, f, W / 2, 372, color=INK, alpha=al)
        draw_text(c, self.subtitle, gfx.text(32), W / 2, 450, color=INK, alpha=0.6 * al)
