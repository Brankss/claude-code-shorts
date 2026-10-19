"""Grafica dell'account: foto profilo (3 proposte), copertina dell'episodio, card delle regole, banner YouTube.

Stesso stile del format "rules": illustrazione piatta, stickman crema senza faccia, rosso delle card,
nebbia blu-grigia. Le foto profilo funzionano anche a 40 px (dentro il cerchio di TikTok).

    python -m shorts.branding --name "RULE NUMBER FOUR" --story dont_answer --at 92.5 \\
        --rules "COVER EVERY WINDOW|UNPLUG EVERY SPEAKER|FAMILY PASSWORD|DON'T ANSWER ANY VOICE" --out brand
"""

import argparse
import math
from pathlib import Path

import skia

from . import gfx
from . import kinetic as K
from . import pov_gfx as G
from .gfx import rgba
from .rules import RED, bebas
from .stick import POSES, Figure

CREAM = (233, 224, 205)
INK = (44, 36, 32)
NAVY = (14, 16, 26)


def _surface(w, h):
    s = skia.Surface(w, h)
    return s, s.getCanvas()


def _save(s, path):
    s.makeImageSnapshot().save(str(path), skia.kPNG)


def _radial_bg(c, w, h, inner, outer, cx=None, cy=None):
    cx = w / 2 if cx is None else cx
    cy = h / 2 if cy is None else cy
    sh = skia.GradientShader.MakeRadial((cx, cy), max(w, h) * 0.75, [rgba(inner), rgba(outer)])
    c.drawRect(skia.Rect(0, 0, w, h), skia.Paint(Shader=sh))


# ---------- foto profilo ----------

def avatar_faceless(path):
    """Testa e spalle dello stickman, senza faccia, su blu notte; il pallino rosso dell'HUD."""
    s, c = _surface(1080, 1080)
    _radial_bg(c, 1080, 1080, (44, 52, 74), NAVY, cy=470)
    G.glow(c, 540, 470, 520, (170, 186, 220), 0.18)
    # collo sotto, spalle sopra: il bordo delle spalle fa da colletto
    c.drawLine(540, 620, 540, 800, G.P(INK, StrokeWidth=124, StrokeCap=skia.Paint.kRound_Cap))
    c.drawLine(540, 620, 540, 800, G.P(CREAM, StrokeWidth=88, StrokeCap=skia.Paint.kRound_Cap))
    body = skia.Path()
    body.moveTo(160, 1080)
    body.cubicTo(200, 820, 360, 760, 540, 760)
    body.cubicTo(720, 760, 880, 820, 920, 1080)
    c.drawPath(body, G.P(INK, StrokeWidth=34, Style=skia.Paint.kStroke_Style))
    c.drawPath(body, G.P(CREAM))
    c.drawCircle(540, 450, 250, G.P(INK))
    c.drawCircle(540, 450, 222, G.P(CREAM))
    sh = skia.GradientShader.MakeLinear([(340, 300), (740, 640)], [rgba((255, 255, 255), 0.0), rgba((0, 0, 0), 0.18)])
    c.drawCircle(540, 450, 222, skia.Paint(AntiAlias=True, Shader=sh))
    c.drawCircle(860, 210, 54, G.P(RED))
    G.glow(c, 860, 210, 150, RED, 0.35)
    _save(s, path)


def _bent(c, x, y, height, facing=1, fill=(14, 15, 20), ink=(6, 6, 9), arms=(12, -10)):
    """La cosa: sagoma scura con la testa che pende di lato sotto la spalla. (x, y) = anca."""
    fig = Figure(height=height, fill=fill, ink=ink, neck=1.9)
    p = dict(POSES["stand"], head=150, lsh=arms[0], lel=-6, rsh=arms[1], rel=4)
    return fig.draw(c, x, y, p, facing=facing, feet=False)


