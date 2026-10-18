"""Pezzi di scenografia piatta per il format "rules": stanze viste di lato, finestre, porte, mobili,
skyline, luce e buio, torcia, telefono (lock screen, allerta, chat), spioncino.

Tutto in pixel dello spazio 1080x1920, colori pieni con sfumature morbide e luci in kPlus: lo stile
delle illustrazioni vettoriali "cinematografiche" dei video di riferimento.
"""

import math

import numpy as np
import skia

from . import gfx
from . import kinetic as K
from .gfx import mix, rgba

W, H = 1080, 1920


def P(col, a=1.0, **kw):
    return skia.Paint(AntiAlias=True, Color=rgba(col, a), **kw)


def rect(c, x0, y0, x1, y1, col, a=1.0):
    c.drawRect(skia.Rect(x0, y0, x1, y1), P(col, a))


def rrect(c, x0, y0, x1, y1, r, col, a=1.0):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r), P(col, a))


def vgrad(c, x0, y0, x1, y1, top, bottom, a=1.0, stops=None):
    cols = [rgba(top, a), rgba(bottom, a)] if not isinstance(top, list) else [rgba(k, a) for k in top]
    sh = skia.GradientShader.MakeLinear([(x0, y0), (x0, y1)], cols, stops)
    c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(AntiAlias=True, Shader=sh))


def glow(c, x, y, r, col, a, plus=True):
    sh = skia.GradientShader.MakeRadial((x, y), r, [rgba(col, a), rgba(col, a * 0.3), rgba(col, 0)], [0, 0.4, 1])
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=sh, BlendMode=skia.BlendMode.kPlus if plus else skia.BlendMode.kSrcOver))


def text(c, s, x, y, font, col, a=1.0, align="left"):
    gfx.draw_text(c, s, font, x, y, color=col, alpha=a, align=align)


# ---------- stanza ----------

def room(c, wall, floor, horizon=1260, plank=None, base=None, ceiling=None):
    """Interno visto di lato: parete di fondo, battiscopa, pavimento in prospettiva con assi."""
    vgrad(c, 0, 0, W, horizon, mix(wall, (0, 0, 0), 0.25), wall)
    if ceiling:
        vgrad(c, 0, 0, W, 160, ceiling, wall, a=0.9)
    rect(c, 0, horizon - 22, W, horizon, base or mix(wall, (0, 0, 0), 0.35))
    vgrad(c, 0, horizon, W, H, mix(floor, (255, 255, 255), 0.04), mix(floor, (0, 0, 0), 0.35))
    line = P(plank or mix(floor, (0, 0, 0), 0.22), 0.7, StrokeWidth=3)
    vx = W / 2
    for i in range(-9, 10):
        x = vx + i * 150
        c.drawLine(vx + i * 60, horizon, x * 1.0 + i * 260, H, line)
    for j in range(1, 6):
        y = horizon + (H - horizon) * (j / 6) ** 1.6
        c.drawLine(0, y, W, y, P(mix(floor, (0, 0, 0), 0.18), 0.35, StrokeWidth=2))


def window(c, x0, y0, x1, y1, view, frame=(52, 46, 46), bars=(2, 2), curtains=None, sill=True):
    """Finestra con vista: view(c, rect) disegna fuori, clippato nel vetro."""
    rect(c, x0 - 16, y0 - 16, x1 + 16, y1 + 16, frame)
    c.save()
    c.clipRect(skia.Rect(x0, y0, x1, y1))
    view(c, (x0, y0, x1, y1))
    sh = skia.GradientShader.MakeLinear([(x0, y0), (x1, y1)], [rgba((255, 255, 255), 0.07), rgba((255, 255, 255), 0)])
    c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=sh))
    c.restore()
    nx, ny = bars
    for i in range(1, nx):
        x = x0 + (x1 - x0) * i / nx
        rect(c, x - 6, y0, x + 6, y1, frame)
    for j in range(1, ny):
        y = y0 + (y1 - y0) * j / ny
        rect(c, x0, y - 6, x1, y + 6, frame)
    if sill:
        rect(c, x0 - 30, y1 + 10, x1 + 30, y1 + 30, mix(frame, (255, 255, 255), 0.1))
    if curtains:
        for side in (-1, 1):
            cx0 = x0 - 70 if side < 0 else x1 - 10
            cx1 = x0 + 10 if side < 0 else x1 + 70
            rect(c, cx0, y0 - 40, cx1, y1 + 70, curtains)
            for k in range(3):
                xx = cx0 + (cx1 - cx0) * (k + 0.5) / 3
                c.drawLine(xx, y0 - 40, xx, y1 + 70, P(mix(curtains, (0, 0, 0), 0.3), 0.6, StrokeWidth=4))
        rect(c, x0 - 90, y0 - 52, x1 + 90, y0 - 38, mix(frame, (0, 0, 0), 0.3))


