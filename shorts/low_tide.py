"""LOW TIDE, Day 1: "The Road". Gli zombie non sanno nuotare, quindi l'isola di Eli è salva, tranne quando
la marea scende e il mare diventa una strada. Vedi docs/LOW_TIDE.md (bibbia della marea, copione, fatti).

Un solo "set" in sezione (world): la terraferma a sinistra, la strada che scende fino alle FLATS (il tratto
più basso e piatto, un quarto di miglio), il box sui pali sul bordo delle FLATS, l'isola col faro a destra.
Poi la stessa baia vista dall'alto (bay), il ballatoio del faro (gallery), il binocolo del nonno (binoc),
il cartello delle maree (sign) e la vista giù dalla botola del box (down).

La marea è una funzione sola (tide) e l'ora la prende dall'HUD: l'acqua di ogni inquadratura, i pollici sul
palo, i piedi sulla scala dipinta e i puntini sulla mappa non possono andare fuori tempo tra loro.

Ogni scena è una funzione (c, s, b, R) come in dont_answer.py; b.params["act"] sceglie la coreografia e i tempi
si legano alle parole con "@parola" (vedi _t).
"""

import math

import numpy as np
import skia

from . import gfx
from . import kinetic as K
from . import pov_gfx as G
from .gfx import mix, rgba
from .rules import _minutes, at_time
from .stick import POSES, Figure, blend, breathe, ease, walk

# ---------- la marea: un modello solo ----------

PERIOD = 12.42          # ore tra due alte maree (NOAA: 12 h 25 min)
RANGE = 12.0            # piedi tra bassa e alta
LOW_H = 15 + 47 / 60    # bassa marea alle 3:47 PM
FLATS = 4.0             # le FLATS stanno 4 ft sopra la bassa marea


def tide(h):
    """Acqua sopra la bassa marea (ft) all'ora h (mezzanotte del giorno 1 = 0; 1:46 AM = 25.77)."""
    return RANGE / 2 * (1 - math.cos(2 * math.pi * (h - LOW_H) / PERIOD))


def depth(h):
    """Acqua sopra le FLATS (ft); negativa = strada asciutta. 0 alle 6:13 PM e alle 1:46 AM."""
    return tide(h) - FLATS


# Eli parte dall'ingresso alle 6:05 e cammina in silenzio (~2 mph): mezzo miglio, bordo delle FLATS alle 6:19.
ELI_START, ELI_EDGE = 18 + 5 / 60, 18 + 19 / 60


# ---------- geometria del set (px nello spazio 1080x1920; la camera la gestisce il motore) ----------

PX = 34.0               # px per piede: uno zombie di 6 ft è alto 204 px
Y0 = 1180.0             # y delle FLATS (quota 0)
X0, X1 = 40.0, 900.0    # inizio e fine della strada
XF0, XF1 = 380.0, 660.0  # le FLATS
END = 5.0               # le estremità della strada stanno 5 ft sopra le FLATS
BOX_E = 9.0             # pavimento del box: l'alta marea (8 ft) arriva un piede sotto le assi
BOX_W = 200.0
XB = XF0 + 6            # centro del box: a cavallo del bordo delle FLATS
LH_X = 1040.0           # faro
POST_X = XF0 + 140      # palo con la scala in pollici, sulle FLATS
LADDER_X = XB - 74      # la scala di corda pende sul pendio asciutto


def road_e(x):
    """Quota del terreno (ft sopra le FLATS) alla x del set."""
    if x < X0:
        return END + 5.0 * ease(min(1.0, (X0 - x) / 130))
    if x > X1:
        return END + 6.0 * ease(min(1.0, (x - X1) / 110))
    if x < XF0:
        return END * ((XF0 - x) / (XF0 - X0)) ** 1.6
    if x > XF1:
        return END * ((x - XF1) / (X1 - XF1)) ** 1.6
    return 0.0


def ey(e):
    return Y0 - e * PX


def gy(x):
    return ey(road_e(x))


def box_geo():
    fy = ey(BOX_E)
    return XB - BOX_W / 2, fy - 6.2 * PX, XB + BOX_W / 2, fy


# ---------- ora, luce, colori ----------

def _beat_index(R):
    e = R.entry
    return next(k for k, x in enumerate(R.tl.beats) if x is e)


def hud_hours(R):
    """L'ora che l'HUD mostra in questo fotogramma (con lo stesso scorrimento del motore, Beat.roll)."""
    e = R.entry
    if not e["clock"]:
        return None
    i = _beat_index(R)
    cur = _minutes(e["clock"])
    prev = R.tl.beats[i - 1]["clock"] if i > 0 else ""
    roll = e["beat"].roll
    if prev and prev != e["clock"] and R.bs < roll:
        p = _minutes(prev)
        if cur < p:
            cur += 24 * 60
        cur = p + (cur - p) * gfx.ease_out(R.bs / roll)
    h = cur / 60
    return h + 24 if h < 12 else h


def hours(R, b):
    """Ora del mondo: params["h"] (numero, o (h0, h1[, durata]) lungo il beat) oppure quella dell'HUD."""
    v = b.params.get("h")
    if v is None:
        h = hud_hours(R)
        return 18.0 if h is None else h
    if isinstance(v, (int, float)):
        return float(v)
    h0, h1 = v[0], v[1]
    dur = v[2] if len(v) > 2 else max(0.01, R.entry["t1"] - R.entry["t0"])
    return h0 + (h1 - h0) * gfx.ease_in_out(R.bs / dur)


KEYS = [  # ora, cielo alto, cielo medio, orizzonte, mare, mare profondo, luce
    (17.3, (60, 92, 150), (236, 156, 104), (255, 210, 140), (52, 104, 134), (18, 44, 64), 1.0),
    (18.05, (40, 48, 98), (176, 98, 112), (248, 146, 96), (46, 76, 112), (14, 30, 50), 0.82),
    (18.45, (22, 28, 66), (74, 62, 108), (150, 96, 112), (32, 50, 82), (10, 20, 38), 0.58),
    (19.4, (8, 10, 26), (16, 20, 44), (30, 36, 66), (18, 28, 48), (5, 9, 18), 0.36),
]


def pal(h):
    if h >= 26:
        h = 23.0
    if h <= KEYS[0][0]:
        return KEYS[0][1:]
    for a, z in zip(KEYS, KEYS[1:]):
        if h <= z[0]:
            k = (h - a[0]) / (z[0] - a[0])
            return tuple(mix(x, y, k) if isinstance(x, tuple) else x + (y - x) * k for x, y in zip(a[1:], z[1:]))
    return KEYS[-1][1:]


def lit(col, L):
    """Un colore alla luce L (1 = sole basso, 0.36 = notte di luna): più blu e più scuro."""
    return mix(mix(col, (24, 30, 60), 0.5 * (1 - L)), (0, 0, 0), 0.5 * (1 - L))


def _p(b, key, default=None):
    return b.params.get(key, default)


def _t(R, b, key, default=None):
    """Come _p, ma un tempo scritto "@parola[:end][+x]" diventa secondi dall'inizio del beat."""
    v = b.params.get(key, default)
    return at_time(R.entry, v) if isinstance(v, str) and v.startswith("@") else v


def ramp(t, t0, dur):
    return ease((t - t0) / dur) if dur > 0 else float(t >= t0)


def screen(c):
    """Esce dalla camera: per maschere e scritte in coordinate dello schermo (ricordarsi c.restore())."""
    c.save()
    c.resetMatrix()


# ---------- personaggi ----------

DEAD_FILL = [(112, 134, 108), (98, 118, 100), (124, 140, 112), (106, 126, 116)]
ELI = Figure(height=176)
GRANDPA = Figure(height=560, fill=(70, 112, 196), extras=["hat"])
JACKET = (196, 70, 52)      # la giacca rossa di Eli: Biscuit ci sta dentro, con la testa fuori


def dead_fig(i, h_ft=5.8, scale=1.0):
    return Figure(height=h_ft * PX * scale, fill=DEAD_FILL[i % len(DEAD_FILL)], ink=(26, 32, 28))


POSES_LT = {
    "shamble": dict(torso=10, head=12, lsh=82, lel=8, rsh=70, rel=18, lhip=4, lkn=0, rhip=-4, rkn=0),
    "lean_car": dict(torso=30, head=16, lsh=70, lel=20, rsh=96, rel=10, lhip=-6, lkn=0, rhip=-14, rkn=0),
    "cling": dict(torso=-4, head=-10, lsh=158, lel=8, rsh=146, rel=20, lhip=6, lkn=0, rhip=-6, rkn=0),
    "hold": dict(torso=6, head=-6, lsh=92, lel=6, rsh=84, rel=14, lhip=6, lkn=0, rhip=-6, rkn=0),
    "shove": dict(torso=24, head=-4, lsh=96, lel=14, rsh=88, rel=20, lhip=-14, lkn=6, rhip=22, rkn=0),
    "look_up": dict(torso=-6, head=-34, lsh=92, lel=6, rsh=84, rel=14, lhip=6, lkn=0, rhip=-6, rkn=0),
    "hide": dict(torso=46, head=-30, lsh=60, lel=60, rsh=48, rel=80, lhip=118, lkn=-130, rhip=84, rkn=-120),
    "phone_low": dict(torso=40, head=10, lsh=44, lel=80, rsh=36, rel=88, lhip=118, lkn=-130, rhip=84, rkn=-120),
    "throw_back": dict(torso=-8, head=-6, lsh=40, lel=60, rsh=-150, rel=-20, lhip=10, lkn=0, rhip=-14, rkn=6),
    "throw": dict(torso=14, head=-8, lsh=30, lel=40, rsh=150, rel=-6, lhip=-12, lkn=4, rhip=18, rkn=0),
    "sneak": dict(torso=14, head=-2, lsh=30, lel=60, rsh=24, rel=66, lhip=6, lkn=-4, rhip=-6, rkn=-4),
    "look_back": dict(torso=-2, head=-10, lsh=20, lel=40, rsh=12, rel=50, lhip=4, lkn=0, rhip=-4, rkn=0),
    "climb_a": dict(torso=8, head=-20, lsh=162, lel=8, rsh=118, rel=40, lhip=70, lkn=-96, rhip=10, rkn=-10),
    "climb_b": dict(torso=8, head=-20, lsh=118, lel=40, rsh=162, rel=8, lhip=10, lkn=-10, rhip=70, rkn=-96),
    "haul": dict(torso=46, head=40, lsh=60, lel=40, rsh=84, rel=24, lhip=100, lkn=-110, rhip=90, rkn=-100),
    "sit_hold": dict(torso=10, head=14, lsh=40, lel=84, rsh=34, rel=90, lhip=96, lkn=-118, rhip=88, rkn=-112),
    "muzzle": dict(torso=18, head=24, lsh=46, lel=96, rsh=58, rel=70, lhip=96, lkn=-118, rhip=88, rkn=-112),
    "rope": dict(torso=-4, head=-14, lsh=10, lel=6, rsh=168, rel=4, lhip=4, lkn=0, rhip=-4, rkn=0),
    "rope_pull": dict(torso=8, head=6, lsh=10, lel=6, rsh=122, rel=30, lhip=4, lkn=0, rhip=-4, rkn=0),
}


def pose(name):
    return dict(POSES_LT.get(name) or POSES[name])


def eyes(c, J, facing, a=1.0, up=0.0, glow=True):
    """Occhi rossi dei morti (l'unico tratto del viso): due punti con un alone."""
    hx, hy = J["head"]
    r = J["r"]
    for s in (-1, 1):
        x = hx + facing * r * 0.34 + s * r * 0.26
        y = hy - r * 0.1 - up * r * 0.3
        if glow:
            G.glow(c, x, y, r * 0.8, (255, 40, 30), 0.35 * a)
        c.drawCircle(x, y, r * 0.13, G.P((255, 52, 40), a))


def draw_dead(c, i, x, yf, pose_, facing=-1, h_ft=5.8, scale=1.0, light=1.0, a=1.0, look=0.0, feet=True):
    fig = dead_fig(i, h_ft, scale)
    fig.shade = max(0.0, 0.85 * (1 - light))
    J = fig.draw(c, x, yf, pose_, facing=facing, alpha=a, feet=feet)
    eyes(c, J, facing, a, up=look)
    return J