def avatar_bent(path):
    """La cosa col collo spezzato, in controluce contro un lampione nella nebbia."""
    s, c = _surface(1080, 1080)
    G.vgrad(c, 0, 0, 1080, 1080, [(14, 16, 26), (46, 54, 74), (84, 94, 114)], (84, 94, 114), stops=[0, 0.55, 1])
    # alone del lampione dietro: la sagoma si stacca nera anche a 40 px
    c.drawCircle(500, 470, 330, skia.Paint(AntiAlias=True, Color=rgba((150, 162, 186)),
                                           MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 60)))
    G.glow(c, 500, 470, 560, (210, 222, 245), 0.35)
    _bent(c, 470, 690, 980, facing=1, arms=(26, -22))
    sh = skia.GradientShader.MakeLinear([(0, 760), (0, 1080)], [rgba((96, 106, 128), 0.0), rgba((96, 106, 128), 0.95)])
    c.drawRect(skia.Rect(0, 760, 1080, 1080), skia.Paint(Shader=sh))
    _save(s, path)


def avatar_rule(path):
    """Il cartellino rosso "RULE #4" su nero: si legge anche minuscolo."""
    s, c = _surface(1080, 1080)
    _radial_bg(c, 1080, 1080, (34, 30, 36), (8, 8, 10))
    c.save()
    c.translate(540, 560)
    c.rotate(-4)
    c.drawRect(skia.Rect(-400, -250, 400, 250), G.P(RED))
    f = bebas(420)
    w = f.measureText("#4")
    c.drawString("#4", -w / 2, 150, f, G.P((255, 255, 255)))
    rf = K.heavy(70)
    rw = rf.measureText("RULE")
    c.drawString("RULE", -rw / 2, -150, rf, G.P((255, 255, 255)))
    c.restore()
    _save(s, path)


# ---------- copertina dell'episodio (9:16) ----------

def clean_frame(story, t, path):
    """Il fotogramma al secondo t senza HUD, card e didascalie: lo sfondo pulito per la copertina."""
    from .pov_stories import STORIES
    from .rules import Renderer
    r = Renderer(STORIES[story]())
    c = r.surface.getCanvas()
    c.clear(skia.Color(8, 8, 10))
    idx, _ = r.tl.at(t)
    r._scene(c, idx, t)
    _save(r.surface, path)


def cover(path, frame_png, title, day="DAY 1", hook="DO YOU ANSWER HER?"):
    """Copertina: un fotogramma del video scurito, titolo della serie, giorno, la domanda."""
    s, c = _surface(1080, 1920)
    img = skia.Image.open(str(frame_png))
    # il fotogramma pulito non ha il bloom del video: lo schiarisco un po' (nel feed la copertina è piccola)
    lift = skia.ColorFilters.Matrix([1.35, 0, 0, 0, 0.02,
                                     0, 1.35, 0, 0, 0.02,
                                     0, 0, 1.35, 0, 0.03,
                                     0, 0, 0, 1, 0])
    c.drawImageRect(img, skia.Rect(0, 0, 1080, 1920), skia.SamplingOptions(), skia.Paint(ColorFilter=lift))
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, 900)], [rgba((0, 0, 0), 0.85), rgba((0, 0, 0), 0.0)])
    c.drawRect(skia.Rect(0, 0, 1080, 900), skia.Paint(Shader=sh))
    sh = skia.GradientShader.MakeLinear([(0, 1300), (0, 1920)], [rgba((0, 0, 0), 0.0), rgba((0, 0, 0), 0.85)])
    c.drawRect(skia.Rect(0, 1300, 1080, 1920), skia.Paint(Shader=sh))
    # titolo con alone
    f = bebas(250)
    w = min(1000, f.measureText(title))
    sc = w / f.measureText(title)
    c.save()
    c.translate(540, 560)
    c.scale(sc, sc)
    tw = f.measureText(title)
    c.drawString(title, -tw / 2, 0, f, skia.Paint(AntiAlias=True, Color=rgba((255, 120, 70), 0.55),
                                                   MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30)))
    c.drawString(title, -tw / 2, 0, f, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=10,
                                                   Color=rgba((0, 0, 0), 0.7)))
    c.drawString(title, -tw / 2, 0, f, G.P((255, 255, 255)))
    c.restore()
    # cartellino del giorno
    df = K.heavy(56)
    dw = df.measureText(day)
    c.save()
    c.translate(540, 330)
    c.rotate(-3)
    c.drawRect(skia.Rect(-dw / 2 - 28, -62, dw / 2 + 28, 22), G.P(RED))
    c.drawString(day, -dw / 2, 0, df, G.P((255, 255, 255)))
    c.restore()
    # la domanda in basso, nello stile delle didascalie
    hf = K.heavy(78)
    hw = hf.measureText(hook)
    hs = min(1.0, 980 / hw)
    c.save()
    c.translate(540, 1560)
    c.scale(hs, hs)
    c.drawString(hook, -hw / 2, 0, hf, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=16,
                                                   StrokeJoin=skia.Paint.kRound_Join, Color=rgba((0, 0, 0), 0.95)))
    c.drawString(hook, -hw / 2, 0, hf, G.P((206, 242, 64)))
    c.restore()
    _save(s, path)