def door(c, x0, y0, x1, y1, col=(98, 58, 40), frame=(70, 66, 70), light_under=0.0, peephole=True, chain=False,
         open_k=0.0, knob_side=1):
    rect(c, x0 - 22, y0 - 22, x1 + 22, y1, frame)
    rect(c, x0, y0, x1, y1, (14, 12, 12))
    if light_under > 0:
        glow(c, (x0 + x1) / 2, y1, (x1 - x0) * 0.9, (255, 210, 150), 0.35 * light_under)
        rect(c, x0, y1 - 5, x1, y1, (255, 220, 170), 0.8 * light_under)
    w = (x1 - x0) * (1 - 0.85 * open_k)
    dx0, dx1 = (x0, x0 + w) if knob_side > 0 else (x1 - w, x1)
    rect(c, dx0, y0, dx1, y1, col)
    shade = mix(col, (0, 0, 0), 0.18)
    for (a, b) in ((0.12, 0.45), (0.55, 0.9)):
        rect(c, dx0 + w * 0.14, y0 + (y1 - y0) * a, dx1 - w * 0.14, y0 + (y1 - y0) * b, shade)
        rect(c, dx0 + w * 0.17, y0 + (y1 - y0) * a + 8, dx1 - w * 0.17, y0 + (y1 - y0) * b - 8, mix(col, (255, 255, 255), 0.03))
    kx = dx1 - w * 0.13 if knob_side > 0 else dx0 + w * 0.13
    c.drawCircle(kx, y0 + (y1 - y0) * 0.52, 13, P((200, 170, 90)))
    rect(c, kx - 30 * knob_side, y0 + (y1 - y0) * 0.5, kx, y0 + (y1 - y0) * 0.5 + 9, (200, 170, 90))
    if peephole:
        c.drawCircle((dx0 + dx1) / 2, y0 + (y1 - y0) * 0.27, 7, P((30, 26, 24)))
        c.drawCircle((dx0 + dx1) / 2, y0 + (y1 - y0) * 0.27, 3.5, P((180, 160, 120)))
    if chain:
        p = skia.Path()
        cy = y0 + (y1 - y0) * 0.4
        p.moveTo(kx - 10 * knob_side, cy)
        p.quadTo(kx + 40 * knob_side, cy + 30, kx + 70 * knob_side, cy - 4)
        c.drawPath(p, P((190, 190, 196), StrokeWidth=5, Style=skia.Paint.kStroke_Style))


def bookshelf(c, x0, y0, x1, y1, seed=1, col=(72, 50, 36)):
    rng = np.random.default_rng(seed)
    rect(c, x0, y0, x1, y1, col)
    rows = 5
    hh = (y1 - y0) / rows
    books = [(150, 60, 50), (60, 90, 120), (190, 160, 90), (70, 110, 80), (120, 70, 110), (200, 200, 190), (40, 50, 70)]
    for r in range(rows):
        yb = y0 + (r + 1) * hh - 10
        rect(c, x0 + 10, yb, x1 - 10, yb + 10, mix(col, (0, 0, 0), 0.3))
        x = x0 + 16
        while x < x1 - 30:
            bw = rng.uniform(12, 26)
            bh = hh * rng.uniform(0.55, 0.85)
            tilt = rng.random() < 0.08
            col_b = books[rng.integers(len(books))]
            if tilt:
                c.save()
                c.translate(x, yb)
                c.rotate(-14)
                rect(c, 0, -bh, bw, 0, col_b)
                c.restore()
                x += bw + 14
            else:
                rect(c, x, yb - bh, x + bw, yb, col_b)
                x += bw + 2
            if rng.random() < 0.12:
                x += rng.uniform(20, 50)


def couch(c, x0, yf, w, h, col=(48, 78, 84)):
    dark = mix(col, (0, 0, 0), 0.25)
    rrect(c, x0, yf - h, x0 + w, yf - h * 0.35, 26, dark)
    rrect(c, x0 + 20, yf - h * 0.55, x0 + w - 20, yf - 20, 18, col)
    rrect(c, x0 - 12, yf - h * 0.72, x0 + 60, yf - 18, 22, dark)
    rrect(c, x0 + w - 60, yf - h * 0.72, x0 + w + 12, yf - 18, 22, dark)
    for k in (0.1, 0.9):
        rect(c, x0 + w * k - 6, yf - 22, x0 + w * k + 6, yf, (30, 24, 20))


def lamp(c, x, yf, h=520, on=True, col=(214, 196, 160)):
    c.drawLine(x, yf, x, yf - h, P((40, 36, 34), StrokeWidth=8))
    rect(c, x - 40, yf - 10, x + 40, yf, (40, 36, 34))
    sh = skia.Path()
    sh.addPoly([skia.Point(x - 70, yf - h + 10), skia.Point(x + 70, yf - h + 10), skia.Point(x + 45, yf - h - 90),
                skia.Point(x - 45, yf - h - 90)], True)
    c.drawPath(sh, P(mix(col, (255, 230, 170), 0.3) if on else mix(col, (0, 0, 0), 0.4)))
    if on:
        glow(c, x, yf - h - 20, 420, (255, 200, 130), 0.28)


def bed(c, x0, yf, w, blanket=(54, 60, 100), sheet=(200, 200, 208), frame=(60, 44, 34)):
    rect(c, x0, yf - 140, x0 + w, yf - 30, frame)
    rect(c, x0 - 14, yf - 300, x0 + 24, yf, frame)
    rect(c, x0 + 10, yf - 210, x0 + w, yf - 130, sheet)
    rrect(c, x0 + 30, yf - 250, x0 + 210, yf - 190, 26, (218, 218, 224))
    rrect(c, x0 + 160, yf - 220, x0 + w + 8, yf - 120, 30, blanket)
    for k in (0.4, 0.65, 0.85):
        c.drawLine(x0 + 160 + (w - 150) * k, yf - 215, x0 + 140 + (w - 150) * k, yf - 125,
                   P(mix(blanket, (0, 0, 0), 0.25), 0.6, StrokeWidth=4))


