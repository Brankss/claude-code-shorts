"""Didascalie cinetiche ed effetti di montaggio, per i format che devono tenere incollati allo schermo.

Didascalie: parola per parola, ognuna entra con un piccolo "pop"; le parole tra *asterischi* sono
evidenziate (colore d'accento e riquadro). Font pesante con contorno scuro: si legge su qualunque sfondo.

Effetti: punch-in (zoom di colpo che si assesta), shake, flash bianco, flash di colore. Ogni effetto è
una funzione del tempo trascorso dall'evento, così il render resta senza stato tra un frame e l'altro.
"""

import math
from dataclasses import dataclass

import numpy as np
import skia

from . import gfx
from .gfx import rgba


def heavy(size):
    """Montserrat Black: per le didascalie grandi."""
    return gfx._font("Montserrat-Black.woff", size)


def bold(size):
    """Montserrat ExtraBold: per i sottotitoli e le etichette."""
    return gfx._font("Montserrat-ExtraBold.woff", size)


def back_out(k, s=1.9):
    """Easing con un leggero rimbalzo oltre il valore finale."""
    k = max(0.0, min(1.0, k)) - 1
    return k * k * ((s + 1) * k + s) + 1


@dataclass
class Word:
    text: str
    hot: bool     # evidenziata
    t: float      # quando entra (s dall'inizio della didascalia)


def words(text, per_word=0.11):
    """Parole con tempi d'entrata; *così* o *anche più parole* = evidenziate."""
    out, inside = [], False
    for i, w in enumerate(text.split()):
        opens = w.startswith("*")
        closes = w.rstrip(".,!?:;'\"").endswith("*")
        hot = inside or opens
        if opens:
            inside = True
        if closes:
            inside = False
        out.append(Word(w.replace("*", ""), hot, i * per_word))
    return out


def layout(ws, font, max_w, space):
    """Righe bilanciate: [(parole, larghezza)]."""
    lines, cur, cw = [], [], 0.0
    for w in ws:
        ww = font.measureText(w.text)
        if cur and cw + space + ww > max_w:
            lines.append((cur, cw))
            cur, cw = [], 0.0
        cw += (space if cur else 0) + ww
        cur.append(w)
    if cur:
        lines.append((cur, cw))
    return lines


def caption(c, text, age, x, y, size=84, max_w=940, accent=(255, 214, 10), color=(255, 255, 255),
            per_word=0.11, alpha=1.0, upper=True, hot_box=True):
    """Disegna una didascalia cinetica centrata su x, con la prima riga a y. age = secondi da quando è iniziata."""
    if alpha <= 0 or age < 0:
        return y
    font = heavy(size)
    ws = words(text.upper() if upper else text, per_word)
    space = font.measureText(" ")
    lh = size * 1.12
    stroke = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=size * 0.16,
                        StrokeJoin=skia.Paint.kRound_Join, Color=rgba((0, 0, 0), 0.92 * alpha))
    shadow = skia.Paint(AntiAlias=True, Color=rgba((0, 0, 0), 0.55 * alpha),
                        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.12))
    yy = y
    for line, lw in layout(ws, font, max_w, space):
        cx = x - lw / 2
        for w in line:
            ww = font.measureText(w.text)
            k = (age - w.t) / 0.22
            if k > 0:
                s = 0.55 + 0.45 * back_out(k)
                a = min(1.0, k * 2.5) * alpha
                c.save()
                c.translate(cx + ww / 2, yy - size * 0.35)
                c.scale(s, s)
                c.translate(-(cx + ww / 2), -(yy - size * 0.35))
                if w.hot and hot_box:
                    pad = size * 0.12
                    box = skia.RRect.MakeRectXY(skia.Rect(cx - pad, yy - size * 0.82, cx + ww + pad, yy + size * 0.16),
                                                size * 0.14, size * 0.14)
                    c.drawRRect(box, skia.Paint(AntiAlias=True, Color=rgba(accent, a)))
                    c.drawString(w.text, cx, yy, font, skia.Paint(AntiAlias=True, Color=rgba((0, 0, 0), a)))
                else:
                    c.drawString(w.text, cx + size * 0.03, yy + size * 0.06, font, shadow)
                    c.drawString(w.text, cx, yy, font, stroke)
                    c.drawString(w.text, cx, yy, font,
                                 skia.Paint(AntiAlias=True, Color=rgba(accent if w.hot else color, a)))
                c.restore()
            cx += ww + space
        yy += lh
    return yy


def duration(text, per_word=0.11):
    """Secondi perché l'ultima parola sia entrata."""
    return len(text.split()) * per_word + 0.22


# ---------- effetti di montaggio ----------

def punch(age, amount=0.08, decay=7.0):
    """Fattore di zoom per un punch-in avvenuto age secondi fa (1 = niente)."""
    if age < 0:
        return 1.0
    return 1.0 + amount * math.exp(-age * decay) * (1 if age > 0.02 else age / 0.02)


def shake(age, amount=18.0, decay=8.0, seed=0):
    """Spostamento (dx, dy) in pixel per uno scossone avvenuto age secondi fa."""
    if age < 0 or age > 1.5:
        return 0.0, 0.0
    e = amount * math.exp(-age * decay)
    return (e * math.sin(age * 71 + seed * 1.7), e * math.cos(age * 53 + seed * 2.3))


def flash(c, age, color=(255, 255, 255), strength=0.85, decay=9.0, w=1080, h=1920):
    if 0 <= age < 0.6:
        c.drawRect(skia.Rect(0, 0, w, h), skia.Paint(Color=rgba(color, strength * math.exp(-age * decay))))


def around(c, cx, cy, zoom=1.0, dx=0.0, dy=0.0):
    """Applica punch e shake al canvas (da chiamare dopo save, prima di disegnare la scena)."""
    c.translate(cx + dx, cy + dy)
    c.scale(zoom, zoom)
    c.translate(-cx, -cy)


def last_event(times, t):
    """Secondi dall'ultimo evento in times (ordinati) prima di t; inf se nessuno."""
    i = int(np.searchsorted(times, t, side="right")) - 1
    return t - times[i] if i >= 0 else math.inf