# ---------- card "le regole del giorno" (post del giorno +2: foto TikTok/Storia 9:16 o feed IG 4:5) ----------

def rules_recap(path, title, day, rules, ask="WHICH ONE BREAKS FIRST?", h=1920):
    """Le regole dell'episodio nello stile delle card del video, con la domanda per i commenti."""
    s, c = _surface(1080, h)
    k = 1.0 if h > 1500 else 0.78          # nel 4:5 tutto un po' più piccolo
    G.vgrad(c, 0, 0, 1080, h, [(8, 9, 14), (26, 30, 44), (52, 58, 76)], (52, 58, 76), stops=[0, 0.6, 1])
    G.glow(c, 540, h, 900, (120, 130, 150), 0.25)
    top = 150 * k
    gfx.draw_text(c, f"{day} · 11:59 PM", K.bold(int(34 * k)), 540, top, color=(235, 90, 80), tracking=8 * k)
    f = bebas(int(170 * k))
    w = f.measureText(title)
    ty = top + 170 * k
    c.drawString(title, 540 - w / 2, ty, f, skia.Paint(AntiAlias=True, Color=rgba((255, 120, 70), 0.45),
                                                        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 24)))
    c.drawString(title, 540 - w / 2, ty, f, G.P((255, 255, 255)))
    y0, y1 = ty + 110 * k, h - 230 * k
    step = (y1 - y0) / len(rules)
    for i, text in enumerate(rules):
        y = y0 + i * step + (step - 190 * k) / 2
        tag = f"RULE #{i + 1}"
        tf = K.heavy(int(30 * k))
        tw = tf.measureText(tag)
        c.drawRect(skia.Rect(90, y, 90 + tw + 36 * k, y + 50 * k), G.P(RED))
        c.drawString(tag, 90 + 18 * k, y + 37 * k, tf, G.P((255, 255, 255)))
        rf = gfx.fit_font(bebas, text, 900, int(110 * k))
        c.drawString(text, 90, y + 160 * k, rf, G.P((255, 255, 255)))
        c.drawRect(skia.Rect(90, y + 176 * k, 90 + min(900, rf.measureText(text)), y + 184 * k), G.P(RED, a=0.8))
    hf = K.heavy(int(64 * k))
    hw = hf.measureText(ask)
    hs = min(1.0, 980 / hw)
    c.save()
    c.translate(540, h - 110 * k)
    c.scale(hs, hs)
    c.drawString(ask, -hw / 2, 0, hf, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=14,
                                                 StrokeJoin=skia.Paint.kRound_Join, Color=rgba((0, 0, 0), 0.95)))
    c.drawString(ask, -hw / 2, 0, hf, G.P((206, 242, 64)))
    c.restore()
    _save(s, path)


# ---------- banner YouTube (2560x1440, zona sicura 1546x423 al centro) ----------