def picture(c, x0, y0, x1, y1, inner=(170, 120, 90), frame=(40, 34, 30)):
    rect(c, x0, y0, x1, y1, frame)
    rect(c, x0 + 12, y0 + 12, x1 - 12, y1 - 12, inner)
    c.drawCircle((x0 + x1) / 2, (y0 + y1) / 2 + 10, (y1 - y0) * 0.22, P(mix(inner, (255, 230, 200), 0.4)))


def wall_clock(c, x, y, r, minutes):
    c.drawCircle(x, y, r + 6, P((40, 36, 34)))
    c.drawCircle(x, y, r, P((226, 222, 210)))
    hh = (minutes / 60) % 12
    for ang, ln, wd in ((hh / 12 * 360, r * 0.5, 6), ((minutes % 60) / 60 * 360, r * 0.8, 4)):
        a = math.radians(ang)
        c.drawLine(x, y, x + math.sin(a) * ln, y - math.cos(a) * ln, P((40, 36, 34), StrokeWidth=wd, StrokeCap=skia.Paint.kRound_Cap))


def plant(c, x, yf, s=1.0):
    rrect(c, x - 40 * s, yf - 70 * s, x + 40 * s, yf, 8, (150, 80, 60))
    for k in range(7):
        a = math.radians(-70 + k * 23)
        p = skia.Path()
        p.moveTo(x, yf - 60 * s)
        p.quadTo(x + math.sin(a) * 60 * s, yf - 60 * s - 90 * s, x + math.sin(a) * 120 * s, yf - 60 * s - math.cos(a) * 140 * s)
        c.drawPath(p, P((60, 110, 70), StrokeWidth=16 * s, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))


# ---------- esterni ----------

def sky(c, x0, y0, x1, y1, mood):
    pal = {
        "dawn": [(26, 30, 60), (70, 62, 96), (190, 120, 110)],
        "day": [(110, 150, 200), (160, 190, 220), (210, 220, 230)],
        "sunset": [(40, 34, 70), (150, 70, 70), (255, 150, 80)],
        "fire": [(30, 22, 40), (110, 50, 50), (240, 120, 60)],
        "night": [(8, 10, 24), (20, 24, 48), (44, 42, 70)],
        "fog": [(120, 126, 132), (150, 154, 158), (170, 172, 174)],
        "wrong": [(30, 60, 50), (90, 140, 90), (200, 220, 140)],
    }[mood]
    vgrad(c, x0, y0, x1, y1, pal, pal[0], stops=[0, 0.6, 1])


def skyline(c, x0, y0, x1, y1, mood="night", seed=2, lights=1.0, fires=0, t=0.0, layers=3):
    """Città in silhouette su più piani, con finestre accese (lights 0..1) e incendi con fumo."""
    rng = np.random.default_rng(seed)
    sky(c, x0, y0, x1, y1, mood)
    base_cols = {"night": (26, 28, 44), "dawn": (40, 40, 64), "day": (120, 130, 150), "sunset": (48, 36, 54),
                 "fire": (36, 28, 40), "fog": (130, 134, 138), "wrong": (40, 60, 56)}[mood]
    for L in range(layers):
        depth = (layers - L) / layers
        col = mix(base_cols, (0, 0, 0), 0.15 * L) if mood != "fog" else mix(base_cols, (90, 94, 98), L / layers)
        if mood != "fog":
            col = mix(col, sky_col(mood), 0.35 * depth)
        x = x0 - 20
        while x < x1:
            bw = rng.uniform(50, 130) * (1.2 - 0.25 * L)
            bh = (y1 - y0) * rng.uniform(0.25, 0.75) * (0.55 + 0.25 * L)
            top = y1 - bh
            rect(c, x, top, x + bw, y1, col)
            if rng.random() < 0.2:
                rect(c, x + bw * 0.4, top - 30, x + bw * 0.45, top, col)
            if lights > 0 and mood not in ("day", "fog"):
                for wy in np.arange(top + 14, y1 - 10, 22):
                    for wx in np.arange(x + 8, x + bw - 10, 16):
                        if rng.random() < 0.22 * lights:
                            warm = mix((250, 200, 120), (255, 240, 200), rng.random())
                            rect(c, wx, wy, wx + 7, wy + 10, warm, 0.55 + 0.4 * L / layers)
            x += bw + rng.uniform(-6, 16)
    for i in range(fires):
        fx = x0 + (x1 - x0) * rng.uniform(0.1, 0.9)
        fy = y1 - (y1 - y0) * rng.uniform(0.15, 0.5)
        glow(c, fx, fy, 160, (255, 120, 50), 0.5)
        glow(c, fx, fy, 50, (255, 210, 120), 0.6)
        for k in range(6):
            ph = (t * 0.15 + k / 6) % 1
            c.drawCircle(fx + math.sin(k * 2 + t * 0.4) * 30 + ph * 40, fy - ph * 300, 40 + ph * 80,
                         P((30, 26, 30), 0.35 * (1 - ph)))


def sky_col(mood):
    return {"night": (20, 24, 48), "dawn": (70, 62, 96), "day": (160, 190, 220), "sunset": (150, 70, 70),
            "fire": (110, 50, 50), "fog": (150, 154, 158), "wrong": (90, 140, 90)}[mood]


