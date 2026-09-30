"""Grafica del canale: avatar, banner e watermark, nello stesso stile dei video.

    python branding.py                     # scrive in assets/channel/
    python branding.py --name "Softloop"   # con un altro nome
"""

import argparse
import math
from pathlib import Path

import numpy as np
import skia

from shorts import gfx
from shorts.gfx import BG, INK, draw_text, mix, rgba
from shorts.themes import ZODIAC

PASTELS = [t.color for t in ZODIAC]
LOOP = [PASTELS[i] for i in (3, 10, 7, 6, 0, 4, 2, 5, 1, 11)]  # giro di colori per l'anello
OUT = Path("assets/channel")


def loop_mark(c, cx, cy, r, width):
    """Il marchio: un anello pastello aperto, con un pallino che esce dal varco."""
    gap = 42.0
    start = -90 + gap / 2          # il varco è in alto a destra
    cols = [rgba(x) for x in LOOP] + [rgba(LOOP[0])]
    shader = skia.GradientShader.MakeSweep(cx, cy, cols)
    rect = skia.Rect(cx - r, cy - r, cx + r, cy + r)
    c.save()
    c.rotate(-60, cx, cy)
    c.drawArc(rect, start, 360 - gap, False, skia.Paint(
        AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
        StrokeCap=skia.Paint.kRound_Cap, Shader=shader))
    c.restore()
    # Pallino appena uscito dal varco.
    a = math.radians(-90 - 60)
    d = r + width * 0.95
    c.drawCircle(cx + d * math.cos(a), cy + d * math.sin(a), width * 0.62,
                 skia.Paint(AntiAlias=True, Color=rgba(PASTELS[7])))


def avatar(size=800):
    s = skia.Surface(size, size)
    c = s.getCanvas()
    c.clear(rgba(BG))
    loop_mark(c, size * 0.47, size * 0.53, size * 0.27, size * 0.085)
    return s.makeImageSnapshot()


def watermark(size=150):
    s = skia.Surface(size, size)
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    loop_mark(c, size * 0.46, size * 0.54, size * 0.28, size * 0.09)
    return s.makeImageSnapshot()


def banner(name, tagline, w=2560, h=1440):
    s = skia.Surface(w, h)
    c = s.getCanvas()
    c.clear(rgba(BG))
    rng = np.random.default_rng(7)

    # Trama di labirinto molto tenue su tutto il banner (si vede solo sulle TV).
    cell = 64
    p = skia.Path()
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            if rng.random() < 0.5:
                p.moveTo(x, y)
                p.lineTo(x + cell, y)
            else:
                p.moveTo(x, y)
                p.lineTo(x, y + cell)
    c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2,
                             Color=rgba(INK, 0.05)))

    cy = h / 2
    # Sinistra, fuori dall'area sicura: palline che si convertono (Contagio).
    ax, ar = 330, 170
    placed = []
    while len(placed) < 22:
        a, rr = rng.uniform(0, 2 * math.pi), math.sqrt(rng.uniform(0, 1)) * (ar - 30)
        x, y = ax + rr * math.cos(a), cy + rr * math.sin(a)
        if all((x - px) ** 2 + (y - py) ** 2 > 46 ** 2 for px, py in placed):
            placed.append((x, y))
            c.drawCircle(x, y, 21, skia.Paint(AntiAlias=True, Color=rgba(PASTELS[int(rng.integers(len(PASTELS)))])))
    c.drawCircle(ax, cy, ar, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3,
                                        Color=rgba(INK, 0.35)))

    # Destra, fuori dall'area sicura: archi del Sync con i pallini quasi allineati.
    sx, sy = 2250, cy + 100
    c.drawLine(sx - 215, sy, sx + 215, sy, skia.Paint(AntiAlias=True, StrokeWidth=2, Color=rgba(INK, 0.3)))
    for i in range(8):
        r = 40 + i * 22
        col = mix(PASTELS[3], PASTELS[7], i / 7)
        c.drawArc(skia.Rect(sx - r, sy - r, sx + r, sy + r), 180, 180, False, skia.Paint(
            AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3, Color=rgba(col, 0.45)))
        ang = math.pi * (0.62 - 0.035 * i)
        c.drawCircle(sx + r * math.cos(ang), sy - r * math.sin(ang), 9, skia.Paint(AntiAlias=True, Color=rgba(col)))

    # Centro, dentro l'area sicura (1546x423): marchio + nome + tagline.
    fn, ft = gfx.title(150), gfx.text(40)
    block = 150 + 40 + max(fn.measureText(name), ft.measureText(tagline))
    x0 = w / 2 - block / 2
    loop_mark(c, x0 + 70, cy - 12, 60, 20)
    draw_text(c, name, fn, x0 + 190, cy + 36, color=INK, align="left")
    draw_text(c, tagline, ft, x0 + 196, cy + 116, color=INK, alpha=0.55, align="left")
    return s.makeImageSnapshot()


def preview(av, bn, path):
    """Controllo visivo: avatar ritagliato a cerchio in 3 dimensioni e banner con l'area sicura."""
    s = skia.Surface(1600, 1200)
    c = s.getCanvas()
    c.clear(skia.Color(40, 40, 46))
    x = 40
    for size in (240, 98, 36):
        c.save()
        path_c = skia.Path()
        path_c.addCircle(x + size / 2, 40 + size / 2, size / 2)
        c.clipPath(path_c, doAntiAlias=True)
        c.drawImageRect(av, skia.Rect(x, 40, x + size, 40 + size), skia.SamplingOptions(skia.FilterMode.kLinear))
        c.restore()
        x += size + 40
    sc = 1520 / 2560
    c.drawImageRect(bn, skia.Rect(40, 320, 40 + 2560 * sc, 320 + 1440 * sc), skia.SamplingOptions(skia.FilterMode.kLinear))
    sx, sy = 40 + (2560 - 1546) / 2 * sc, 320 + (1440 - 423) / 2 * sc
    c.drawRect(skia.Rect(sx, sy, sx + 1546 * sc, sy + 423 * sc),
               skia.Paint(Style=skia.Paint.kStroke_Style, StrokeWidth=2, Color=skia.Color(255, 80, 80)))
    s.makeImageSnapshot().save(str(path), skia.kPNG)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="Softloop")
    ap.add_argument("--tagline", default="Calm simulations. A new one every day.")
    ap.add_argument("--preview", default="out/branding_preview.png")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    av, bn, wm = avatar(), banner(args.name, args.tagline), watermark()
    av.save(str(OUT / "avatar.png"), skia.kPNG)
    bn.save(str(OUT / "banner.png"), skia.kPNG)
    wm.save(str(OUT / "watermark.png"), skia.kPNG)
    Path(args.preview).parent.mkdir(parents=True, exist_ok=True)
    preview(av, bn, args.preview)
    print(f"scritti {OUT}/avatar.png, banner.png, watermark.png e l'anteprima {args.preview}")


if __name__ == "__main__":
    main()