def banner(path, name, tagline):
    s, c = _surface(2560, 1440)
    G.vgrad(c, 0, 0, 2560, 1440, [(10, 12, 20), (30, 36, 52), (60, 68, 88)], (60, 68, 88), stops=[0, 0.55, 1])
    G.fog(c, -200, 700, 2760, 1440, 3.0, a=0.6, col=(110, 120, 140), seed=4, n=18)
    # case nella nebbia
    for i, x in enumerate((300, 900, 1700, 2300)):
        G.house(c, x, 1260, 520, 420, dark=0.6, lit=(0,) if i == 1 else (), siding=(90, 100, 120))
    G.rect(c, 0, 1260, 2560, 1440, (24, 28, 34))
    G.fog(c, -200, 900, 2760, 1440, 6.0, a=0.55, col=(110, 120, 140), seed=9, n=14)
    # vignetta su tutto il banner (darkness() è pensata per il 1080 del video)
    sh = skia.GradientShader.MakeRadial((1280, 720), 1500, [rgba((3, 4, 9), 0.0), rgba((3, 4, 9), 0.75)], [0.35, 1])
    c.drawRect(skia.Rect(0, 0, 2560, 1440), skia.Paint(Shader=sh))
    # la cosa piegata a destra, il protagonista con la torcia a sinistra: il fascio attraversa il nome
    J = _bent(c, 2050, 960 - 0.47 * 560, 560, facing=-1)
    me = Figure(height=400, shade=0.15)
    mx, my = me.hip_for_feet(540, 960, POSES["flashlight"])
    hand = me.joints(mx, my, POSES["flashlight"], 1)["rhand"]
    ang = math.degrees(math.atan2(J["head"][1] - hand[1], J["head"][0] - hand[0]))
    G.beam(c, hand[0], hand[1], ang, spread=12, length=1500, a=0.2)
    me.draw(c, mx, my, POSES["flashlight"], facing=1, feet=False)
    G.glow(c, hand[0], hand[1], 60, (255, 244, 220), 0.5)
    # nome e tagline, dentro la zona sicura e tra le due figure
    f = bebas(200)
    w = f.measureText(name)
    sc = min(1.0, 900 / w)
    c.save()
    c.translate(1280, 730)
    c.scale(sc, sc)
    c.drawString(name, -w / 2, 0, f, skia.Paint(AntiAlias=True, Color=rgba((255, 120, 70), 0.45),
                                                 MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 28)))
    c.drawString(name, -w / 2, 0, f, G.P((255, 255, 255)))
    c.restore()
    c.drawRect(skia.Rect(1280 - 60, 762, 1280 + 60, 770), G.P(RED))
    gfx.draw_text(c, tagline.upper(), K.bold(36), 1280, 830, color=(225, 228, 236), tracking=5)
    _save(s, path)


def preview_avatars(paths, out):
    """Come si vedono nel cerchio a 160, 80 e 40 px."""
    s, c = _surface(len(paths) * 300, 300)
    c.clear(skia.Color(250, 250, 250))
    for i, p in enumerate(paths):
        img = skia.Image.open(str(p))
        for size, (x, y) in ((160, (20, 70)), (80, (195, 40)), (40, (215, 190))):
            c.save()
            c.clipPath(skia.Path.Circle(i * 300 + x + size / 2, y + size / 2, size / 2), skia.ClipOp.kIntersect, True)
            c.drawImageRect(img, skia.Rect(i * 300 + x, y, i * 300 + x + size, y + size),
                            skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
            c.restore()
    _save(s, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--tagline", default="Survive the night. Follow the rules.")
    ap.add_argument("--frame", default=None, help="PNG del video per la copertina")
    ap.add_argument("--story", default=None, help="in alternativa a --frame: la storia da cui prendere il fotogramma")
    ap.add_argument("--at", type=float, default=92.5, help="secondo del fotogramma (con --story)")
    ap.add_argument("--title", default="DON'T ANSWER")
    ap.add_argument("--day", default="DAY 1")
    ap.add_argument("--hook", default="DO YOU ANSWER HER?")
    ap.add_argument("--rules", default=None, help="regole separate da | per la card riassuntiva")
    ap.add_argument("--out", default="out/brand")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    avs = [out / "avatar_1_faceless.png", out / "avatar_2_bent.png", out / "avatar_3_rule4.png"]
    avatar_faceless(avs[0])
    avatar_bent(avs[1])
    avatar_rule(avs[2])
    preview_avatars(avs, out / "avatar_preview.png")
    slug = a.day.lower().replace(" ", "")
    frame = a.frame
    if frame is None and a.story:
        frame = out / f"frame_{slug}.png"
        clean_frame(a.story, a.at, frame)
    if frame:
        cover(out / f"cover_{slug}.png", frame, a.title, day=a.day, hook=a.hook)
    if a.rules:
        rules = a.rules.split("|")
        rules_recap(out / f"rules_{slug}_9x16.png", a.title, a.day, rules)
        rules_recap(out / f"rules_{slug}_4x5.png", a.title, a.day, rules, h=1350)
    banner(out / "youtube_banner.png", a.name, a.tagline)
    print("fatto:", out)


if __name__ == "__main__":
    main()