def fog(c, x0, y0, x1, y1, t, a=0.6, col=(170, 172, 176), seed=4, n=18, stretch=2.6):
    """Banchi di nebbia: ellissi morbide allungate che scorrono piano, più una foschia uniforme."""
    rng = np.random.default_rng(seed)
    w, h = x1 - x0, y1 - y0
    vgrad(c, x0, y0, x1, y1, [mix(col, (0, 0, 0), 0.0), col, col], col, a=a * 0.35, stops=[0, 0.5, 1])
    for k in range(n):
        speed = rng.uniform(0.006, 0.018) * (1 if k % 2 else -1)
        cx = x0 + ((rng.uniform(0, 1) + t * speed) % 1.4 - 0.2) * w
        cy = y0 + rng.uniform(0.0, 1.0) * h
        r = rng.uniform(0.18, 0.4) * w
        c.save()
        c.translate(cx, cy)
        c.scale(stretch, 1.0)
        sh = skia.GradientShader.MakeRadial((0, 0), r, [rgba(col, a * rng.uniform(0.35, 0.6)), rgba(col, 0)])
        c.drawCircle(0, 0, r, skia.Paint(AntiAlias=True, Shader=sh))
        c.restore()


def rain(c, x0, y0, x1, y1, t, n=140, a=0.35, seed=5):
    rng = np.random.default_rng(seed)
    p = P((190, 200, 220), a, StrokeWidth=2)
    for k in range(n):
        x = x0 + rng.uniform(0, 1) * (x1 - x0)
        y = y0 + ((rng.uniform(0, 1) + t * rng.uniform(1.4, 2.0)) % 1) * (y1 - y0)
        c.drawLine(x, y, x - 8, y + 34, p)


def dust(c, x0, y0, x1, y1, t, n=40, a=0.5, seed=6, col=(255, 240, 210)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x = x0 + (rng.uniform(0, 1) + math.sin(t * 0.3 + k) * 0.02) * (x1 - x0)
        y = y0 + ((rng.uniform(0, 1) - t * rng.uniform(0.005, 0.02)) % 1) * (y1 - y0)
        c.drawCircle(x, y, rng.uniform(1.2, 3.0), P(col, a * (0.4 + 0.6 * abs(math.sin(t * 0.7 + k)))))


# ---------- luce e buio ----------

def darkness(c, a, lights=(), col=(3, 4, 9)):
    """Buio su tutto lo schermo con "buchi" morbidi dove c'è luce: lights = [(x, y, r, forza)]."""
    if a <= 0:
        return
    c.saveLayer(None, None)
    c.drawRect(skia.Rect(-W, -H, 2 * W, 2 * H), P(col, a))
    for x, y, r, s in lights:
        sh = skia.GradientShader.MakeRadial((x, y), r, [rgba((0, 0, 0), s), rgba((0, 0, 0), s * 0.6), rgba((0, 0, 0), 0)],
                                            [0, 0.45, 1])
        c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=sh, BlendMode=skia.BlendMode.kDstOut))
    c.restore()


def beam(c, x, y, angle, spread=22, length=900, col=(255, 244, 220), a=0.35):
    """Fascio di torcia: cono con sfumatura lungo la lunghezza."""
    a0, a1 = math.radians(angle - spread / 2), math.radians(angle + spread / 2)
    p = skia.Path()
    p.moveTo(x, y)
    p.lineTo(x + math.cos(a0) * length, y + math.sin(a0) * length)
    p.lineTo(x + math.cos(a1) * length, y + math.sin(a1) * length)
    p.close()
    am = math.radians(angle)
    sh = skia.GradientShader.MakeLinear([(x, y), (x + math.cos(am) * length, y + math.sin(am) * length)],
                                        [rgba(col, a), rgba(col, a * 0.35), rgba(col, 0)], [0, 0.5, 1])
    c.drawPath(p, skia.Paint(AntiAlias=True, Shader=sh, BlendMode=skia.BlendMode.kPlus))
    glow(c, x, y, 60, col, 0.7)


# ---------- telefono ----------

def phone(c, cx, cy, w, h, screen, tilt=0.0, glow_a=0.25, glow_col=(150, 170, 255)):
    """Telefono con schermo: screen(c, (x0, y0, x1, y1)) disegna la UI dentro lo schermo."""
    c.save()
    c.translate(cx, cy)
    c.rotate(tilt)
    if glow_a > 0:
        glow(c, 0, 0, max(w, h) * 0.9, glow_col, glow_a)
    rrect(c, -w / 2 - 10, -h / 2 - 10, w / 2 + 10, h / 2 + 10, w * 0.14, (16, 16, 20))
    rrect(c, -w / 2 - 10, -h / 2 - 10, w / 2 + 10, h / 2 + 10, w * 0.14, (60, 60, 70), 0.0)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-w / 2 - 10, -h / 2 - 10, w / 2 + 10, h / 2 + 10), w * 0.14, w * 0.14),
                P((80, 80, 92), StrokeWidth=3, Style=skia.Paint.kStroke_Style))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect(-w / 2, -h / 2, w / 2, h / 2), w * 0.11, w * 0.11), True)
    screen(c, (-w / 2, -h / 2, w / 2, h / 2))
    c.restore()
    rrect(c, -w * 0.16, -h / 2 + 14, w * 0.16, -h / 2 + 40, 13, (8, 8, 10))
    c.restore()


