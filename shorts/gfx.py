"""Helper grafici su skia: font, colori, testo, easing."""

from functools import lru_cache
from pathlib import Path

import skia

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


@lru_cache(maxsize=None)
def typeface(name):
    return skia.Typeface.MakeFromFile(str(FONT_DIR / name))


def title(size):
    """Titoli e nomi."""
    return _font("Montserrat-SemiBold.ttf", size)


def text(size):
    """Testo di servizio."""
    return _font("Montserrat-Medium.ttf", size)


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
BG = (17, 17, 21)
INK = (236, 236, 240)


def fit_font(maker, s, max_w, size):
    while size > 10 and maker(size).measureText(s) > max_w:
        size -= 2
    return maker(size)


def text_width(s, font, tracking=0.0):
    return font.measureText(s) + tracking * max(0, len(s) - 1)


def draw_text(canvas, s, font, x, y, color=WHITE, alpha=1.0, align="center", vcenter=False, tracking=0.0):
    """Disegna testo; y è la baseline, o il centro se vcenter. tracking = spaziatura extra tra lettere."""
    if not s or alpha <= 0:
        return
    w = text_width(s, font, tracking)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    if vcenter:
        m = font.getMetrics()
        y -= (m.fAscent + m.fDescent) / 2
    paint = skia.Paint(AntiAlias=True, Color=rgba(color, alpha))
    if not tracking:
        canvas.drawTextBlob(skia.TextBlob.MakeFromString(s, font), x, y, paint)
        return
    for ch in s:
        canvas.drawTextBlob(skia.TextBlob.MakeFromString(ch, font), x, y, paint)
        x += font.measureText(ch) + tracking


def ease_in_out(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def ease_out(k):
    k = max(0.0, min(1.0, k))
    return 1 - (1 - k) ** 3


def fade(a, fade_in, hold, fade_out):
    """Opacità di un elemento che compare, resta e sparisce (a = secondi da quando compare)."""
    if a < 0 or a > fade_in + hold + fade_out:
        return 0.0
    if a < fade_in:
        return ease_in_out(a / fade_in)
    if a < fade_in + hold:
        return 1.0
    return 1.0 - ease_in_out((a - fade_in - hold) / fade_out)
