"""Helper grafici su skia: font, colori, testo."""

from functools import lru_cache
from pathlib import Path

import skia

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


@lru_cache(maxsize=None)
def typeface(name):
    return skia.Typeface.MakeFromFile(str(FONT_DIR / name))


def display(size):
    """Titoli, banner, numeri."""
    return _font("Anton-Regular.ttf", size)


def label(size):
    """Testo piccolo."""
    return _font("Montserrat-ExtraBold.ttf", size)


def glyph(size):
    """Simboli (zodiaco ecc.)."""
    return _font("DejaVuSans-Bold.ttf", size)


@lru_cache(maxsize=None)
def _font(name, size):
    f = skia.Font(typeface(name), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def rgba(c, a=1.0):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(max(0, min(1, a)) * 255))


def mix(c1, c2, k):
    return tuple(c1[i] + (c2[i] - c1[i]) * k for i in range(3))


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def fit_font(maker, text, max_w, size):
    while size > 10 and maker(size).measureText(text) > max_w:
        size -= 2
    return maker(size)


def draw_text(canvas, text, font, x, y, color=WHITE, alpha=1.0, align="center",
              stroke=None, stroke_w=0.0, stroke_alpha=1.0, vcenter=False):
    """Disegna testo; y è la baseline, o il centro se vcenter."""
    if not text or alpha <= 0:
        return
    w = font.measureText(text)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    if vcenter:
        m = font.getMetrics()
        y -= (m.fAscent + m.fDescent) / 2
    blob = skia.TextBlob.MakeFromString(text, font)
    if stroke is not None and stroke_w > 0:
        p = skia.Paint(AntiAlias=True, Color=rgba(stroke, alpha * stroke_alpha),
                       Style=skia.Paint.kStroke_Style, StrokeWidth=stroke_w,
                       StrokeJoin=skia.Paint.kRound_Join)
        canvas.drawTextBlob(blob, x, y, p)
    canvas.drawTextBlob(blob, x, y, skia.Paint(AntiAlias=True, Color=rgba(color, alpha)))


def ease_out_back(k, s=1.7):
    k = max(0.0, min(1.0, k)) - 1
    return 1 + (s + 1) * k ** 3 + s * k ** 2


def ease_in_out(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def ease_out(k):
    k = max(0.0, min(1.0, k))
    return 1 - (1 - k) ** 3