def dog_head(c, x, y, s=1.0, facing=1, state="idle", light=1.0, a=1.0):
    """La testa di Biscuit (fuori dalla giacca). state: idle | bark | alert (orecchie su) | down (orecchie su,
    muso in giù verso le assi)."""
    col = lit((214, 168, 108), light)
    ink = (40, 30, 24)
    c.save()
    c.translate(x, y)
    c.scale(s * facing, s)
    if state == "down":
        c.rotate(58)
        state = "alert"
    for dx in (-6, 4):
        ear = skia.Path()
        if state == "alert":
            ear.moveTo(dx - 6, -10)
            ear.lineTo(dx, -32)
            ear.lineTo(dx + 6, -10)
        else:
            ear.moveTo(dx - 7, -10)
            ear.quadTo(dx - 15, 0, dx - 10, 12)
            ear.lineTo(dx + 1, -8)
        ear.close()
        c.drawPath(ear, G.P(ink, a, StrokeWidth=5, Style=skia.Paint.kStroke_Style, StrokeJoin=skia.Paint.kRound_Join))
        c.drawPath(ear, G.P(mix(col, (90, 60, 40), 0.45), a))
    c.drawCircle(0, 0, 18, G.P(ink, a))
    c.drawCircle(0, 0, 15.5, G.P(col, a))
    snout = skia.RRect.MakeRectXY(skia.Rect(6, -2, 28, 11), 5, 5)
    c.drawRRect(snout, G.P(ink, a, StrokeWidth=3, Style=skia.Paint.kStroke_Style))
    c.drawRRect(snout, G.P(mix(col, (255, 240, 220), 0.25), a))
    c.drawCircle(27, 1, 3.8, G.P(ink, a))
    c.drawCircle(7, -5, 2.8, G.P(ink, a))
    if state == "bark":
        c.drawLine(10, 11, 26, 20, G.P(ink, a, StrokeWidth=3))
    c.restore()


def eli(c, x, yf, p, facing=1, dog="idle", zip_k=0.0, light=1.0, a=1.0, feet=True):
    """Eli con la giacca rossa e Biscuit dentro, la testa fuori dal collo della giacca.
    zip_k 0..1 = il colletto che sale sul muso (silenzio); dog=None = niente cane."""
    ELI.shade = max(0.0, 0.8 * (1 - light))
    J = ELI.draw(c, x, yf, p, facing=facing, alpha=a, feet=feet)
    sx, sy = J["sho"]
    hx, hy = J["hip"]
    jc = lit(JACKET, light)
    body = skia.Path()
    w = ELI.height * 0.075
    fwd = facing * ELI.height * 0.05
    body.moveTo(sx - w, sy - 4)
    body.lineTo(sx + w + fwd * 0.4, sy - 4)
    body.quadTo(hx + fwd * 2.2, (sy + hy) / 2, hx + w + fwd, hy + 6)
    body.lineTo(hx - w, hy + 6)
    body.close()
    c.drawPath(body, G.P((40, 20, 16), a, StrokeWidth=7, Style=skia.Paint.kStroke_Style, StrokeJoin=skia.Paint.kRound_Join))
    c.drawPath(body, G.P(jc, a))
    for s in ("l", "r"):
        p_ = skia.Path()
        p_.moveTo(*J["sho"])
        p_.lineTo(*J[s + "elb"])
        c.drawPath(p_, G.P(jc, a, StrokeWidth=ELI.height * 0.07, StrokeCap=skia.Paint.kRound_Cap,
                           Style=skia.Paint.kStroke_Style))
    if dog:
        k = ELI.height / 230
        dx = sx + fwd * 1.3
        dy = sy + 8
        dog_head(c, dx, dy, s=k, facing=facing, state=dog, light=light, a=a)
        if zip_k > 0:
            c.drawRoundRect(skia.Rect(dx - 22 * k, dy + (14 - 30 * zip_k) * k, dx + 32 * k, dy + 22 * k), 8, 8,
                            G.P(jc, a * min(1.0, zip_k * 2)))
    return J


def car(c, x, yb, s=1.0, col=(150, 60, 56), light=1.0, blink=0.0, facing=1):
    """Berlina di lato. blink 0..1 = frecce dell'allarme accese."""
    body = lit(col, light)
    dark = mix(body, (0, 0, 0), 0.35)
    c.save()
    c.translate(x, yb)
    c.scale(s * facing, s)
    G.rrect(c, -150, -66, 150, -18, 18, body)
    p = skia.Path()
    p.moveTo(-90, -66)
    p.lineTo(-56, -110)
    p.lineTo(52, -110)
    p.lineTo(92, -66)
    p.close()
    c.drawPath(p, G.P(body))
    win = lit((120, 150, 180), light)
    for wx0, wx1 in ((-80, -8), (2, 78)):
        q = skia.Path()
        q.moveTo(wx0, -70)
        q.lineTo(wx0 + (18 if wx0 < 0 else 0), -102)
        q.lineTo(wx1 - (0 if wx1 < 0 else 16), -102)
        q.lineTo(wx1, -70)
        q.close()
        c.drawPath(q, G.P(win))
    G.rect(c, -150, -40, 150, -34, dark)
    for wx in (-92, 92):
        c.drawCircle(wx, -18, 26, G.P((22, 22, 26)))
        c.drawCircle(wx, -18, 12, G.P(lit((150, 150, 156), light)))
    G.rrect(c, 136, -60, 152, -46, 4, lit((230, 226, 210), light))
    G.rrect(c, -152, -60, -138, -46, 4, lit((200, 40, 40), light))
    if blink > 0:
        for bx in (144, -145):
            c.drawCircle(bx, -53, 10, G.P((255, 190, 60), blink))
            G.glow(c, bx, -53, 90, (255, 170, 50), 0.6 * blink)
    c.restore()


# ---------- il set in sezione ----------

def sky(c, h, t=0.0, x0=-1800, x1=2900, y0=-1200, y1=1400):
    top, midc, hor, sea, deep, L = pal(h)
    G.vgrad(c, x0, y0, x1, y1, [top, midc, hor], top, stops=[0, 0.62, 1])
    if L > 0.75:            # sole basso sopra l'isola
        k = (L - 0.75) / 0.25
        G.glow(c, 880, 880, 560, (255, 196, 120), 0.5 * k)
        c.drawCircle(880, 930, 60, G.P((255, 226, 160), 0.92 * k))
    if L < 0.6:             # stelle e luna
        k = min(1.0, (0.6 - L) / 0.2)
        rng = np.random.default_rng(5)
        for _ in range(110):
            sx, sy = rng.uniform(x0, x1), rng.uniform(y0, 900)
            c.drawCircle(sx, sy, rng.uniform(0.8, 2.4),
                         G.P((230, 236, 255), k * rng.uniform(0.3, 0.9) * (0.75 + 0.25 * math.sin(t * 2 + sx))))
        G.glow(c, 230, 330, 260, (200, 214, 255), 0.28 * k)
        c.drawCircle(230, 330, 36, G.P((236, 240, 255), k))


def water_y(d):
    return ey(d)


def back_water(c, d, h, t, x0=-1800, x1=2900):
    top, midc, hor, sea, deep, L = pal(h)
    y = water_y(d)
    G.vgrad(c, x0, y, x1, y + 700, mix(sea, hor, 0.18), deep)
    G.rect(c, x0, y + 699, x1, 3400, deep)
    if L > 0.75:            # riflesso del sole
        for k in range(10):
            yy = y + 8 + k * 18
            w = 160 - k * 10 + 20 * math.sin(t * 2 + k)
            G.rect(c, 880 - w / 2, yy, 880 + w / 2, yy + 5, (255, 220, 150), 0.5 * (1 - k / 10) * (L - 0.75) / 0.25)
    if L < 0.6:             # scia della luna
        for k in range(8):
            yy = y + 10 + k * 20
            w = 70 - k * 6 + 10 * math.sin(t * 1.6 + k)
            G.rect(c, 230 - w / 2, yy, 230 + w / 2, yy + 4, (210, 220, 255), 0.25 * (1 - k / 8))


def front_water(c, d, h, t, x0=-1800, x1=2900, current=0.0):
    """Il mare davanti a tutto: trasparente sul pelo dell'acqua, opaco un piede più giù. Quello che va sotto
    sparisce davvero (IN SIGHT 0 dev'essere vero)."""
    top, midc, hor, sea, deep, L = pal(h)
    y = water_y(d)
    mid = mix(sea, deep, 0.55)
    sh = skia.GradientShader.MakeLinear([(0, y), (0, y + 1.0 * PX)], [rgba(sea, 0.45), rgba(mid, 0.985)])
    c.drawRect(skia.Rect(x0, y, x1, y + 1.0 * PX), skia.Paint(AntiAlias=True, Shader=sh))
    G.rect(c, x0, y + 1.0 * PX - 1, x1, 3400, mid, 0.985)
    rng = np.random.default_rng(9)
    for k in range(26):    # pulviscolo sott'acqua: il blocco non è mai piatto
        px_ = rng.uniform(-200, 1300)
        py_ = y + 60 + ((rng.uniform(0, 1) + t * 0.02 * (1 + k % 3)) % 1) * 700
        c.drawCircle(px_, py_, rng.uniform(1.5, 3.5), G.P(mix(sea, (255, 255, 255), 0.3), 0.18))
    p = skia.Path()
    p.moveTo(x0, y)
    for xx in range(int(x0), int(x1) + 1, 12):
        p.lineTo(xx, y + 2.5 * math.sin(xx * 0.045 + t * 2.4) + 1.5 * math.sin(xx * 0.11 - t * 3.1))
    c.drawPath(p, G.P(mix(hor, (255, 255, 255), 0.35), 0.8, StrokeWidth=3, Style=skia.Paint.kStroke_Style))
    if current > 0 and d > 0:   # corrente sulle FLATS (da sinistra a destra: la marea che entra)
        for k in range(10):
            ph = (t * 0.55 + k / 10) % 1
            cx = XF0 - 40 + ph * (XF1 - XF0 + 120)
            cy = y + 8 + (k % 3) * min(9, d * PX / 4)
            ar = skia.Path()
            ar.moveTo(cx - 14, cy - 5)
            ar.lineTo(cx, cy)
            ar.lineTo(cx - 14, cy + 5)
            c.drawPath(ar, G.P((210, 240, 255), current * math.sin(ph * math.pi) * 0.9, StrokeWidth=3,
                               Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))


def land(c, h):
    top, midc, hor, sea, deep, L = pal(h)
    p = skia.Path()
    p.moveTo(-1800, 3400)
    for x in np.arange(-1800, 2900, 8):
        p.lineTo(x, gy(x))
    p.lineTo(2900, 3400)
    p.close()
    sh = skia.GradientShader.MakeLinear([(0, 820), (0, 1500)], [rgba(lit((92, 86, 82), L)), rgba(lit((34, 32, 34), L))])
    c.drawPath(p, skia.Paint(AntiAlias=True, Shader=sh))
    q = skia.Path()
    q.moveTo(-1800, gy(-1800))
    for x in np.arange(-1800, X0 - 20, 8):
        q.lineTo(x, gy(x))
    c.drawPath(q, G.P(lit((210, 180, 126), L), StrokeWidth=34, Style=skia.Paint.kStroke_Style))
    r = skia.Path()
    r.moveTo(X0 - 30, gy(X0 - 30))
    for x in np.arange(X0 - 30, X1 + 31, 6):
        r.lineTo(x, gy(x))
    c.drawPath(r, G.P(lit((60, 58, 58), L), StrokeWidth=22, Style=skia.Paint.kStroke_Style))
    c.drawPath(r, G.P(lit((138, 132, 124), L), StrokeWidth=12, Style=skia.Paint.kStroke_Style))
    for x in np.arange(X0 + 20, X1, 46):
        c.drawLine(x, gy(x) - 6, x, gy(x) + 6, G.P(lit((84, 80, 78), L), StrokeWidth=2))
    for x in (X0 + 90, X0 + 200, XF1 + 70, XF1 + 170):
        yb = gy(x)
        G.rect(c, x - 3, yb - 3.2 * PX, x + 3, yb, lit((226, 226, 220), L))
        G.rect(c, x - 3, yb - 3.2 * PX, x + 3, yb - 2.8 * PX, lit((210, 60, 50), L))
    rng = np.random.default_rng(3)
    for k in range(16):
        bx = X1 + 20 + k * 34 + rng.uniform(-10, 10)
        by = gy(bx) + rng.uniform(-4, 18)
        rr = rng.uniform(26, 56)
        c.drawCircle(bx, by, rr, G.P(lit(mix((70, 68, 74), (40, 40, 46), rng.random()), L)))