def lock_screen(c, r, time_s, date_s, notifs, t=0.0, wall=((38, 34, 70), (90, 60, 110))):
    """notifs: [(app, titolo, testo, colore icona, quando compare in s)] dalla più recente in alto."""
    x0, y0, x1, y1 = r
    vgrad(c, x0, y0, x1, y1, wall[0], wall[1])
    w = x1 - x0
    cx = (x0 + x1) / 2
    gfx.draw_text(c, date_s, K.bold(int(w * 0.055)), cx, y0 + w * 0.3, color=(235, 235, 245), alpha=0.85)
    gfx.draw_text(c, time_s, gfx._font("Montserrat-SemiBold.ttf", int(w * 0.25)), cx, y0 + w * 0.56,
                  color=(245, 245, 250))
    y = y0 + w * 0.72
    shown = [n for n in notifs if t >= n[4]]
    for app, title, body, icol, at in shown:
        k = gfx.ease_out((t - at) / 0.25)
        yy = y - (1 - k) * 30
        alert = icol == (220, 40, 40)
        rrect(c, x0 + w * 0.05, yy, x1 - w * 0.05, yy + w * 0.2, w * 0.05, (120, 30, 34) if alert else (46, 44, 66), 0.92 * k)
        rrect(c, x0 + w * 0.09, yy + w * 0.045, x0 + w * 0.19, yy + w * 0.145, w * 0.025, icol, k)
        if alert:
            tri = skia.Path()
            ix, iy = x0 + w * 0.14, yy + w * 0.095
            tri.addPoly([skia.Point(ix, iy - w * 0.035), skia.Point(ix + w * 0.035, iy + w * 0.03),
                         skia.Point(ix - w * 0.035, iy + w * 0.03)], True)
            c.drawPath(tri, P((255, 255, 255), k))
        gfx.draw_text(c, title, K.bold(int(w * 0.042)), x0 + w * 0.23, yy + w * 0.085,
                      color=(255, 120, 110) if alert else (240, 240, 245), alpha=k, align="left")
        gfx.draw_text(c, body, gfx.text(int(w * 0.036)), x0 + w * 0.23, yy + w * 0.145, color=(215, 215, 225),
                      alpha=k, align="left")
        gfx.draw_text(c, "now", gfx.text(int(w * 0.03)), x1 - w * 0.09, yy + w * 0.07, color=(200, 200, 210),
                      alpha=0.8 * k, align="right")
        y += w * 0.23


def alert_screen(c, r, title, kind, lines, t=0.0, footer="Further instructions will follow."):
    """Allerta d'emergenza a tutto schermo: rosso, triangolo, titolo, testo che compare riga per riga."""
    x0, y0, x1, y1 = r
    w = x1 - x0
    cx = (x0 + x1) / 2
    vgrad(c, x0, y0, x1, y1, (120, 16, 18), (40, 6, 8))
    pulse = 0.5 + 0.5 * math.sin(t * 6)
    glow(c, cx, y0 + w * 0.32, w * 0.6, (255, 60, 50), 0.25 + 0.15 * pulse)
    tri = skia.Path()
    ty = y0 + w * 0.3
    s = w * 0.17
    tri.addPoly([skia.Point(cx, ty - s), skia.Point(cx + s * 1.1, ty + s * 0.8), skia.Point(cx - s * 1.1, ty + s * 0.8)], True)
    c.drawPath(tri, skia.Paint(AntiAlias=True, Color=rgba((235, 50, 45)), PathEffect=skia.CornerPathEffect.Make(s * 0.2)))
    rrect(c, cx - s * 0.1, ty - s * 0.45, cx + s * 0.1, ty + s * 0.3, s * 0.08, (255, 255, 255))
    c.drawCircle(cx, ty + s * 0.55, s * 0.11, P((255, 255, 255)))
    gfx.draw_text(c, title, gfx.fit_font(K.heavy, title, w * 0.9, int(w * 0.085)), cx, y0 + w * 0.68, color=(255, 255, 255))
    gfx.draw_text(c, kind, K.bold(int(w * 0.045)), cx, y0 + w * 0.77, color=(255, 120, 100), tracking=4)
    c.drawLine(x0 + w * 0.12, y0 + w * 0.83, x1 - w * 0.12, y0 + w * 0.83, P((255, 255, 255), 0.25, StrokeWidth=2))
    y = y0 + w * 0.98
    for i, (line, col, at) in enumerate(lines):
        if t < at:
            continue
        k = gfx.ease_out((t - at) / 0.2)
        f = gfx.fit_font(K.heavy, line, w * 0.88, int(w * 0.075))
        gfx.draw_text(c, line, f, cx, y + (1 - k) * 12, color=col, alpha=k)
        y += w * 0.1
    gfx.draw_text(c, footer, gfx.text(int(w * 0.034)), cx, y1 - w * 0.36, color=(240, 200, 200), alpha=0.85)
    rrect(c, cx - w * 0.2, y1 - w * 0.3, cx + w * 0.2, y1 - w * 0.2, w * 0.05, (255, 255, 255), 0.18)
    gfx.draw_text(c, "OK", K.bold(int(w * 0.045)), cx, y1 - w * 0.234, color=(255, 255, 255))


def chat_screen(c, r, name, msgs, t=0.0, typing_at=None, status="online"):
    """Chat: msgs = [(testo, mio?, quando compare)]; typing_at = da quando mostrare i tre puntini."""
    x0, y0, x1, y1 = r
    w = x1 - x0
    rect(c, x0, y0, x1, y1, (16, 18, 24))
    rect(c, x0, y0, x1, y0 + w * 0.3, (28, 30, 38))
    c.drawCircle(x0 + w * 0.16, y0 + w * 0.2, w * 0.06, P((120, 140, 190)))
    gfx.draw_text(c, name, K.bold(int(w * 0.05)), x0 + w * 0.26, y0 + w * 0.2, color=(240, 240, 245), align="left")
    gfx.draw_text(c, status, gfx.text(int(w * 0.034)), x0 + w * 0.26, y0 + w * 0.25, color=(140, 200, 150), align="left")
    y = y0 + w * 0.42
    f = gfx.text(int(w * 0.045))
    for body, mine, at in msgs:
        if t < at:
            continue
        k = gfx.ease_out((t - at) / 0.2)
        tw = min(w * 0.68, f.measureText(body) + w * 0.08)
        bx0 = x1 - w * 0.05 - tw if mine else x0 + w * 0.05
        rrect(c, bx0, y, bx0 + tw, y + w * 0.12, w * 0.04, (60, 110, 230) if mine else (52, 54, 64), k)
        gfx.draw_text(c, body, f, bx0 + w * 0.04, y + w * 0.077, color=(255, 255, 255), alpha=k, align="left")
        y += w * 0.15
    if typing_at is not None and t >= typing_at:
        rrect(c, x0 + w * 0.05, y, x0 + w * 0.25, y + w * 0.1, w * 0.04, (52, 54, 64))
        for i in range(3):
            a = 0.4 + 0.6 * max(0, math.sin(t * 6 - i * 0.8))
            c.drawCircle(x0 + w * (0.1 + i * 0.05), y + w * 0.05, w * 0.014, P((220, 220, 230), a))