def tide_sign(c, x, h):
    L = pal(h)[5]
    yb = gy(x)
    G.rect(c, x - 4, yb - 150, x + 4, yb, lit((70, 70, 74), L))
    G.rrect(c, x - 62, yb - 200, x + 62, yb - 120, 6, lit((236, 232, 220), L))
    gfx.draw_text(c, "TIDE TIMES", K.bold(16), x, yb - 178, color=lit((40, 40, 46), L))
    for k in range(3):
        G.rect(c, x - 46, yb - 164 + k * 14, x + 46, yb - 158 + k * 14, lit((150, 150, 156), L) if k else (200, 60, 50))


def inch_post(c, h, a=1.0):
    """Il palo con la scala in pollici sulle FLATS: tacche ogni pollice, linea rossa a 6."""
    L = pal(h)[5]
    x = POST_X
    yb = gy(x)
    G.rect(c, x - 10, yb - 1.25 * PX - 4, x + 10, yb + 2, lit((240, 240, 236), L), a)
    for i in range(0, 13):
        y = yb - i * PX / 12
        w = 10 if i % 6 == 0 else 5
        c.drawLine(x - 10, y, x - 10 + w, y, G.P((30, 30, 34), a, StrokeWidth=1.2))
    y6 = yb - 6 * PX / 12
    c.drawLine(x - 12, y6, x + 12, y6, G.P((230, 40, 40), a, StrokeWidth=2.6))


def lighthouse(c, h, lamp=1.0, s=0.62, x=LH_X):
    """Faro sull'isola, in scala "lontano". Torre bianca a fasce rosse, ballatoio, lanterna."""
    L = pal(h)[5]
    yb = gy(x) + 6
    H_ = 560 * s
    c.save()
    c.translate(x, yb)
    w0, w1 = 70 * s, 46 * s
    p = skia.Path()
    p.moveTo(-w0, 0)
    p.lineTo(-w1, -H_)
    p.lineTo(w1, -H_)
    p.lineTo(w0, 0)
    p.close()
    c.drawPath(p, G.P(lit((236, 232, 224), L)))
    for k in (0.2, 0.55):
        q = skia.Path()
        ww0 = w0 + (w1 - w0) * k
        ww1 = w0 + (w1 - w0) * (k + 0.14)
        q.moveTo(-ww0, -H_ * k)
        q.lineTo(-ww1, -H_ * (k + 0.14))
        q.lineTo(ww1, -H_ * (k + 0.14))
        q.lineTo(ww0, -H_ * k)
        q.close()
        c.drawPath(q, G.P(lit((196, 52, 48), L)))
    G.rect(c, -w1 - 22 * s, -H_ - 10 * s, w1 + 22 * s, -H_, lit((40, 40, 44), L))
    for k in range(7):
        xx = -w1 - 18 * s + k * (2 * w1 + 36 * s) / 6
        c.drawLine(xx, -H_ - 10 * s, xx, -H_ - 40 * s, G.P(lit((40, 40, 44), L), StrokeWidth=2.5))
    c.drawLine(-w1 - 22 * s, -H_ - 40 * s, w1 + 22 * s, -H_ - 40 * s, G.P(lit((40, 40, 44), L), StrokeWidth=3))
    G.rect(c, -w1 * 0.8, -H_ - 96 * s, w1 * 0.8, -H_ - 10 * s, lit((60, 64, 72), L))
    glass = mix(lit((110, 130, 150), L), (255, 236, 170), lamp)
    G.rect(c, -w1 * 0.66, -H_ - 88 * s, w1 * 0.66, -H_ - 18 * s, glass)
    dome = skia.Path()
    dome.moveTo(-w1 * 0.9, -H_ - 96 * s)
    dome.quadTo(0, -H_ - 150 * s, w1 * 0.9, -H_ - 96 * s)
    dome.close()
    c.drawPath(dome, G.P(lit((40, 40, 44), L)))
    c.restore()
    if lamp > 0:
        G.glow(c, x, yb - H_ - 52 * s, 220, (255, 230, 160), 0.5 * lamp)
    return x, yb - H_ - 52 * s


def lh_beam(c, lx, ly, t, lamp=1.0, period=6.0, target=(XB, Y0 - 60), spread=10):
    """Il fascio che gira: visto di lato si allunga verso la strada e torna corto quando va dall'altra parte."""
    if lamp <= 0:
        return 0.0
    k = max(0.0, math.cos((t / period) % 1.0 * 2 * math.pi)) ** 3
    if k <= 0.01:
        return 0.0
    ang = math.degrees(math.atan2(target[1] - ly, target[0] - lx))
    G.beam(c, lx, ly, ang, spread=spread, length=math.hypot(target[0] - lx, target[1] - ly) * 1.3 * k + 60,
           col=(255, 240, 200), a=0.3 * lamp * k)
    return k


# ---------- il box sui pali ----------

STILTS = [XB - BOX_W / 2 + 16, XB + BOX_W / 2 - 16]     # coppia davanti (quella di destra porta la scala in piedi)


def stilts(c, h, front=True, lurch=0.0):
    L = pal(h)[5]
    x0, y0, x1, fy = box_geo()
    col = lit((104, 86, 68) if front else (70, 58, 48), L)
    dx = 0 if front else 22
    for x in STILTS:
        xb = x + dx
        c.drawLine(xb, gy(xb) + 20, xb + lurch, fy, G.P(col, StrokeWidth=18))
    if front:
        for k0, k1 in ((0.05, 0.42), (0.42, 0.8)):
            ya, yb_ = fy + (Y0 - fy) * k0, fy + (Y0 - fy) * k1
            c.drawLine(STILTS[0] + lurch * (1 - k0), ya, STILTS[1] + lurch * (1 - k1), yb_,
                       G.P(mix(col, (0, 0, 0), 0.15), StrokeWidth=8))
            c.drawLine(STILTS[1] + lurch * (1 - k0), ya, STILTS[0] + lurch * (1 - k1), yb_,
                       G.P(mix(col, (0, 0, 0), 0.15), StrokeWidth=8))


def gauge(c, h, a=1.0, hot=None):
    """Scala dipinta sul palo di destra (in piedi sulle FLATS): 0-9 FT. hot = piede da evidenziare in rosso."""
    L = pal(h)[5]
    x = STILTS[1]
    G.rect(c, x - 9, ey(9.0), x + 9, Y0, lit((238, 234, 224), L), a)
    for ft in range(0, 10):
        y = ey(ft)
        c.drawLine(x - 9, y, x + 9, y, G.P((24, 24, 28), a, StrokeWidth=2.6))
        c.drawLine(x - 9, ey(ft + 0.5), x, ey(ft + 0.5), G.P((24, 24, 28), a, StrokeWidth=1.4))
        if (ft % 2 == 0 and ft) or ft == 5 or hot == ft:
            col = (240, 60, 50) if hot == ft else lit((244, 242, 234), L)
            gfx.draw_text(c, str(ft), K.heavy(30 if hot != ft else 44), x + 16, y + (10 if hot != ft else 15),
                          color=col, alpha=a, align="left")
    gfx.draw_text(c, "FT", K.bold(16), x + 16, ey(9.0) + 14, color=lit((244, 242, 234), L), alpha=a, align="left")


def box(c, h, t, cutaway=False, inner=None, lurch=0.0, dust=0.0):
    """Il box REFUGE. cutaway = senza parete davanti (si vede dentro: inner(c, geo))."""
    L = pal(h)[5]
    x0, y0, x1, fy = box_geo()
    c.save()
    if lurch:
        c.translate(lurch, 0)
        c.rotate(lurch * 0.06)
    wood = lit((132, 106, 80), L)
    dark = mix(wood, (0, 0, 0), 0.5)
    G.rect(c, x0, y0, x1, fy + 14, dark if cutaway else wood)
    if cutaway:
        for k in range(1, 6):
            yy = y0 + (fy - y0) * k / 6
            c.drawLine(x0, yy, x1, yy, G.P(mix(dark, (0, 0, 0), 0.25), StrokeWidth=2))
        G.rect(c, x1 - 66, y0 + 36, x1 - 20, y0 + 84, lit((40, 52, 86), L))          # finestrella verso l'isola
        G.rect(c, x0 + 6, y0 + 40, x0 + 46, fy, (14, 12, 12))                       # porta (lato terraferma)
        if inner:
            inner(c, (x0, y0, x1, fy))
        G.rect(c, x0, fy, x1, fy + 14, wood)                                          # pavimento di taglio
        for k in range(9):                                                            # assi con le fessure
            xx = x0 + 6 + k * (BOX_W - 12) / 8
            c.drawLine(xx, fy + 1, xx, fy + 13, G.P((10, 8, 8), StrokeWidth=2.4))
        G.rect(c, x0 - 7, y0, x0 + 5, fy + 14, wood)
        G.rect(c, x1 - 5, y0, x1 + 7, fy + 14, wood)
    else:
        for k in range(1, 8):
            xx = x0 + BOX_W * k / 8
            c.drawLine(xx, y0, xx, fy + 14, G.P(mix(wood, (0, 0, 0), 0.2), StrokeWidth=2))
        G.rect(c, x0 + 8, y0 + 40, x0 + 48, fy, (14, 12, 12))                        # porta
        gfx.draw_text(c, "REFUGE", K.heavy(36), XB + 22, y0 + 86, color=lit((242, 238, 228), L))
    roof = skia.Path()
    roof.moveTo(x0 - 18, y0 + 8)
    roof.lineTo(XB, y0 - 44)
    roof.lineTo(x1 + 18, y0 + 8)
    roof.close()
    c.drawPath(roof, G.P(lit((70, 60, 54), L)))
    c.restore()
    if dust > 0:     # polvere che cade dalle fessure quando lo scuotono
        rng = np.random.default_rng(int(t * 20))
        for k in range(30):
            dx = rng.uniform(x0, x1)
            dy = fy + 14 + rng.uniform(0, 260) * dust
            c.drawCircle(dx, dy, rng.uniform(1.5, 3.5), G.P((210, 196, 170), 0.6 * dust))


def rope_ladder(c, h, t, k_up=0.0, a=1.0, sway=1.0):
    """Scala di corda dalla porta al pendio asciutto. k_up 0..1 = tirata su."""
    L = pal(h)[5]
    x0, y0, x1, fy = box_geo()
    tx, ty = x0 + 26, fy + 4
    full = gy(LADDER_X) - ty
    length = full * (1 - 0.97 * ease(k_up))
    if length < 6:
        return
    col = lit((176, 150, 110), L)
    sw = sway * 8 * math.sin(t * 1.3)
    bx = tx + (LADDER_X - tx) * (length / full)
    for dx in (-12, 12):
        p = skia.Path()
        p.moveTo(tx + dx, ty)
        p.quadTo(tx + dx + sw * 0.5, ty + length * 0.5, bx + dx + sw, ty + length)
        c.drawPath(p, G.P(col, a, StrokeWidth=3.5, Style=skia.Paint.kStroke_Style))
    n = max(1, int(length / 26))
    for i in range(1, n + 1):
        f = i / n
        x = tx + (bx + sw - tx) * f
        y = ty + length * f
        c.drawLine(x - 13, y, x + 13, y, G.P(col, a, StrokeWidth=5, StrokeCap=skia.Paint.kRound_Cap))


def chip(c, x, y, label, value, col=(240, 240, 244), a=1.0, size=30, anchor=None):
    """Pastiglia scura con etichetta e numero, attaccata a un oggetto (linea fino ad anchor)."""
    if a <= 0:
        return
    f1 = gfx.mono(size * 0.62, "Medium")
    f2 = gfx.mono(size, "SemiBold")
    w1 = gfx.text_width(label, f1, 2)
    w2 = f2.measureText(value)
    w = w1 + w2 + 44
    if anchor:
        c.drawLine(anchor[0], anchor[1], x, y, G.P(col, 0.7 * a, StrokeWidth=2.5))
        c.drawCircle(anchor[0], anchor[1], 5, G.P(col, a))
    r = skia.RRect.MakeRectXY(skia.Rect(x - w / 2, y - size * 0.95, x + w / 2, y + size * 0.55), 14, 14)
    c.drawRRect(r, G.P((12, 12, 16), 0.92 * a))
    c.drawRRect(r, G.P(col, 0.85 * a, StrokeWidth=2.5, Style=skia.Paint.kStroke_Style))
    gfx.draw_text(c, label, f1, x - w / 2 + 16, y - 2, color=(196, 198, 206), alpha=a, align="left", tracking=2)
    gfx.draw_text(c, value, f2, x + w / 2 - 16, y + 2, color=col, alpha=a, align="right")


def tag(c, x, y, text_, col=(255, 200, 90), a=1.0, size=24):
    """Etichetta di testo semplice su pastiglia (niente numero)."""
    if a <= 0:
        return
    f = K.bold(size)
    w = gfx.text_width(text_, f, 2) + 40
    r = skia.RRect.MakeRectXY(skia.Rect(x - w / 2, y - size * 1.1, x + w / 2, y + size * 0.55), 14, 14)
    c.drawRRect(r, G.P((12, 12, 16), 0.9 * a))
    c.drawRRect(r, G.P(col, 0.85 * a, StrokeWidth=2.5, Style=skia.Paint.kStroke_Style))
    gfx.draw_text(c, text_, f, x, y, color=col, alpha=a, tracking=2)


# ---------- i 14 attorno al box ----------

# altezza (ft), x, davanti ai pali? Più alti = la testa riemerge prima. Tutti sulle FLATS o sul bordo.
CROWD = [
    (6.00, XB + 40, 1), (5.96, XB + 150, 1), (5.92, XB - 60, 0), (5.88, XB + 96, 0), (5.84, XB + 10, 1),
    (5.80, XB + 200, 0), (5.76, XB - 20, 0), (5.72, XB + 124, 1), (5.68, XB + 240, 1), (5.64, XB + 64, 0),
    (5.60, XB + 270, 0), (5.56, XB + 178, 1), (5.53, XB - 40, 1), (5.50, XB + 300, 0),
]


def crowd(c, h, t, d, mode="cling", n=14, light=1.0, slap=0.0, shove=0.0, a=1.0):
    """I morti attorno al box. mode: cling (braccia su, schiaffi ai pali) | hold (mani sulle traverse
    all'altezza delle spalle: sott'acqua non spunta niente) | look (come hold, testa in su).
    shove 0..1 = spingono tutti insieme."""
    for i, (hf, x, fr) in enumerate(CROWD[:n]):
        base = pose({"look": "look_up", "hold": "hold"}.get(mode, "cling"))
        if mode == "hold":
            base["torso"] += 7 * min(1.0, max(0.0, d) / 2)
        if mode == "cling":
            w = math.sin(t * 7 + i * 1.7) * 16 * slap
            base["lsh"] += w
            base["rsh"] -= w
            base["torso"] += 7 * min(1.0, max(0.0, d) / 2)
            if shove:
                base = blend(base, pose("shove"), shove * (0.6 + 0.4 * math.sin(t * 14 + i)))
        facing = 1 if x < XB + 60 else -1
        draw_dead(c, i, x, gy(x), breathe(base, t + i, 0.6), facing=facing, h_ft=hf, light=light, a=a,
                  look=1.0 if mode == "look" else 0.0)