# ---------- spioncino ----------

def peephole(c, cx, cy, r, draw, t=0.0):
    """Vista dallo spioncino: scena deformata a occhio di pesce dentro un cerchio, tutto il resto nero."""
    c.drawRect(skia.Rect(-W, -H, 2 * W, 2 * H), P((0, 0, 0)))
    c.save()
    c.clipPath(skia.Path.Circle(cx, cy, r), skia.ClipOp.kIntersect, True)
    c.save()
    c.translate(cx, cy)
    c.scale(1.08, 1.08)
    c.translate(-cx, -cy)
    draw(c)
    c.restore()
    sh = skia.GradientShader.MakeRadial((cx, cy), r, [rgba((0, 0, 0), 0), rgba((0, 0, 0), 0.15), rgba((0, 0, 0), 0.92)],
                                        [0, 0.7, 1])
    c.drawCircle(cx, cy, r, skia.Paint(AntiAlias=True, Shader=sh))
    c.restore()
    c.drawCircle(cx, cy, r, P((60, 50, 40), 0.6, StrokeWidth=6, Style=skia.Paint.kStroke_Style))


def pin(c, x, y, label, a=1.0, up=150, col=(240, 200, 80)):
    """Etichetta "YOU · FLOOR 14" con la linea che punta al posto giusto."""
    if a <= 0:
        return
    f = K.bold(26)
    w = f.measureText(label)
    top = y - up
    c.drawLine(x, y, x, top + 22, P(col, a, StrokeWidth=3))
    c.drawCircle(x, y, 9, P(col, a, StrokeWidth=3, Style=skia.Paint.kStroke_Style))
    r = skia.RRect.MakeRectXY(skia.Rect(x - w / 2 - 22, top - 22, x + w / 2 + 22, top + 22), 22, 22)
    c.drawRRect(r, P((16, 14, 12), 0.88 * a))
    c.drawRRect(r, P(col, a, StrokeWidth=3, Style=skia.Paint.kStroke_Style))
    gfx.draw_text(c, label, f, x, top + 9, color=col, alpha=a, tracking=2)


def shaft(c, x0, y0, x1, y1, spread, length, col=(255, 230, 190), a=0.12, angle=20):
    """Fascio di luce dalla finestra: dal bordo (x0,y0)-(x1,y1) verso il basso, inclinato di angle gradi."""
    ang = math.radians(90 - angle)
    dx, dy = math.cos(ang) * length, math.sin(ang) * length
    p = skia.Path()
    p.moveTo(x0, y0)
    p.lineTo(x1, y1)
    p.lineTo(x1 + dx + spread, y1 + dy)
    p.lineTo(x0 + dx - spread, y0 + dy)
    p.close()
    sh = skia.GradientShader.MakeLinear([((x0 + x1) / 2, (y0 + y1) / 2), ((x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy)],
                                        [rgba(col, a), rgba(col, 0)])
    c.drawPath(p, skia.Paint(AntiAlias=True, Shader=sh, BlendMode=skia.BlendMode.kPlus))


def birds(c, x0, y0, x1, y1, t, n=7, seed=8, col=(20, 18, 24)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x = x0 + ((rng.uniform(0, 1) + t * rng.uniform(0.02, 0.05)) % 1) * (x1 - x0)
        y = y0 + rng.uniform(0, 1) * (y1 - y0) + math.sin(t * 2 + k) * 6
        flap = math.sin(t * 9 + k * 1.3) * 5
        p = skia.Path()
        p.moveTo(x - 9, y - flap)
        p.quadTo(x - 4, y - 4, x, y)
        p.quadTo(x + 4, y - 4, x + 9, y - flap)
        c.drawPath(p, P(col, 0.85, StrokeWidth=2.5, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))


def corridor(c, vx=540, vy=820, wall=(46, 84, 82), floor=(140, 58, 48), ceil=(30, 34, 38), far=(14, 14, 16),
             doors=4, lights=3, light_on=1.0, far_w=150, far_h=260):
    """Corridoio in prospettiva centrale (hotel, condominio, vagone): pareti, moquette, luci, porte ai lati."""
    fx0, fx1 = vx - far_w / 2, vx + far_w / 2
    fy0, fy1 = vy - far_h / 2, vy + far_h / 2

    def quad(pts, col, a=1.0):
        p = skia.Path()
        p.addPoly([skia.Point(*q) for q in pts], True)
        c.drawPath(p, P(col, a))

    quad([(0, 0), (W, 0), (fx1, fy0), (fx0, fy0)], ceil)
    quad([(0, H), (W, H), (fx1, fy1), (fx0, fy1)], floor)
    quad([(0, 0), (fx0, fy0), (fx0, fy1), (0, H)], wall)
    quad([(W, 0), (fx1, fy0), (fx1, fy1), (W, H)], mix(wall, (0, 0, 0), 0.15))
    rect(c, fx0, fy0, fx1, fy1, far)
    # motivo della moquette: rombi che si stringono verso il fondo
    for k in range(1, 12):
        d = (k / 12) ** 1.8
        y = fy1 + (H - fy1) * d
        hw = far_w / 2 + (W / 2 - far_w / 2) * d
        c.drawLine(vx - hw, y, vx + hw, y, P(mix(floor, (0, 0, 0), 0.2), 0.5, StrokeWidth=1 + 3 * d))
    for side in (-1, 1):
        for i in range(doors):
            d0 = 0.15 + i * 0.22
            d1 = d0 + 0.1

            def at(d, yy):
                x = vx + side * (far_w / 2 + (W / 2 - far_w / 2) * d)
                y = vy + (yy - vy) * (far_h / 2 + (H / 2 - far_h / 2) * d) / (far_h / 2) if False else None
                return x

            xa = vx + side * (far_w / 2 + (W / 2 + 80 - far_w / 2) * (1 - d1) ** 2)
            xb = vx + side * (far_w / 2 + (W / 2 + 80 - far_w / 2) * (1 - d0) ** 2)
            ka, kb = (abs(xa - vx) - far_w / 2) / (W / 2 - far_w / 2), (abs(xb - vx) - far_w / 2) / (W / 2 - far_w / 2)
            ta, tb = fy0 * (1 - ka) + 0 * ka, fy0 * (1 - kb) + 0 * kb
            ba, bb = fy1 * (1 - ka) + H * ka, fy1 * (1 - kb) + H * kb
            top_a, top_b = ta + (ba - ta) * 0.18, tb + (bb - tb) * 0.18
            quad([(xa, top_a), (xb, top_b), (xb, bb - (bb - tb) * 0.02), (xa, ba - (ba - ta) * 0.02)], (92, 54, 40))
            c.drawCircle(xa + (xb - xa) * 0.85, (top_a + ba) / 2, 3 + 6 * kb, P((200, 170, 90)))
    for i in range(lights):
        d = 0.2 + i * 0.3
        y = fy0 * (1 - d)
        hw = far_w / 2 + (W / 2 - far_w / 2) * d
        rect(c, vx - hw * 0.25, y - 4 - 10 * d, vx + hw * 0.25, y + 4 + 6 * d, (255, 236, 200), 0.9 * light_on)
        glow(c, vx, y + 30 * d, 120 + 380 * d, (255, 220, 170), 0.22 * light_on)


# ---------- quartiere ----------

def house(c, x, yb, w=520, h=420, siding=(150, 156, 168), roof=(70, 62, 66), trim=(225, 222, 214),
          lit=(), porch_light=0.0, door=(90, 54, 44), seed=1, dark=0.0):
    """Casa a due piani vista di fronte. lit = indici delle finestre accese (0-3 sopra, 4-5 sotto)."""
    sid = mix(siding, (10, 12, 18), dark)
    rf = mix(roof, (6, 6, 10), dark)
    x0, x1 = x - w / 2, x + w / 2
    top = yb - h
    rect(c, x0, top, x1, yb, sid)
    for k in range(int(h / 18)):
        c.drawLine(x0, top + k * 18 + 9, x1, top + k * 18 + 9, P(mix(sid, (0, 0, 0), 0.1), 0.6, StrokeWidth=2))
    p = skia.Path()
    p.addPoly([skia.Point(x0 - 40, top + 4), skia.Point(x, top - h * 0.45), skia.Point(x1 + 40, top + 4)], True)
    c.drawPath(p, P(rf))
    rect(c, x0 + w * 0.68, top - h * 0.38, x0 + w * 0.78, top - h * 0.08, mix(rf, (0, 0, 0), 0.2))   # camino
    wins = [(0.12, 0.08), (0.62, 0.08), (0.12, 0.55), (0.62, 0.55)]
    for i, (fx, fy) in enumerate(wins):
        wx0, wy0 = x0 + w * fx, top + h * fy
        wx1, wy1 = wx0 + w * 0.26, wy0 + h * 0.28
        on = i in lit
        rect(c, wx0 - 8, wy0 - 8, wx1 + 8, wy1 + 8, mix(trim, (10, 12, 18), dark))
        rect(c, wx0, wy0, wx1, wy1, (255, 214, 140) if on else mix((40, 46, 58), (4, 5, 8), dark))
        if on:
            glow(c, (wx0 + wx1) / 2, (wy0 + wy1) / 2, w * 0.35, (255, 190, 110), 0.3)
        c.drawLine((wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1, P(mix(trim, (10, 12, 18), dark), StrokeWidth=5))
        c.drawLine(wx0, (wy0 + wy1) / 2, wx1, (wy0 + wy1) / 2, P(mix(trim, (10, 12, 18), dark), StrokeWidth=5))
    # porta e portico
    dx0, dx1 = x - w * 0.09, x + w * 0.09
    rect(c, dx0 - 8, yb - h * 0.42 - 8, dx1 + 8, yb, mix(trim, (10, 12, 18), dark))
    rect(c, dx0, yb - h * 0.42, dx1, yb, mix(door, (4, 4, 6), dark))
    c.drawCircle(dx1 - 12, yb - h * 0.2, 5, P((200, 170, 90)))
    rect(c, x - w * 0.22, yb - h * 0.5, x + w * 0.22, yb - h * 0.45, mix(rf, (0, 0, 0), 0.1))
    for k in range(3):
        rect(c, x - w * 0.16 - k * 14, yb + k * 16, x + w * 0.16 + k * 14, yb + (k + 1) * 16, mix((150, 146, 140), (8, 8, 10), dark))
    if porch_light > 0:
        c.drawCircle(dx1 + 24, yb - h * 0.36, 7, P((255, 230, 170), porch_light))
        glow(c, dx1 + 24, yb - h * 0.36, 160, (255, 200, 120), 0.4 * porch_light)


def streetlight(c, x, yb, h=560, on=1.0, flicker_t=None):
    c.drawLine(x, yb, x, yb - h, P((40, 42, 48), StrokeWidth=12))
    c.drawLine(x, yb - h, x + 90, yb - h + 10, P((40, 42, 48), StrokeWidth=10))
    rrect(c, x + 60, yb - h + 4, x + 120, yb - h + 22, 6, (60, 60, 64))
    if on > 0:
        rect(c, x + 66, yb - h + 18, x + 114, yb - h + 24, (255, 236, 190), on)
        glow(c, x + 90, yb - h + 30, 300, (255, 220, 160), 0.35 * on)
        p = skia.Path()
        p.addPoly([skia.Point(x + 66, yb - h + 24), skia.Point(x + 114, yb - h + 24), skia.Point(x + 260, yb),
                   skia.Point(x - 80, yb)], True)
        sh = skia.GradientShader.MakeLinear([(x + 90, yb - h), (x + 90, yb)], [rgba((255, 225, 170), 0.22 * on),
                                                                               rgba((255, 225, 170), 0.02 * on)])
        c.drawPath(p, skia.Paint(AntiAlias=True, Shader=sh, BlendMode=skia.BlendMode.kPlus))


def sound_rings(c, x, y, t, col=(200, 220, 255), n=3, r_max=260, a=0.6, period=1.6, width=6):
    """Onde sonore che si allargano da un punto (una casa che "parla")."""
    for k in range(n):
        ph = ((t / period) + k / n) % 1.0
        c.drawCircle(x, y, 20 + ph * r_max, P(col, a * (1 - ph) ** 1.5, StrokeWidth=width * (1 - 0.5 * ph),
                                               Style=skia.Paint.kStroke_Style))


def tv(c, x0, y0, x1, y1, on=0.0, t=0.0, unplugged=False):
    rrect(c, x0, y0, x1, y1, 10, (20, 20, 24))
    rect(c, x0 + 14, y0 + 14, x1 - 14, y1 - 14, (12, 14, 18))
    if on > 0:
        rect(c, x0 + 14, y0 + 14, x1 - 14, y1 - 14, (120, 140, 190), 0.5 * on)
        glow(c, (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0), (130, 160, 255), 0.2 * on)
    rect(c, (x0 + x1) / 2 - 50, y1, (x0 + x1) / 2 + 50, y1 + 16, (30, 30, 34))
    cab = P((30, 30, 34), StrokeWidth=5, Style=skia.Paint.kStroke_Style)
    p = skia.Path()
    p.moveTo(x1 - 30, y1)
    if unplugged:
        p.quadTo(x1 + 20, y1 + 120, x1 + 90, y1 + 150)
    else:
        p.quadTo(x1 + 10, y1 + 80, x1 + 40, y1 + 140)
    c.drawPath(p, cab)


def smart_speaker(c, x, yb, h=110, ring=0.0, t=0.0):
    rrect(c, x - 34, yb - h, x + 34, yb, 20, (52, 54, 62))
    for k in range(5):
        c.drawLine(x - 28, yb - h + 26 + k * 16, x + 28, yb - h + 26 + k * 16, P((40, 42, 48), StrokeWidth=3))
    if ring > 0:
        rect(c, x - 30, yb - h + 6, x + 30, yb - h + 12, (120, 200, 255), ring * (0.6 + 0.4 * math.sin(t * 7)))
        glow(c, x, yb - h + 9, 90, (120, 200, 255), 0.4 * ring)


def fridge(c, x0, y0, x1, y1, light=0.0, col=(206, 208, 212)):
    rrect(c, x0, y0, x1, y1, 14, col)
    c.drawLine(x0, y0 + (y1 - y0) * 0.36, x1, y0 + (y1 - y0) * 0.36, P(mix(col, (0, 0, 0), 0.25), StrokeWidth=4))
    for yy in (0.18, 0.55):
        rect(c, x1 - 26, y0 + (y1 - y0) * yy, x1 - 16, y0 + (y1 - y0) * (yy + 0.14), (120, 120, 126))
    if light > 0:
        c.drawCircle(x0 + 30, y0 + 30, 6, P((120, 230, 255), light))


def counter(c, x0, x1, yf, h=330, top=(180, 170, 156), body=(92, 72, 58)):
    rect(c, x0, yf - h, x1, yf, body)
    rect(c, x0 - 10, yf - h - 18, x1 + 10, yf - h, top)
    n = max(1, int((x1 - x0) / 160))
    for k in range(n):
        cx0 = x0 + (x1 - x0) * k / n + 10
        cx1 = x0 + (x1 - x0) * (k + 1) / n - 10
        rect(c, cx0, yf - h + 20, cx1, yf - 20, mix(body, (255, 255, 255), 0.05))
        rect(c, (cx0 + cx1) / 2 - 20, yf - h + 50, (cx0 + cx1) / 2 + 20, yf - h + 58, (170, 170, 176))