def hands_ghost(c, d, a=0.22):
    """Le mani grigie ancora strette ai pali e alle traverse sotto il pelo dell'acqua: l'indizio per chi
    riguarda (le teste sono sparite, le mani no)."""
    for i, (hf, x, fr) in enumerate(CROWD):
        sx = STILTS[i % 2] + (-14 if i % 2 == 0 else 14) + (i // 2 % 3 - 1) * 30
        y = ey(hf - 1.0 - 0.12 * (i % 3))
        if y > water_y(d) + 10:
            c.drawOval(skia.Rect(sx - 13, y - 9, sx + 13, y + 9), G.P((160, 180, 156), a))


# ---------- scena: il set ----------

def world(c, s, b, R):
    act = _p(b, "act", "wide")
    h = hours(R, b)
    t = R.t
    d = depth(h)
    if act in ACTS_D:
        d = ACTS_D[act](R, b, h, d)
    L = pal(h)[5]
    st = {"h": h, "d": d, "L": L, "lurch": 0.0, "dust": 0.0}
    if act in PRE:
        PRE[act](R, b, st)
    sky(c, h, t=t)
    back_water(c, d, h, t)
    lamp = ramp(h, 18.35, 0.1) if _p(b, "lamp") is None else _p(b, "lamp")
    lx, ly = lighthouse(c, h, lamp=lamp)
    land(c, h)
    tide_sign(c, X0 - 40, h)
    for cx, col in ((-150, (60, 86, 140)), (-400, (150, 60, 56)), (-640, (90, 96, 104))):
        car(c, cx, gy(cx) + 4, s=0.9, col=col, light=L)
    stilts(c, h, front=False, lurch=st["lurch"])
    box(c, h, t, cutaway=_p(b, "cutaway", False), lurch=st["lurch"], dust=st["dust"],
        inner=lambda c_, g: INNER.get(act, _no)(c_, g, R, b, st))
    stilts(c, h, front=True, lurch=st["lurch"])
    gauge(c, h, hot=_p(b, "gauge_hot"))
    rope_ladder(c, h, t, k_up=LADDER.get(act, lambda R, b: _p(b, "ladder", 0.0))(R, b))
    inch_post(c, h)
    ACTS.get(act, _no)(c, s, b, R, st)
    front_water(c, d, h, t, current=_p(b, "current", 1.0 if 0 < d < 3 else 0.0))
    if lamp > 0:
        lh_beam(c, lx, ly, t, lamp=lamp)
    dk = _p(b, "dark", 0.0)
    if dk:
        G.darkness(c, dk, lights=[(lx, ly, 260, 0.9), (230, 330, 260, 0.6)] + list(_p(b, "lights", [])))
    OVER.get(act, _no)(c, s, b, R, st)


def _no(*a, **k):
    return None


# ---------- coreografie del set ----------

HOOK_DEAD = ((-330, 5.9), (-262, 5.6), (-200, 6.0), (-136, 5.7), (-72, 5.8), (-20, 5.65))


def d_hook(R, b, h, d):
    """Prima tutta sott'acqua; su "OUT" il mare si ritira in 1.4 s e la strada emerge."""
    out = _t(R, b, "drain_at", 3.2)
    return 6.6 - 9.8 * gfx.ease_in_out((R.bs - out) / 1.4)


def act_hook(c, s, b, R, st):
    """Golden hour: i morti sul bagnasciuga. Uno è già in acqua fino alle ginocchia: l'onda lo butta giù su
    "SWIM" e la corrente se lo porta via (l'acqua non li uccide: li trascina)."""
    t = R.bs
    d = st["d"]
    out = _t(R, b, "drain_at", 3.2)
    for i, (x, hf) in enumerate(HOOK_DEAD):
        look = pose("shamble") if t < out + 0.4 else blend(pose("shamble"), walk(R.t * 0.6, 0.5), 0.3)
        draw_dead(c, i + 3, x, gy(x), breathe(look, R.t + i), facing=1, h_ft=hf)
    hit = _t(R, b, "hit_at", 0.7)
    wx = 70.0
    if t < hit:
        yb = water_y(d) + 2.2 * PX
        draw_dead(c, 9, wx, yb, breathe(pose("shamble"), R.t), facing=1, h_ft=5.9)
    else:
        g = t - hit
        yb = water_y(d) - 4 + 70 * ease((g - 1.3) / 1.2)
        xx = wx + 420 * ease(g / 2.8)
        c.save()
        c.translate(xx, yb)
        c.rotate(-84 - 40 * math.sin(g * 2.6))
        J = dead_fig(9, 5.9).draw(c, 0, 0, pose("shamble"), facing=1, feet=False)
        eyes(c, J, 1, a=max(0.0, 1 - g / 1.4))
        c.restore()


def over_hook(c, s, b, R, st):
    """L'onda che si arriccia sul primo e lo ribalta su "SWIM"."""
    t = R.bs
    hit = _t(R, b, "hit_at", 0.7)
    g = t - (hit - 0.45)
    if 0 <= g < 1.3:
        y = water_y(st["d"])
        x = 250 - 160 * ease(g / 0.5)
        hgt = 210 * math.sin(min(1.0, g / 0.55) * math.pi * 0.5) * (1 - ease((g - 0.5) / 0.8))
        p = skia.Path()
        p.moveTo(x - 220, y + 6)
        p.quadTo(x - 80, y - hgt * 0.4, x - 20, y - hgt)
        p.quadTo(x + 30, y - hgt * 1.1, x + 10, y - hgt * 0.6)
        p.quadTo(x + 120, y - 10, x + 260, y + 6)
        p.close()
        c.drawPath(p, G.P((70, 130, 160), 0.92))
        c.drawPath(p, G.P((240, 250, 255), 0.9, StrokeWidth=8, Style=skia.Paint.kStroke_Style))


ROAD_DEAD = ((X0 + 10, 5.9), (X0 + 64, 5.6), (X0 - 40, 6.0), (X0 + 120, 5.7), (X0 + 176, 5.65))


def act_arrive(c, s, b, R, st):
    """6:04 PM: Eli arriva di corsa e si butta dietro l'auto blu; dall'altra parte un morto appoggia la mano
    sul cofano a un palmo dalla sua testa ("Day one"). I morti sull'inizio della strada."""
    L = st["L"]
    t = R.bs
    slap = _t(R, b, "slap_at", 0.9)
    for i, (x, hf) in enumerate(ROAD_DEAD):
        draw_dead(c, i, x, gy(x), breathe(pose("shamble"), R.t + i), facing=-1, h_ft=hf, light=L)
    x = -20 - 60 * ramp(t, 0.0, slap)
    p = blend(walk(R.t * 0.8, 0.6), pose("lean_car"), ramp(t, slap - 0.25, 0.25))
    draw_dead(c, 7, x, gy(x), p, facing=-1, h_ft=5.9, light=L)
    car(c, -150, gy(-150) + 4, s=0.9, col=(60, 86, 140), light=L)
    run_end = 0.55
    ex = -560 + 250 * ramp(t, 0.0, run_end)
    if t < run_end:
        eli(c, ex, gy(ex), blend(walk(R.t * 2.2, 1.3), pose("sneak"), 0.3), facing=1, light=L)
    else:
        eli(c, ex, gy(ex), breathe(pose("hide"), R.t), facing=1, light=L, dog="alert" if t > slap else "idle")


def act_hide(c, s, b, R, st):
    """Primo piano dietro l'auto: il telefono all'1% che si spegne su "WRONG"; i morti fermi sulla strada."""
    L = st["L"]
    t = R.bs
    for i, (x, hf) in enumerate(ROAD_DEAD + ((-80, 5.9),)):
        draw_dead(c, i, x, gy(x), breathe(pose("shamble"), R.t + i), facing=-1, h_ft=hf, light=L)
    car(c, -150, gy(-150) + 4, s=0.9, col=(60, 86, 140), light=L)
    ex = -310
    J = eli(c, ex, gy(ex), breathe(pose("phone_low"), R.t), facing=1, light=L, dog="idle")
    hx, hy = J["rhand"]
    off = _t(R, b, "dies_at", 99)
    c.save()
    c.translate(hx + 10, hy - 6)
    c.rotate(-12)
    G.rrect(c, -15, -26, 15, 26, 5, (14, 14, 16))
    if t < off:
        G.rrect(c, -12, -22, 12, 22, 4, (40, 46, 70))
        G.glow(c, 0, 0, 70, (150, 170, 255), 0.35)
        G.rect(c, -7, -4, 7, 4, (230, 230, 230))
        G.rect(c, -6, -3, -5, 3, (240, 60, 50))
    c.restore()
    if t < off + 0.8:
        chip(c, ex + 130, gy(ex) - 200, "PHONE", "1%" if t < off else "0%", col=(255, 90, 80), size=30,
             a=ramp(t, 0.05, 0.2), anchor=(hx + 8, hy - 20))


def act_throw(c, s, b, R, st):
    """Si alza dietro l'auto e lancia il sasso lontano lungo la spiaggia (esce dall'inquadratura in alto)."""
    L = st["L"]
    t = R.bs
    for i, (x, hf) in enumerate(ROAD_DEAD):
        draw_dead(c, i, x, gy(x), breathe(pose("shamble"), R.t + i), facing=-1, h_ft=hf, light=L)
    car(c, -150, gy(-150) + 4, s=0.9, col=(60, 86, 140), light=L)
    ex = -310
    th = _t(R, b, "throw_at", 0.5)
    g = t - th
    if g < -0.4:
        p = pose("hide")
    elif g < 0:
        p = blend(pose("hide"), pose("throw_back"), ease((g + 0.4) / 0.4))
    elif g < 0.25:
        p = blend(pose("throw_back"), pose("throw"), ease(g / 0.25))
    else:
        p = blend(pose("throw"), pose("hide"), ease((g - 0.6) / 0.5))
    J = eli(c, ex, gy(ex), p, facing=-1, light=L, dog="idle")
    if 0.05 <= g < 1.2:
        for j in range(6):
            k = max(0.0, (g - 0.05 - j * 0.03) / 0.8)
            sx = J["sho"][0] - 900 * k
            sy = J["sho"][1] - 80 - 700 * k + 500 * k * k
            c.drawCircle(sx, sy, 13 - j * 1.6, G.P(lit((190, 186, 176), L), 1.0 - j * 0.16))


def act_walk_side(c, s, b, R, st):
    """Sulla strada, a metà: la campana e la testa che scatta indietro verso la spiaggia (lui sa cosa fa un suono)."""
    L = st["L"]
    t = R.bs
    x = X0 + 110
    turn = _t(R, b, "turn_at", 0.3)
    k = ramp(t, turn, 0.18)
    p = blend(blend(walk(R.t * 0.7, 0.6), pose("sneak"), 0.5), pose("look_back"), k)
    eli(c, x, gy(x), p, facing=1 if k < 0.5 else -1, light=L, dog="alert" if k > 0.5 else "idle")
    if t > turn - 0.3:
        G.sound_rings(c, LH_X, gy(LH_X) - 360, R.t, col=(255, 230, 170), n=3, r_max=700, a=0.5, period=1.1)


def act_edge(c, s, b, R, st):
    """Al bordo delle FLATS, sull'asciutto: davanti un quarto di miglio d'acqua che sale. Un Eli "fantasma"
    prova a guadare: i pollici salgono mentre attraversa e a metà passano la linea rossa, e cade."""
    L = st["L"]
    t = R.bs
    ex = XF0 - 46
    eli(c, ex, gy(ex), breathe(pose("stand_tense"), R.t), facing=1, light=L)
    gs = _t(R, b, "ghost_at", 1.6)
    if t >= gs:
        g = (t - gs) / 2.2
        frac = min(1.0, g)
        fall = next((f / 100 for f in range(101) if depth(st["h"] + f / 100 * 7.5 / 60) * 12 >= 6), 2.0)
        fell = frac >= fall
        frac = min(frac, fall)
        gx = XF0 + 20 + (XF1 - XF0 - 40) * frac
        gd = 0.5 if fell else depth(st["h"] + frac * 7.5 / 60)    # un quarto di miglio a 2 mph
        a = 0.62 * (1 - ramp(t, gs + 2.6, 0.4))
        if not fell:
            eli(c, gx, Y0, blend(walk(R.t * 1.2, 0.8), pose("sneak"), 0.4), facing=1, light=L, a=a, dog=None)
        else:
            c.save()
            c.translate(gx, Y0 - 20)
            c.rotate(-70)
            ELI.draw(c, 0, 0, pose("stand"), facing=1, alpha=a, feet=False)
            c.restore()
        st["ghost"] = (gx, gd, fell, a)


def over_edge(c, s, b, R, st):
    d = st["d"]
    inch = max(0.0, d * 12)
    col = (255, 90, 80) if inch >= 6 else (120, 200, 255)
    chip(c, POST_X + 60, gy(POST_X) - 120, "WATER", f"{inch:.0f} IN", col=col, size=32, anchor=(POST_X, water_y(d)))
    g = st.get("ghost")
    if g:
        gx, gd, fell, a = g
        chip(c, gx + 30, Y0 + 70, "IF HE WADES", f"{gd * 12:.0f} IN", col=(255, 90, 80) if fell else (255, 200, 90),
             a=min(1.0, a * 2.2), size=30)


def act_run(c, s, b, R, st):
    """L'ultima risorsa: corre alla scala di corda; dietro, il primo della fila entra nell'inquadratura."""
    L = st["L"]
    t = R.bs
    run = _t(R, b, "run_at", 0.5)
    k = ramp(t, run, 0.9)
    x = XF0 - 46 + (LADDER_X - 16 - (XF0 - 46)) * k
    p = blend(walk(R.t * 2.0, 1.2), pose("stand"), 0.2) if 0 < k < 1 else (pose("reach_up") if k >= 1 else pose("stand_tense"))
    eli(c, x, gy(x), p, facing=-1 if k < 1 else 1, light=L)
    head = _t(R, b, "head_at", 99)
    if t > head:
        xx = X0 - 60 + 80 * ramp(t, head, 1.2)
        draw_dead(c, 0, xx, gy(xx), blend(walk(R.t * 2.2, 1.4), pose("shamble"), 0.3), facing=1, h_ft=5.9, light=L)


def over_run(c, s, b, R, st):
    k = ramp(R.bs, _t(R, b, "chip_at", 1.4), 0.25)
    x0, y0, x1, fy = box_geo()
    tag(c, XB + 50, y0 - 100, "REAL: SOME TIDAL ROADS HAVE THESE", col=(255, 200, 90), a=k, size=19)


def ladder_haul(R, b):
    up = _t(R, b, "haul_at")
    return 0.0 if up is None else ramp(R.bs, up, 0.9)


def act_climb(c, s, b, R, st):
    """Sale con Biscuit nella giacca, entra, tira su la scala; i morti arrivano di corsa da sinistra."""
    L = st["L"]
    t = R.bs
    x0, y0, x1, fy = box_geo()
    climb_end = _t(R, b, "in_at", 1.3)
    if t < climb_end:
        k = ease(t / climb_end)
        yfeet = gy(LADDER_X) + (fy - gy(LADDER_X)) * k
        p = pose("climb_a" if int(R.t * 5) % 2 else "climb_b")
        eli(c, LADDER_X - 4, yfeet, p, facing=1, light=L)
    elif t < climb_end + 1.6:   # dalla porta: si vede che tira su
        k = ladder_haul(R, b)
        eli(c, x0 + 30, fy, blend(pose("haul"), pose("sit_hold"), k), facing=-1, light=L, a=1.0)
    arrive = _t(R, b, "arrive_at", 1.8)
    for i, (hf, x, fr) in enumerate(CROWD[:9]):
        g = t - arrive - i * 0.12
        start = X0 - 160 - i * 50
        xx = start + (x - start) * ease(g / 1.0) if g > 0 else start
        p = blend(walk(R.t * 2.0 + i * 0.3, 1.4), pose("cling"), ease((g - 0.8) / 0.4))
        if g > -0.6:
            draw_dead(c, i, xx, gy(xx), p, facing=1 if xx < XB + 60 else -1, h_ft=hf, light=L)


def pre_shake(R, b, st):
    """La scala che sbatte: tutti spingono insieme, il box barcolla, cade polvere dalle assi."""
    t = R.bs
    sh = _t(R, b, "shove_at", 0.6)
    calm = _t(R, b, "calm_at", 3.0)
    g = t - sh
    amp = 1.0 if t < calm else max(0.0, 1 - (t - calm) / 0.8)
    if g >= 0:
        st["lurch"] = 9 * math.sin(g * 16) * amp
        st["dust"] = min(1.0, g / 0.3) * amp
    st["shove"] = amp * ramp(t, sh, 0.15)


def coil(c, x, y, L):
    for r in (16, 11, 6):
        c.drawCircle(x, y, r, G.P(lit((176, 150, 110), L), StrokeWidth=3, Style=skia.Paint.kStroke_Style))


def inner_shake(c, g, R, b, st):
    """Dentro: Eli stringe Biscuit; quando abbaia la zip sale sul muso."""
    L = max(st["L"], 0.6)
    x0, y0, x1, fy = g
    t = R.bs
    zp = _t(R, b, "zip_at", 99)
    k = ramp(t, zp, 0.35)
    barking = t < zp and st.get("shove", 0) > 0.2 and (R.t * 5) % 1 < 0.5
    eli(c, XB - 6, fy, breathe(blend(pose("sit_hold"), pose("muzzle"), k), R.t, 0.4), facing=1, light=L,
        dog="bark" if barking else "alert", zip_k=k)
    coil(c, x0 + 50, fy - 8, L)


def act_shake(c, s, b, R, st):
    crowd(c, st["h"], R.t, st["d"], mode="cling", light=st["L"], slap=0.4, shove=st.get("shove", 0.0))


def act_rise(c, s, b, R, st):
    """L'acqua sale sul palo: le teste vanno sotto (il pelo dell'acqua le copre davvero)."""
    crowd(c, st["h"], R.t, st["d"], mode="hold", light=st["L"])


def over_rise(c, s, b, R, st):
    d = st["d"]
    hands_ghost(c, d, a=0.2)
    n = sum(1 for hf, x, fr in CROWD if hf - d > 0.02)
    x0, y0, x1, fy = box_geo()
    if _p(b, "insight", True):
        col = (120, 200, 255) if n else (220, 222, 230)
        chip(c, XB + 250, y0 + 60, "IN SIGHT", str(n), col=col, size=44)
    tick = _t(R, b, "tick_at")
    if tick is not None and R.bs >= tick:   # quanto sono alti: tratteggio dalla testa più alta alla scala
        k = ramp(R.bs, tick, 0.3) * (1 - ramp(R.bs, tick + 2.4, 0.3))
        y = ey(CROWD[0][0])
        c.drawLine(CROWD[0][1] - 30, y, STILTS[1] + 60, y,
                   G.P((255, 200, 90), 0.9 * k, StrokeWidth=3, PathEffect=skia.DashPathEffect.Make([10, 8], 0)))
        tag(c, STILTS[1] + 130, y - 26, "THEIR HEADS · 6 FT", col=(255, 200, 90), a=k, size=18)
    egg = _t(R, b, "egg_at")
    if egg is not None and 0 <= R.bs - egg < 5 / 60:    # due occhi rossi sotto il pelo dell'acqua, 5 fotogrammi
        y = water_y(d) + 30
        for dx in (-8, 8):
            c.drawCircle(XB + 210 + dx, y, 4, G.P((255, 50, 40), 0.6))


def inner_high(c, g, R, b, st):
    """Alta marea: l'acqua nera un piede sotto le assi."""
    L = max(st["L"], 0.55)
    x0, y0, x1, fy = g
    eli(c, XB - 30, fy, breathe(pose("sit_hold"), R.t, 0.3), facing=1, light=L, dog="idle")
    coil(c, x0 + 50, fy - 8, L)


def inner_freeze(c, g, R, b, st):
    """Notte. Biscuit drizza le orecchie e guarda giù tra le assi; la mano di Eli gli chiude il muso."""
    L = max(st["L"], 0.6)
    x0, y0, x1, fy = g
    t = R.bs
    fr = _t(R, b, "freeze_at", 0.6)
    hand = _t(R, b, "hand_at", 99)
    k = ramp(t, hand, 0.3)
    eli(c, XB - 6, fy, breathe(blend(pose("sit_hold"), pose("muzzle"), k), R.t, 0.2), facing=1, light=L,
        dog=("down" if t >= fr + 0.5 else "alert") if t >= fr else "idle", zip_k=0.0)
    if t >= fr + 0.5:     # lo sguardo: una linea tratteggiata giù tra le assi
        J = ELI.joints(*ELI.hip_for_feet(XB - 6, fy, pose("sit_hold")), pose("sit_hold"), 1)
        sx, sy = J["sho"][0] + 12, J["sho"][1] + 30
        k2 = ramp(t, fr + 0.5, 0.4)
        c.drawLine(sx, sy, sx + 30, fy + 60, G.P((255, 200, 90), 0.7 * k2, StrokeWidth=3,
                                                 PathEffect=skia.DashPathEffect.Make([8, 7], 0)))
    coil(c, x0 + 50, fy - 8, L)


def act_gauge_down(c, s, b, R, st):
    crowd(c, st["h"], R.t, st["d"], mode="look", light=st["L"])


def act_ledger(c, s, b, R, st):
    crowd(c, st["h"], R.t, st["d"], mode="hold", light=st["L"])


def over_gauge_down(c, s, b, R, st):
    hands_ghost(c, st["d"], a=0.28)


ACTS = {"hook": act_hook, "arrive": act_arrive, "hide": act_hide, "throw": act_throw, "walk_side": act_walk_side,
        "edge": act_edge, "run": act_run, "climb": act_climb, "shake": act_shake, "rise": act_rise,
        "high": act_ledger, "freeze": act_rise, "gauge_down": act_gauge_down}
ACTS_D = {"hook": d_hook}
PRE = {"shake": pre_shake}
OVER = {"hook": over_hook, "edge": over_edge, "run": over_run, "rise": over_rise, "high": over_rise,
        "gauge_down": over_gauge_down}
INNER = {"shake": inner_shake, "high": inner_high, "freeze": inner_freeze, "rise": inner_high}
_UP = lambda R, b: 1.0
LADDER = {"climb": ladder_haul, "shake": _UP, "rise": _UP, "high": _UP, "freeze": _UP, "gauge_down": _UP}


# ---------- scena: il cartello delle maree ----------

def sign(c, s, b, R):
    """Il cartello all'ingresso della strada, in primo piano: gli orari di oggi. Il conto alla rovescia si
    stacca dalle 6:13 (l'ora è quella dell'HUD)."""
    h = hours(R, b)
    top, midc, hor, sea, deep, L = pal(h)
    G.vgrad(c, -300, -300, 1380, 1250, [top, midc, hor], top, stops=[0, 0.6, 1])
    G.vgrad(c, -300, 1250, 1380, 2300, mix(sea, hor, 0.15), deep)
    G.rect(c, -300, 1330, 1380, 2300, lit((196, 168, 118), L))
    G.rect(c, 500, 900, 580, 2300, lit((70, 70, 74), L))
    y0 = 330
    G.rrect(c, 110, y0, 970, y0 + 700, 26, lit((240, 236, 224), L))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(110, y0, 970, y0 + 700), 26, 26),
                G.P((40, 40, 46), StrokeWidth=10, Style=skia.Paint.kStroke_Style))
    ink = lit((34, 34, 40), L)
    gfx.draw_text(c, "TIDAL ROAD", K.heavy(70), 540, y0 + 100, color=ink)
    gfx.draw_text(c, "UNDER WATER TODAY", K.bold(40), 540, y0 + 180, color=lit((90, 92, 100), L))
    G.rrect(c, 160, y0 + 220, 920, y0 + 370, 18, (200, 46, 40))
    gfx.draw_text(c, "6:13 PM – 1:46 AM", gfx.mono(66, "SemiBold"), 540, y0 + 320, color=(255, 255, 255))
    gfx.draw_text(c, "NEVER RACE THE TIDE", K.heavy(52), 540, y0 + 560, color=ink)
    gfx.draw_text(c, "WREN ISLAND CAUSEWAY", K.bold(26), 540, y0 + 640, color=lit((90, 92, 100), L), tracking=3)
    left = max(0.0, round((18 + 13 / 60 - h) * 3600))
    k = ramp(R.bs, _t(R, b, "peel_at", 0.8), 0.45)
    if k > 0:
        x = 380 + 160 * k
        y = y0 + 300 + 150 * k
        chip(c, x, y, "FLOODS IN", f"{int(left // 60)}:{int(left % 60):02d}", col=(255, 200, 90), size=56)


# ---------- scena: la mappa dall'alto ----------

ROAD_A = (560, 1560)     # ingresso dalla terraferma
ROAD_B = (540, 620)      # arrivo sull'isola
F0, F1 = 0.5, 0.75       # le FLATS sulla strada (frazioni dal lato terraferma): mezzo miglio, poi un quarto
LHM = (440, 420)         # il faro sulla mappa


def road_xy(v):
    """Punto della strada a frazione v (0 terraferma, 1 isola): una curva dolce."""
    x = ROAD_A[0] + (ROAD_B[0] - ROAD_A[0]) * v + 34 * math.sin(v * math.pi * 1.6)
    y = ROAD_A[1] + (ROAD_B[1] - ROAD_A[1]) * v
    return x, y


def road_ev(v):
    if v < F0:
        return END * ((F0 - v) / F0) ** 1.6
    if v > F1:
        return END * ((v - F1) / (1 - F1)) ** 1.6
    return 0.0


def eli_v(h):
    """Dove sta Eli sulla strada all'ora h: parte alle 6:05, al bordo delle FLATS alle 6:19."""
    return F0 * max(0.0, min(1.0, (h - ELI_START) / (ELI_EDGE - ELI_START)))


ALARM = (110, 1700)
CAR_LOT = [(220 + 66 * (k % 5), 1666 + 64 * (k // 5)) for k in range(10)]


def _dots(seed=7, n=30):
    rng = np.random.default_rng(seed)
    return [(rng.uniform(480, 700), rng.uniform(1575, 1660)) for _ in range(n)]


DOTS = _dots()


def dead_dot(c, x, y, a=1.0, dim=False):
    c.drawCircle(x, y, 10, G.P((40, 10, 10), a))
    c.drawCircle(x, y, 8, G.P((150, 60, 56) if dim else (226, 56, 50), a))


def eli_dot(c, x, y, label=True):
    G.glow(c, x, y, 40, (255, 240, 200), 0.4)
    c.drawCircle(x, y, 12, G.P((40, 20, 16)))
    c.drawCircle(x, y, 10, G.P((240, 236, 220)))
    if label:
        G.pin(c, x, y, "ELI", up=90, col=(240, 236, 220))


def bay(c, s, b, R):
    """La baia vista dall'alto: terraferma in basso, l'isola col faro in alto, la strada che emerge con la marea."""
    lapse = _p(b, "lapse")
    if lapse:
        g = R.bs / max(0.01, R.entry["t1"] - R.entry["t0"])
        h = 19.9 + g * PERIOD          # da alta marea, giù, su: un ciclo intero
    else:
        h = hours(R, b)
    d = depth(h)
    L = max(0.62, pal(min(h, 23.0))[5]) if not lapse else 0.9
    calm = _p(b, "calm", False)
    sea = lit((40, 100, 136), L)
    G.vgrad(c, -400, -400, 1480, 2320, lit((30, 82, 120), L), lit((46, 112, 146), L))
    rng = np.random.default_rng(2)
    for k in range(70 if not calm else 18):
        x, y = rng.uniform(-200, 1280), rng.uniform(0, 1920)
        w = 20 + 30 * rng.random()
        ph = math.sin(R.t * 1.4 + k)
        c.drawLine(x + 6 * ph, y, x + w + 6 * ph, y, G.P(mix(sea, (255, 255, 255), 0.25), 0.35 if not calm else 0.12,
                                                          StrokeWidth=2, StrokeCap=skia.Paint.kRound_Cap))
    # la secca lungo la strada (sabbia bagnata) e la strada stessa
    for i in range(80):
        v0, v1 = i / 80, (i + 1) / 80
        (ax, ay), (bx_, by_) = road_xy(v0), road_xy(v1)
        e = road_ev((v0 + v1) / 2)
        c.drawLine(ax, ay, bx_, by_, G.P(mix(lit((150, 140, 110), L), sea, 0.7 if d > e + 1.5 else 0.15),
                                         StrokeWidth=96, StrokeCap=skia.Paint.kRound_Cap))
    for i in range(80):
        v0, v1 = i / 80, (i + 1) / 80
        (ax, ay), (bx_, by_) = road_xy(v0), road_xy(v1)
        e = road_ev((v0 + v1) / 2)
        wet = d > e
        col = lit((160, 154, 144), L) if not wet else mix(sea, lit((160, 154, 144), L), 0.25)
        c.drawLine(ax, ay, bx_, by_, G.P(col, StrokeWidth=32, StrokeCap=skia.Paint.kRound_Cap))
        if wet:
            ph = (R.t * 0.8 + i * 0.37) % 1
            c.drawLine(ax - 14, ay + ph * 10, ax + 14, ay + ph * 10, G.P((210, 236, 252), 0.4, StrokeWidth=2))
    for v in np.arange(0.03, 1.0, 0.05):     # paletti
        x, y = road_xy(v)
        for sd in (-24, 24):
            c.drawCircle(x + sd, y, 3.5, G.P(lit((236, 236, 230), L)))
    bxv = road_xy(F0)
    G.rect(c, bxv[0] + 28, bxv[1] - 14, bxv[0] + 56, bxv[1] + 14, lit((132, 106, 80), L))
    c.drawLine(bxv[0] + 28, bxv[1], bxv[0] + 56, bxv[1], G.P(lit((80, 64, 50), L), StrokeWidth=3))
    if _p(b, "flats_label"):
        (fx0, fy0), (fx1, fy1) = road_xy(F0), road_xy(F1)
        c.drawLine(fx0 + 70, fy0, fx1 + 70, fy1, G.P((150, 210, 255), 0.9, StrokeWidth=4))
        for yy, xx in ((fy0, fx0), (fy1, fx1)):
            c.drawLine(xx + 58, yy, xx + 82, yy, G.P((150, 210, 255), 0.9, StrokeWidth=4))
        tag(c, (fx0 + fx1) / 2 + 210, (fy0 + fy1) / 2 + 8, "THE FLATS · ¼ MILE", col=(150, 210, 255), size=20)
    # terraferma
    land_ = skia.Path()
    land_.moveTo(-400, 1590)
    for x in range(-400, 1500, 30):
        land_.lineTo(x, 1590 + 22 * math.sin(x * 0.011) + 10 * math.sin(x * 0.037))
    land_.lineTo(1500, 2400)
    land_.lineTo(-400, 2400)
    land_.close()
    c.drawPath(land_, G.P(lit((214, 186, 132), L)))
    c.drawPath(land_, G.P(lit((240, 226, 190), L), 0.6, StrokeWidth=6, Style=skia.Paint.kStroke_Style))
    G.rect(c, -400, 1800, 1500, 2400, lit((84, 116, 72), L))
    for k in range(30):
        x, y = rng.uniform(-300, 1400), rng.uniform(1810, 2300)
        c.drawCircle(x, y, rng.uniform(16, 34), G.P(lit((64, 96, 58), L)))
    G.rrect(c, 180, 1630, 540, 1776, 14, lit((90, 90, 96), L))          # parcheggio
    for k, (x, y) in enumerate(CAR_LOT):
        cc = [(60, 86, 140), (150, 60, 56), (200, 200, 196), (90, 96, 104), (120, 90, 60)][k % 5]
        G.rrect(c, x - 18, y - 28, x + 18, y + 28, 8, lit(cc, L))
        G.rrect(c, x - 13, y - 16, x + 13, y - 4, 4, lit((150, 180, 210), L))
    blink = 0.0
    if _p(b, "alarm"):
        off = _t(R, b, "alarm_off", 99)
        if R.bs < off:
            blink = 1.0 if (R.t * 3.0) % 1 < 0.5 else 0.15
    G.rrect(c, ALARM[0] - 22, ALARM[1] - 36, ALARM[0] + 22, ALARM[1] + 36, 9, lit((210, 210, 206), L))
    G.rrect(c, ALARM[0] - 16, ALARM[1] - 22, ALARM[0] + 16, ALARM[1] - 6, 4, lit((150, 180, 210), L))
    if blink:
        for dy in (-30, 30):
            c.drawCircle(ALARM[0], ALARM[1] + dy, 9, G.P((255, 190, 60), blink))
        G.glow(c, ALARM[0], ALARM[1], 150, (255, 170, 50), 0.5 * blink)
        G.sound_rings(c, *ALARM, R.t, col=(255, 200, 120), n=3, r_max=280, a=0.55, period=1.0)
    elif _p(b, "alarm_off_tag") and R.bs > _t(R, b, "alarm_off", 99):
        tag(c, ALARM[0] + 210, ALARM[1] - 130, "ALARM · OFF", col=(220, 220, 220), size=20)
    # isola
    isl = skia.Path()
    pts = [(260, 520), (300, 360), (420, 270), (600, 250), (760, 300), (840, 420), (800, 560), (640, 630),
           (470, 620), (330, 600)]
    isl.moveTo((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2)
    for i in range(len(pts)):
        a_, b_ = pts[i], pts[(i + 1) % len(pts)]
        isl.quadTo(a_[0], a_[1], (a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2)
    isl.close()
    c.drawPath(isl, G.P(lit((176, 158, 116), L)))
    c.save()
    c.translate(550, 440)
    c.scale(0.88, 0.84)
    c.translate(-550, -440)
    c.drawPath(isl, G.P(lit((92, 112, 78), L)))
    c.restore()
    for k in range(9):
        x, y = rng.uniform(330, 780), rng.uniform(310, 570)
        if math.hypot(x - LHM[0], y - LHM[1]) > 60 and not (620 < x < 740 and 340 < y < 460):
            c.drawCircle(x, y, rng.uniform(10, 20), G.P(lit((110, 106, 108), L)))
    G.rect(c, 640, 380, 720, 440, lit((226, 218, 204), L))                # casa del nonno
    p = skia.Path()
    p.addPoly([skia.Point(632, 384), skia.Point(680, 350), skia.Point(728, 384)], True)
    c.drawPath(p, G.P(lit((150, 70, 60), L)))
    c.drawCircle(*LHM, 28, G.P(lit((236, 232, 224), L)))
    c.drawCircle(*LHM, 28, G.P(lit((196, 52, 48), L), StrokeWidth=6, Style=skia.Paint.kStroke_Style))
    c.drawCircle(*LHM, 11, G.P((255, 226, 150)))
    if h > 18.35 and not lapse:
        G.beam(c, *LHM, (R.t * 60) % 360, spread=16, length=700, col=(255, 240, 200), a=0.2)
    G.rect(c, 770, 590, 840, 602, lit((120, 90, 60), L))                # molo con la barca
    G.rrect(c, 806, 610, 866, 634, 10, lit((200, 200, 196), L))
    if _p(b, "dinghy"):
        tag(c, 836, 680, "HULL CRACKED", col=(210, 210, 210), size=16)
    MAP_ACTS.get(_p(b, "act"), _no)(c, s, b, R, h, d)


_RNG = np.random.default_rng(21)
HUDDLE = [(ALARM[0] + 70 + 60 * math.cos(a) * r, ALARM[1] - 30 + 52 * math.sin(a) * r)
          for a, r in zip(_RNG.uniform(0, 2 * math.pi, 30), np.sqrt(_RNG.uniform(0.15, 1.0, 30)))]
# i 14 che sentono la campana per primi sono i più vicini all'acqua (y più piccola)
_ORDER = sorted(range(30), key=lambda i: HUDDLE[i][1])
HUDDLE = [HUDDLE[i] for i in _ORDER]


def _alarm_pos(i, k):
    """Puntino i: dall'ingresso della strada al mucchio attorno all'auto dell'allarme (k 0..1)."""
    sx, sy = DOTS[i]
    tx, ty = HUDDLE[i]
    return sx + (tx - sx) * k, sy + (ty - sy) * k


def map_lapse(c, s, b, R, h, d):
    for x, y in DOTS:
        dead_dot(c, x, y)
    x, y = road_xy(0.0)
    eli_dot(c, x - 120, y + 140, label=False)


def map_run(c, s, b, R, h, d):
    """Il sasso, l'allarme, e i morti che CORRONO verso il suono: l'ingresso della strada si libera."""
    t = R.bs
    go = _t(R, b, "go_at", 0.3)
    for i in range(len(DOTS)):
        k = ramp(t, go + 0.02 * i, 0.9)
        dead_dot(c, *_alarm_pos(i, k))
    eli_dot(c, 470, 1690)


def map_walk(c, s, b, R, h, d):
    """Eli sulla strada in silenzio; il conto alla rovescia attaccato alle FLATS; i morti fermi all'auto."""
    t = R.bs
    for i in range(len(DOTS)):
        x, y = _alarm_pos(i, 1.0)
        dead_dot(c, x + 3 * math.sin(R.t + i), y)
    v = eli_v(h)
    x, y = road_xy(v)
    eli_dot(c, x, y)
    fx, fy = road_xy(F0)
    left = max(0.0, round((18 + 13 / 60 - h) * 3600))
    col = (255, 90, 80) if left <= 0 else (255, 200, 90)
    chip(c, fx - 210, fy - 90, "FLATS FLOOD IN", f"{int(left // 60)}:{int(left % 60):02d}", col=col, size=36,
         anchor=(fx - 20, fy))
    if left <= 0 and _p(b, "short") is not None:
        k = ramp(t, _t(R, b, "short"), 0.3)
        c.drawLine(x - 50, y, fx - 50, fy, G.P((255, 90, 80), k, StrokeWidth=5,
                                              PathEffect=skia.DashPathEffect.Make([12, 8], 0)))
        for yy in (y, fy):
            c.drawLine(x - 64, yy, x - 36, yy, G.P((255, 90, 80), k, StrokeWidth=5))
        tag(c, x - 210, (y + fy) / 2 + 30, "STILL OUT HERE", col=(255, 90, 80), a=k, size=20)


def map_rings(c, s, b, R, h, d):
    """La campana: gli anelli scivolano sull'acqua calma fino alla spiaggia; all'auto le teste si girano."""
    t = R.bs
    ring = _t(R, b, "ring_at", 0.0)
    g = t - ring
    for k in range(4):
        r = (g - k * 0.4) * 1100
        if 0 < r < 1900:
            c.drawCircle(*LHM, r, G.P((255, 230, 160), 0.7 * (1 - r / 1900), StrokeWidth=7,
                                       Style=skia.Paint.kStroke_Style))
    reach = math.hypot(ALARM[0] - LHM[0], ALARM[1] - LHM[1]) / 1100 + ring
    for i in range(len(DOTS)):
        x, y = _alarm_pos(i, 1.0)
        dead_dot(c, x, y)
        if t > reach + 0.03 * i:      # si girano verso il mare
            c.drawLine(x, y, x + 9, y - 13, G.P((255, 140, 130), StrokeWidth=3.5))
    v = eli_v(h)
    x, y = road_xy(v)
    eli_dot(c, x, y)
    G.pin(c, *LHM, "GRANDPA", up=120, col=(120, 170, 255))


def map_count(c, s, b, R, h, d):
    """DING... DING: a ogni colpo un gruppo dei più vicini all'acqua corre oltre la linea d'ingresso.
    ON THE ROAD li conta mentre la passano; gli altri restano all'auto."""
    t = R.bs
    marks = [_t(R, b, k) for k in ("c1", "c2", "c3")]
    groups = [range(0, 5), range(5, 10), range(10, 14)]
    on = 0
    for m, grp in zip(marks, groups):
        for i in grp:
            sx, sy = _alarm_pos(i, 1.0)
            if m is None or t < m:
                dead_dot(c, sx, sy)
                continue
            k = ease((t - m) / 0.8)
            ex_, ey_ = road_xy(0.02 + 0.025 * (i % 5) + 0.06 * k)
            dead_dot(c, sx + (ex_ - sx) * k + (i % 3 - 1) * 9, sy + (ey_ - sy) * k)
            if k > 0.75:
                on += 1
    for i in range(14, len(DOTS)):
        dead_dot(c, *_alarm_pos(i, 1.0), dim=True)
    ex0, ey0 = road_xy(0.0)
    c.drawLine(ex0 - 80, ey0 - 30, ex0 + 80, ey0 - 30, G.P((255, 255, 255), 0.85, StrokeWidth=4,
                                                         PathEffect=skia.DashPathEffect.Make([12, 8], 0)))
    if marks[0] is not None and t >= marks[0] - 0.4:
        chip(c, ex0 - 190, ey0 - 140, "ON THE ROAD", str(on), col=(255, 90, 80), size=46, anchor=(ex0 - 80, ey0 - 30))
    for m in marks:
        if m is not None and 0 <= t - m < 1.4:
            r = (t - m) * 1300
            c.drawCircle(*LHM, r, G.P((255, 230, 160), 0.6 * (1 - (t - m) / 1.4), StrokeWidth=7,
                                       Style=skia.Paint.kStroke_Style))
    v = eli_v(h)
    x, y = road_xy(v)
    eli_dot(c, x, y)


MAP_ACTS = {"lapse": map_lapse, "run": map_run, "walk": map_walk, "rings": map_rings, "count": map_count}


# ---------- scena: il ballatoio del faro ----------

def gallery(c, s, b, R):
    """Il nonno sul ballatoio: tira la corda e la campana suona su "BELL". La targa spiega perché; la radio
    sulla ringhiera fa solo fruscio (non sa niente di quello che c'è sulla spiaggia)."""
    h = hours(R, b)
    top, midc, hor, sea, deep, L = pal(h)
    t = R.bs
    G.vgrad(c, -300, -300, 1380, 1300, [top, midc, hor], top, stops=[0, 0.6, 1])
    G.vgrad(c, -300, 1300, 1380, 2300, sea, deep)
    G.rect(c, -300, 1420, 700, 1434, lit((120, 116, 110), L))
    G.rect(c, 120, 1420, 330, 1434, sea, 0.85)
    c.drawLine(120, 1418, 330, 1418, G.P((220, 240, 255), 0.8, StrokeWidth=3))
    G.rect(c, 560, 200, 1180, 1220, lit((70, 74, 82), L))
    G.rect(c, 620, 260, 1120, 1000, mix(lit((110, 130, 150), L), (255, 236, 170), 0.9))
    G.glow(c, 870, 620, 520, (255, 230, 160), 0.35)
    for k in range(4):
        G.rect(c, 620 + k * 166, 260, 632 + k * 166, 1000, lit((60, 62, 70), L))
    G.rect(c, -300, 1220, 1380, 1260, lit((44, 44, 50), L))
    for k in range(12):
        x = -260 + k * 130
        c.drawLine(x, 1220, x, 980, G.P(lit((44, 44, 50), L), StrokeWidth=10))
    c.drawLine(-300, 980, 1380, 980, G.P(lit((44, 44, 50), L), StrokeWidth=14))
    G.rrect(c, 40, 916, 200, 980, 10, lit((70, 58, 50), L))
    for k in range(6):
        c.drawLine(60 + k * 10, 930, 60 + k * 10, 966, G.P((30, 26, 24), StrokeWidth=4))
    G.rrect(c, 140, 930, 186, 966, 6, (40, 60, 40))
    c.drawLine(186, 916, 204, 850, G.P((40, 40, 44), StrokeWidth=3))
    for k in range(3):   # fruscio
        ph = (R.t * 2 + k / 3) % 1
        c.drawArc(skia.Rect(200 - 30 * ph, 900 - 30 * ph, 260 + 30 * ph, 960 + 30 * ph), -60, 120, False,
                  G.P((200, 200, 200), 0.4 * (1 - ph), StrokeWidth=3, Style=skia.Paint.kStroke_Style))
    ring_at = _t(R, b, "ring_at")
    swing = 0.0
    if ring_at is not None and t >= ring_at:
        g = t - ring_at
        swing = 28 * math.sin(g * 7.5) * math.exp(-g * 0.35)
    bx, by = 330, 520
    G.rect(c, bx - 120, by - 70, bx + 40, by - 54, lit((50, 50, 54), L))
    c.save()
    c.translate(bx, by - 60)
    c.rotate(swing)
    bell = skia.Path()
    bell.moveTo(-90, 210)
    bell.quadTo(-80, 20, -36, 10)
    bell.quadTo(0, 0, 36, 10)
    bell.quadTo(80, 20, 90, 210)
    bell.close()
    c.drawPath(bell, G.P(lit((222, 176, 74), L)))
    c.drawPath(bell, G.P((60, 44, 20), StrokeWidth=5, Style=skia.Paint.kStroke_Style))
    c.drawCircle(0, 218, 18, G.P((70, 52, 24)))
    c.restore()
    rope_x = bx + 30 + 120 * math.sin(math.radians(swing))
    c.drawLine(bx + 20, by + 150, rope_x, 1100, G.P(lit((200, 180, 140), L), StrokeWidth=7))
    G.rrect(c, bx - 160, 760, bx + 100, 880, 8, lit((190, 170, 120), L))
    gfx.draw_text(c, "RING WHEN THE SEA", K.bold(22), bx - 30, 808, color=lit((50, 40, 24), L))
    gfx.draw_text(c, "TOUCHES THE ROAD", K.bold(22), bx - 30, 842, color=lit((50, 40, 24), L))
    if ring_at is not None and t >= ring_at:
        G.sound_rings(c, bx, by + 80, R.t - ring_at, col=(255, 230, 170), n=3, r_max=760, a=0.7, period=1.0, width=10)
    grab = _t(R, b, "grab_at", 0.0)
    if ring_at is None or t < ring_at - 0.25:
        p = blend(pose("stand"), pose("rope"), ramp(t, grab, 0.4))
    else:
        p = blend(pose("rope"), pose("rope_pull"), 0.5 + 0.5 * math.sin((t - ring_at) * 7.5))
    GRANDPA.draw(c, 600, 1222, breathe(p, R.t, 0.5), facing=-1)
    G.darkness(c, 0.25 * (1 - L), lights=[(870, 620, 700, 0.8)])


def binoc(c, s, b, R):
    """Il binocolo del nonno: nel cerchio solo la strada allagata e Eli, piccolo. La spiaggia è dietro il
    promontorio: lui i morti non li vede."""
    h = hours(R, b)
    top, midc, hor, sea, deep, L = pal(h)
    G.vgrad(c, -300, -300, 1380, 900, [top, midc, hor], top, stops=[0, 0.6, 1])
    G.vgrad(c, -300, 900, 1380, 2300, mix(sea, hor, 0.2), deep)
    p = skia.Path()
    p.moveTo(-300, 860)
    p.quadTo(120, 700, 340, 950)
    p.lineTo(340, 2300)
    p.lineTo(-300, 2300)
    p.close()
    c.drawPath(p, G.P(lit((60, 72, 58), L)))
    road = skia.Path()
    road.moveTo(560, 940)
    road.lineTo(604, 940)
    road.lineTo(820, 2300)
    road.lineTo(360, 2300)
    road.close()
    c.drawPath(road, G.P(lit((140, 134, 126), L)))
    wet = ramp(R.bs, 0.1, 1.2)
    G.rect(c, 300, 1220 - 100 * wet, 900, 1330 + 50 * wet, mix(sea, (150, 200, 230), 0.2), 0.8 * wet)
    for k in range(5):
        ph = (R.t * 0.6 + k / 5) % 1
        c.drawLine(380 + ph * 420, 1250 + k * 14, 420 + ph * 420, 1250 + k * 14,
                   G.P((220, 240, 255), 0.6 * wet, StrokeWidth=3))
    eli(c, 586, 1110, breathe(pose("sneak"), R.t), facing=1, light=L)
    screen(c)
    full = skia.Path()
    full.addRect(skia.Rect(-10, -10, 1090, 1930))
    holes = skia.Path()
    holes.addCircle(380, 960, 330)
    holes.addCircle(700, 960, 330)
    m = skia.Op(full, holes, skia.PathOp.kDifference_PathOp)
    c.drawPath(m, G.P((4, 4, 6)))
    for cx_ in (380, 700):     # bordo morbido delle lenti
        c.drawCircle(cx_, 960, 330, G.P((0, 0, 0), 0.6, StrokeWidth=26, Style=skia.Paint.kStroke_Style,
                                         MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14)))
    c.restore()


# ---------- scena: giù dalla botola del box ----------

def down(c, s, b, R):
    """Dalla botola del box, giù: i quattro pali che scendono nell'acqua nera. Il fascio del faro passa e
    illumina teste e mani: 1, 6, tutte e 14, che guardano su."""
    t = R.bs
    G.rect(c, -300, -300, 1380, 2300, (6, 10, 20))
    cx, cy = 540, 1040
    for k in range(10):
        ph = (R.t * 0.12 + k / 10) % 1
        c.drawOval(skia.Rect(cx - 120 - ph * 700, cy - 70 - ph * 400, cx + 120 + ph * 700, cy + 70 + ph * 400),
                   G.P((70, 100, 140), 0.16 * (1 - ph), StrokeWidth=3, Style=skia.Paint.kStroke_Style))
    feet = [(410, 920), (670, 920), (410, 1160), (670, 1160)]
    tops = [(170, 640), (910, 640), (170, 1440), (910, 1440)]
    sweeps = [_t(R, b, k) for k in ("s1", "s2", "s3")]
    shown = [1, 6, 14]
    vis = 0
    for m, n in zip(sweeps, shown):
        if m is not None and t >= m:
            vis = n
    beam_k = 0.0
    bands = []
    for m in sweeps:
        if m is not None and -0.25 <= t - m < 1.2:
            g = (t - m + 0.25) / 1.45
            bands.append(g)
            beam_k = max(beam_k, math.sin(g * math.pi))
    lit_k = 0.5 + 0.5 * beam_k
    for (fx, fy), (tx, ty) in zip(feet, tops):
        p = skia.Path()
        p.moveTo(tx - 34, ty)
        p.lineTo(fx - 12, fy)
        p.lineTo(fx + 12, fy)
        p.lineTo(tx + 34, ty)
        p.close()
        c.drawPath(p, G.P(mix((50, 40, 32), (110, 88, 66), lit_k)))
    ring = []
    for i in range(14):
        a = i / 14 * 2 * math.pi + 0.3
        rx = 290 + 46 * (i % 3)
        ry = 260 + 40 * ((i + 1) % 3)
        ring.append((cx + math.cos(a) * rx, cy + math.sin(a) * ry))
    order = [3, 10, 6, 0, 12, 8, 1, 5, 13, 2, 9, 4, 11, 7]
    for rank, i in enumerate(order[:vis]):
        x, y = ring[i]
        m = sweeps[0 if rank < 1 else (1 if rank < 6 else 2)]
        a = ease((t - m) / 0.25)
        bob = 3 * math.sin(R.t * 1.3 + i)
        c.drawOval(skia.Rect(x - 70, y - 30 + bob, x + 70, y + 40 + bob), G.P((120, 150, 190), 0.12 * a,
                                                                              StrokeWidth=3, Style=skia.Paint.kStroke_Style))
        c.drawCircle(x, y + bob, 42, G.P(mix((50, 62, 54), (132, 152, 128), lit_k), a))
        c.drawCircle(x, y + bob, 42, G.P((14, 18, 16), a, StrokeWidth=5, Style=skia.Paint.kStroke_Style))
        c.drawArc(skia.Rect(x - 30, y - 32 + bob, x + 10, y + 4 + bob), 200, 70, False,
                  G.P((240, 250, 255), 0.7 * a * lit_k, StrokeWidth=4, Style=skia.Paint.kStroke_Style))
        for dx in (-14, 14):
            G.glow(c, x + dx, y + 4 + bob, 28, (255, 40, 30), 0.45 * a)
            c.drawCircle(x + dx, y + 4 + bob, 6.5, G.P((255, 52, 40), a))
    if vis >= 14:       # mani strette ai pali, su tutti e quattro
        a = ease((t - sweeps[2]) / 0.3)
        for (fx, fy), (tx, ty) in zip(feet, tops):
            for f in (0.1, 0.2):
                hx = fx + (tx - fx) * f
                hy = fy + (ty - fy) * f
                c.drawOval(skia.Rect(hx - 20, hy - 12, hx + 20, hy + 12),
                           G.P(mix((60, 72, 62), (140, 160, 136), lit_k), a))
    for g in bands:     # il fascio che attraversa l'acqua
        bx = -400 + 1900 * g
        p = skia.Path()
        p.moveTo(bx - 280, -300)
        p.lineTo(bx + 60, -300)
        p.lineTo(bx + 280, 2300)
        p.lineTo(bx - 60, 2300)
        p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=rgba((255, 240, 200), 0.16 * math.sin(g * math.pi)),
                                 BlendMode=skia.BlendMode.kPlus))
    wood = (70, 54, 40)       # la botola: siamo noi che guardiamo giù
    G.rect(c, -300, -300, 1380, 330, wood)
    G.rect(c, -300, 1700, 1380, 2300, wood)
    G.rect(c, -300, -300, 70, 2300, wood)
    G.rect(c, 1010, -300, 1380, 2300, wood)
    for k in range(7):
        c.drawLine(-300, 40 + k * 46, 1380, 40 + k * 46, G.P((40, 30, 22), StrokeWidth=3))
        c.drawLine(-300, 1740 + k * 46, 1380, 1740 + k * 46, G.P((40, 30, 22), StrokeWidth=3))
    c.drawRect(skia.Rect(70, 330, 1010, 1700), G.P((30, 22, 16), StrokeWidth=14, Style=skia.Paint.kStroke_Style))
    G.darkness(c, 0.3, lights=[(540, 1010, 900, 0.5)])
    if vis and _p(b, "insight", True):
        chip(c, 540, 490, "IN SIGHT", str(vis), col=(255, 80, 70), size=60)


# ---------- scena: cartello finale ----------

def end_map(c, s, b, R):
    """La baia di notte: 14 puntini sotto il box, sulla strada che porta dritta al nonno. 6:38 AM."""
    t = R.bs
    G.rect(c, -300, -300, 1380, 2300, (6, 10, 20))
    c.save()
    c.translate(540, 300)
    c.scale(0.68, 0.68)
    c.translate(-540, -440)
    c.clipRect(skia.Rect(-200, 160, 1280, 1700))
    bay(c, s, _Fake({"h": 23.95, "calm": True}), R)
    G.rect(c, -300, -300, 1380, 2300, (4, 6, 14), 0.45)
    bx, by = road_xy(F0)
    G.rect(c, bx + 28, by - 14, bx + 56, by + 14, (132, 106, 80))
    for i in range(14):
        a = i / 14 * 2 * math.pi
        dead_dot(c, bx + 42 + math.cos(a) * 50, by + math.sin(a) * 42)
    c.drawCircle(*LHM, 22, G.P((236, 232, 224)))
    c.drawCircle(*LHM, 9, G.P((255, 226, 150)))
    G.pin(c, *LHM, "GRANDPA", up=110, col=(120, 170, 255))
    c.drawLine(bx + 40, by - 50, LHM[0] + 30, LHM[1] + 40, G.P((255, 90, 80), 0.8, StrokeWidth=4,
                                                               PathEffect=skia.DashPathEffect.Make([12, 10], 0)))
    c.restore()
    k1 = ramp(t, _t(R, b, "l1_at", 0.2), 0.25)
    k2 = ramp(t, _t(R, b, "l2_at", 1.0), 0.1)
    gfx.draw_text(c, "6:38 AM · THE ROAD FLOODS AGAIN", K.bold(40), 540, 1130, color=(240, 240, 244), alpha=k1,
                  tracking=2)
    if k2 > 0:
        f = K.heavy(92)
        gfx.draw_text(c, "GRANDPA RINGS", f, 540, 1250, color=(235, 50, 44), alpha=k2)
        gfx.draw_text(c, "THE BELL.", f, 540, 1345, color=(235, 50, 44), alpha=k2)
    k3 = ramp(t, _t(R, b, "l3_at", 1.6), 0.3)
    if k3 > 0:
        label = "FOLLOW · DON'T MAKE A SOUND"
        pf = K.bold(32)
        pw = pf.measureText(label)
        r = skia.RRect.MakeRectXY(skia.Rect(540 - pw / 2 - 40, 1420, 540 + pw / 2 + 40, 1496), 38, 38)
        c.drawRRect(r, G.P((20, 18, 18), 0.92 * k3))
        c.drawRRect(r, G.P((255, 110, 80), k3, StrokeWidth=3, Style=skia.Paint.kStroke_Style))
        gfx.draw_text(c, label, pf, 540, 1470, color=(245, 240, 235), alpha=k3, tracking=2)
        gfx.draw_text(c, "LOW TIDE · DAY 2", K.bold(26), 540, 1560, color=(170, 172, 180), alpha=k3, tracking=4)


class _Fake:
    """Un beat finto per ridisegnare una scena dentro un'altra (la baia sotto il cartello finale)."""
    def __init__(self, params):
        self.params = params


def black(c, s, b, R):
    G.rect(c, -300, -300, 1380, 2300, (2, 1, 4))


SCENES = {"world": world, "bay": bay, "gallery": gallery, "binoc": binoc, "sign": sign, "down": down,
          "end_map": end_map, "black": black}
