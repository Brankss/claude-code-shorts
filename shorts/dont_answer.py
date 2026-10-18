"""DON'T ANSWER, Day 1: una nebbia che copia le voci. Scene disegnate con pov_gfx e lo stickman.

Ogni scena è una funzione (c, s, b, R):
- s = secondi dall'inizio dell'inquadratura (resta continuo se più beat condividono la stessa)
- b = beat corrente, con i parametri in b.params
- R = renderer: R.bs (secondi dall'inizio del beat), R.t (tempo del video), R.word("x") (quando viene detta
  una parola nel beat corrente), così gli eventi cadono esattamente sulla parola giusta.

Luce: blu-grigio freddo per la nebbia, una sola luce calda (lampada) come luce principale, e un colore
saturo per inquadratura (la vestaglia blu, la vestaglia rosa, l'impermeabile giallo), come chiedevano le note.
"""

import math

import numpy as np
import skia

from . import gfx
from . import kinetic as K
from . import pov_gfx as G
from .gfx import mix, rgba
from .stick import POSES, Figure, blend, breathe, ease

YELLOW = (250, 204, 36)
BLUE_ROBE = (60, 120, 230)
PINK_ROBE = (236, 120, 160)
WARM = (255, 196, 120)
NIGHT_FOG = (52, 58, 74)

YOU = Figure(height=560)
ELLIE = Figure(height=330, coat=YELLOW)
MAN = Figure(height=300, fill=BLUE_ROBE)
WIFE = Figure(height=280, fill=PINK_ROBE)
BIG = Figure(height=1500, fill=(30, 28, 32), ink=(8, 8, 10))      # la tua sagoma in primo piano, di spalle
SHAPE = Figure(height=1000, fill=(66, 68, 82), ink=(14, 14, 18))  # la cosa nella nebbia

MOODS = {
    # tipo di cielo, colore della nebbia, luce (1 = giorno pieno, 0 = buio)
    "dawn": ("fog", (104, 114, 134), 0.65),
    "day": ("fog", (126, 136, 152), 0.85),
    "sunset": ("sunset", (214, 138, 92), 0.6),
    "night": ("night", NIGHT_FOG, 0.22),
}


def _p(b, key, default=None):
    return b.params.get(key, default)


def _w(R, needle, default=99.0, end=False):
    """Quando (secondi dall'inizio del beat) viene detta la parola; default se non c'è."""
    t = R.word(needle, end=end)
    return default if t is None else t


def bent(pose, angle=-38):
    """Il "collo piegato": la testa che pende su una spalla, il segno di chi è stato preso."""
    p = dict(pose)
    p["head"] = angle
    return p


def ring_at(c, x, y, t, a=0.45, r=180, col=(214, 222, 236), n=3):
    G.sound_rings(c, x, y, t, col=col, n=n, r_max=r, a=a)


# ---------- camera da letto (l'hook) ----------

def bedroom(c, s, b, R):
    sky, fogc, light = MOODS["dawn"]
    G.room(c, (44, 52, 70), (48, 46, 56), horizon=1270, x0=-200, x1=1280, y1=2100)
    gone = _w(R, "work") - 0.15

    def view(c, r):
        x0, y0, x1, y1 = r
        G.sky(c, *r, sky)
        G.rect(c, x0, y1 - 120, x1, y1, (56, 66, 64))
        for k in range(9):                      # la staccionata in fondo al giardino
            G.rect(c, x0 + 10 + k * 46, y1 - 230, x0 + 34 + k * 46, y1 - 110, (78, 84, 92))
        G.rect(c, x0, y1 - 200, x1, y1 - 186, (78, 84, 92))
        G.fog(c, *r, s, a=0.7, col=fogc, seed=2)
        mx = (x0 + x1) / 2 + 30
        if R.bs < gone:
            # la "mamma": una sagoma alta nella nebbia, col collo piegato (disegnata sopra la nebbia, appena velata)
            mom = Figure(height=360, fill=(54, 60, 74), ink=(30, 32, 40))
            mom.draw(c, mx, y1 - 100, bent(POSES["stand"]), facing=-1)
            G.vgrad(c, *r, fogc, fogc, a=0.18)
            if R.bs > _w(R, "backyard"):
                ring_at(c, mx, y1 - 300, R.t, a=0.55, r=220)
        elif R.bs - gone < 1.2:
            ring_at(c, mx, y1 - 300, R.t, a=0.55 * (1 - (R.bs - gone) / 1.2), r=220)
        G.vgrad(c, *r, fogc, fogc, a=0.12)

    G.window(c, 640, 380, 1020, 900, view, frame=(36, 38, 46))
    G.shaft(c, 640, 900, 1020, 900, 140, 560, col=(170, 186, 210), a=0.05, angle=-14)
    # comodino con la lampada (a sinistra) e letto
    G.rect(c, 40, 1110, 190, 1270, (70, 54, 42))
    G.lamp(c, 115, 1110, h=150, on=True)
    G.bed(c, 200, 1270, 520, blanket=(58, 66, 104))
    YOU.draw(c, 440, 1072, breathe(dict(POSES["sit_up_bed"], head=-12), s), facing=1, feet=False)
    G.rrect(c, 360, 1050, 728, 1150, 30, (58, 66, 104))
    for k in (0.3, 0.6, 0.85):
        c.drawLine(380 + 330 * k, 1055, 360 + 330 * k, 1145, G.P((44, 50, 80), 0.6, StrokeWidth=4))
    # il telefono in primo piano, sul comodino davanti: si accende su "texting" con il banner leggibile
    on_at = _w(R, "texting") - 0.05
    k = ease((R.bs - on_at) / 0.15) if R.bs >= on_at else 0.0
    buzz = math.sin(R.t * 80) * 3 if 0 <= R.bs - on_at < 0.6 else 0.0
    c.save()
    c.translate(700 + buzz, 1640)
    c.rotate(-7)
    G.rect(c, -700, 90, 700, 700, (60, 46, 38))
    G.rrect(c, -250, -120, 250, 120, 36, (14, 14, 18))
    G.rrect(c, -236, -106, 236, 106, 30, mix((10, 10, 14), (40, 46, 70), k))
    if k > 0:
        G.glow(c, 0, 0, 460, (150, 170, 255), 0.45 * k)
        G.rrect(c, -216, -78, 216, 78, 24, (50, 54, 78), k)
        G.rrect(c, -192, -52, -128, 12, 14, (60, 190, 90), k)
        gfx.draw_text(c, "MOM", K.heavy(44), -106, -12, color=(245, 245, 250), alpha=k, align="left")
        gfx.draw_text(c, "at work", gfx.text(40), -106, 42, color=(225, 228, 238), alpha=k, align="left")
    c.restore()
    G.darkness(c, 0.3, lights=[(115, 960, 520, 0.85), (700, 1640, 420, 0.7 * k), (830, 640, 360, 0.6)])

def phone(c, s, b, R):
    """Il telefono sul comodino (cavo, luce). params: ui = lock | alert | chat | receipt."""
    G.rect(c, -300, -300, 1380, 2220, (20, 18, 22))
    G.vgrad(c, 0, 0, 1080, 1920, (32, 28, 32), (10, 9, 12))
    p = skia.Path()
    p.moveTo(560, 1520)
    p.cubicTo(600, 1700, 420, 1760, 470, 2000)
    c.drawPath(p, G.P((200, 200, 206), StrokeWidth=12, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))
    ui = _p(b, "ui", "lock")
    t = R.bs
    jx = 0.0
    if ui == "alert" and (R.t * 2.0) % 1 < 0.36:
        jx = 3 * math.sin(R.t * 90)
    if ui == "lock":
        notifs = [(a, ti, bo, col, _w(R, at[1:]) if isinstance(at, str) else at) for a, ti, bo, col, at in _p(b, "notifs", [])]
        G.phone(c, 540 + jx, 900, 560, 1180, lambda c, r: G.lock_screen(c, r, _p(b, "time", "6:41"), "Tuesday",
                                                                           notifs, t=t, wall=((40, 50, 74), (16, 20, 32))),
                tilt=-4, glow_a=0.3)
    elif ui == "alert":
        hot = _p(b, "hot")             # parola del narratore su cui una riga si accende
        lit_at = _w(R, hot) if hot else -9

        def screen(c, r):
            lines = []
            for i, (txt, col) in enumerate(ALERT_LINES):
                bright = col
                if _p(b, "dim_but") is not None and i not in _p(b, "dim_but"):
                    bright = mix(col, (120, 40, 40), 0.55)
                if hot and i in (1, 2) and t >= lit_at:
                    bright = (255, 236, 120)
                lines.append((txt, bright, _p(b, "line_at", [0, 0, 0, 0])[i]))
            G.alert_screen(c, r, "EMERGENCY ALERT", "EXTREME THREAT · DENSE FOG EVENT", lines, t=t)
        G.phone(c, 540 + jx, 900, 560, 1180, screen, tilt=-4, glow_a=0.5, glow_col=(255, 60, 50))
        if _p(b, "glitch"):
            rng = np.random.default_rng(int(R.t * 24))
            for _ in range(8):
                y0 = rng.uniform(300, 1500)
                dy = rng.uniform(4, 30)
                G.rect(c, 0, y0, 1080, y0 + dy, (255, 255, 255), 0.16)
                G.rect(c, rng.uniform(-40, 40), y0, 1080, y0 + dy * 0.4, (255, 60, 60), 0.2)
            G.vgrad(c, 0, 0, 1080, 1920, (255, 255, 255), (255, 255, 255), a=max(0.0, 0.6 - R.bs * 2.5))
    else:
        G.phone(c, 540, 900, 560, 1180, lambda c, r: G.chat_screen(c, r, "MOM", _p(b, "msgs", []), t=t,
                                                                    typing_at=_p(b, "typing"),
                                                                    typing_until=_p(b, "typing_until"),
                                                                    status=_p(b, "status", "last seen 8:06 PM"),
                                                                    receipt=_p(b, "receipt"),
                                                                    highlight=_p(b, "highlight")),
                tilt=-4, glow_a=0.3)
        zoom_at = _p(b, "receipt_zoom")
        if isinstance(zoom_at, str):
            zoom_at = _w(R, zoom_at[1:])
        if zoom_at is not None and R.bs >= zoom_at:
            # stacco secco: "Read 11:51 PM" a tutto schermo
            k = ease((R.bs - zoom_at) / 0.12)
            G.rect(c, -300, -300, 1380, 2220, (0, 0, 0), k)
            f = gfx.fit_font(K.heavy, "Read 11:51 PM", 960, 130)
            gfx.draw_text(c, "Read 11:51 PM", f, 540, 1000, color=(255, 255, 255), alpha=k)
    if _p(b, "dim"):
        G.darkness(c, _p(b, "dim"), lights=[(540, 900, 560, 0.85)])


# ---------- casa vista da fuori ----------

def _ellie_house(c, x, yb, light, coat=True, dark_windows=False, rings=False, t=0.0):
    G.house(c, x, yb, 600, 470, siding=(120, 138, 156), dark=0.25 + 0.6 * (1 - light), lit=())
    if coat:
        # l'impermeabile giallo appeso accanto alla porta: l'unico colore saturo
        cx, cy = x - 120, yb - 230
        c.drawLine(cx, cy - 40, cx, cy - 20, G.P((40, 40, 44), StrokeWidth=6))
        G.rrect(c, cx - 26, cy - 22, cx + 26, cy + 64, 16, YELLOW)
        c.drawCircle(cx, cy - 22, 22, G.P(YELLOW))
        G.rrect(c, cx - 26, cy + 30, cx + 26, cy + 36, 2, mix(YELLOW, (0, 0, 0), 0.25))


def house_ext(c, s, b, R):
    mood = _p(b, "mood", "dawn")
    sky, fogc, light = MOODS[mood]
    G.sky(c, -300, -300, 1380, 2220, sky)
    dark = 1 - light
    # luci della strada: aloni morbidi nella nebbia che muoiono dal fondo verso di noi
    die = _p(b, "lamps_die_at")
    lamps = ((1250, 900), (-200, 950), (880, 1180), (120, 1240))
    for i, (lx, ly) in enumerate(lamps):
        on = 1.0
        if die is not None:
            ti = die + i * 0.32
            on = 0.0 if R.bs >= ti + 0.12 else (1.0 if R.bs < ti else 0.5 * (1 + math.sin(R.t * 90)))
        if mood in ("night", "sunset") and on > 0:
            G.glow(c, lx, ly, 260, (255, 214, 150), 0.32 * on)
            G.glow(c, lx, ly, 50, (255, 236, 200), 0.6 * on)
    # la nostra casa, con la lampada calda
    up_lamp = _p(b, "up_lamp", True)
    G.house(c, 420, 1320, 640, 500, dark=0.2 + 0.6 * dark, lit=(0,) if up_lamp else ())
    line = _p(b, "blanket_line", 0.0)
    line_off = _p(b, "line_off_at")
    if line_off is not None and R.bs >= line_off:
        line = 0.0 if R.bs >= line_off + 0.2 else line * 0.5 * (1 + math.sin(R.t * 70))
    if line > 0:       # una riga di luce calda dal bordo della coperta alla finestra di sotto
        x0 = 420 - 320 + 640 * 0.62
        G.rect(c, x0 + 160, 1320 - 500 + 500 * 0.55, x0 + 166, 1320 - 500 + 500 * 0.55 + 140, WARM, line)
        G.glow(c, x0 + 163, 1320 - 500 + 500 * 0.55 + 70, 120, WARM, 0.45 * line)
    _ellie_house(c, 1080, 1300, light, coat=_p(b, "coat", True))
    G.rect(c, -300, 1320, 1380, 1500, mix((52, 64, 58), (0, 0, 0), dark * 0.8))
    G.rect(c, -300, 1500, 1380, 2300, mix((50, 52, 60), (0, 0, 0), dark * 0.8))
    vanish = _w(R, _p(b, "rings_stop", "@@"))
    for k, (rx, ry) in enumerate(_p(b, "rings", [])):
        if R.bs < vanish:
            ring_at(c, rx, ry, R.t + k * 0.5, a=0.45)
    G.fog(c, -300, 500, 1380, 2000, s + 3, a=0.55, col=fogc, seed=5)
    if mood == "night":
        G.darkness(c, 0.55, lights=[(420, 1050, 500, 0.6)] if line > 0 else [])
    pin = _p(b, "pin")
    if pin:
        px, py = _p(b, "pin_at", (290, 960))
        pa = min(1.0, R.bs / 0.3)
        if line_off is not None and R.bs >= line_off:
            pa = 0.0 if R.bs >= line_off + 0.2 else 0.5 * (1 + math.sin(R.t * 70))
        G.pin(c, px, py, pin, a=pa)
    if _p(b, "to_black") is not None and R.bs >= _p(b, "to_black"):
        G.rect(c, -300, -300, 1380, 2220, (0, 0, 0))


# ---------- dalla finestra di casa ----------

def window_view(c, s, b, R):
    """La finestra davanti: la strada (il vicino, la moglie, Ellie che esce) o la casa di Ellie.
    gap = se c'è la coperta, quanto è largo lo spiraglio da cui guardi."""
    mood = _p(b, "mood", "dawn")
    sky, fogc, light = MOODS[mood]
    vis = _p(b, "vis", 0.8)
    what = _p(b, "what", "street")

    def view(c, r):
        x0, y0, x1, y1 = r
        G.sky(c, *r, sky)
        if what == "street":
            # casa del vicino dall'altra parte della strada, con il portico acceso e la zanzariera socchiusa
            G.house(c, 560, 1080, 520, 420, siding=(170, 150, 132), dark=0.25 + 0.6 * (1 - light), lit=(4,),
                    porch_light=1.0 if _p(b, "porch", True) else 0.0)
            G.rect(c, 0, 1080, 1080, 1200, mix((56, 68, 60), (0, 0, 0), 1 - light))
            G.rect(c, 0, 1200, 1080, 1240, (110, 110, 116))
            G.rect(c, 0, 1240, 1080, 1920, (54, 56, 62))
            G.rect(c, 520, 1080, 600, 1200, (130, 126, 120))            # il vialetto
            # Ellie: casa a destra, gancio con l'impermeabile (o vuoto)
            G.rect(c, 940, 860, 1120, 1240, (110, 128, 146))
            hook = _p(b, "hook", True)
            out_at = _p(b, "ellie_out_at")
            ex = 1010
            if hook and (out_at is None or R.bs < out_at):
                G.rrect(c, ex - 22, 990, ex + 22, 1066, 14, YELLOW)
                c.drawCircle(ex, 990, 18, G.P(YELLOW))
            elif out_at is not None and R.bs - out_at < 2.5:
                k = (R.bs - out_at) / 2.5         # la piccola che esce e va verso un'onda lontana (non lo dice nessuno)
                Figure(height=150, coat=YELLOW).draw(c, ex - 40 - 120 * k, 1230, breathe(POSES["stand"], s), facing=-1)
                ring_at(c, 760, 1180, R.t, a=0.25 * (1 - k), r=120)
            G.fog(c, *r, s + 2, a=0.45 + 0.45 * (1 - vis), col=fogc, seed=3)
            man = _p(b, "man")
            if man:
                walk = _p(b, "walk_at")
                k = ease((R.bs - walk) / 3.0) if walk is not None else 0.0
                mx = 470 - 520 * k
                pose = bent(POSES["stand"]) if man == "bent" else (POSES["stand"] if k == 0 else
                                                                   blend(POSES["stand"], POSES["stand_tense"], 0.3))
                fig = MAN if man != "bent" else Figure(height=300, fill=mix(BLUE_ROBE, (30, 20, 30), 0.35),
                                                       ink=(20, 16, 24))
                fig.draw(c, mx, 1210 if man != "bent" else 1236, breathe(pose, s), facing=-1 if man != "bent" else 1)
                if man != "bent":
                    ring_at(c, 90, 1080, R.t, a=0.4, r=160)
            if _p(b, "wife"):
                WIFE.draw(c, 560, 1060, breathe(POSES["plead"], s), facing=-1)
            G.vgrad(c, *r, fogc, fogc, a=0.12 + 0.3 * (1 - vis))
        else:
            # la casa di Ellie: finestre buie, gancio vuoto, una palla rossa sul prato; la casa "parla"
            G.house(c, 540, 1240, 680, 540, siding=(120, 138, 156), dark=0.3 + 0.6 * (1 - light), lit=())
            G.rect(c, 0, 1240, 1080, 1920, mix((56, 68, 60), (0, 0, 0), 1 - light))
            c.drawCircle(330, 1330, 34, G.P((210, 50, 50)))
            c.drawLine(390, 1000, 390, 1020, G.P((40, 40, 44), StrokeWidth=6))
            wins = [(250, 760), (720, 760), (250, 1010)]
            for wx, wy in wins:
                G.rect(c, wx + 6, wy + 6, wx + 120, wy + 130, (14, 16, 22), 0.85)
            G.fog(c, *r, s + 2, a=0.35 + 0.4 * (1 - vis), col=fogc, seed=3)
            for i, (wx, wy) in enumerate(wins):
                G.sound_rings(c, wx + 60, wy + 66, R.t + i * 0.55, col=(236, 240, 250), n=3, r_max=170, a=0.7, width=8)
            tap = _w(R, _p(b, "tap_word", "@@"))
            if 0 <= R.bs - tap < 0.7:
                age = R.bs - tap
                c.drawCircle(770, 810, 20 + 110 * age, G.P((236, 240, 250), 0.85 * (1 - age / 0.7), StrokeWidth=5,
                                                           Style=skia.Paint.kStroke_Style))
                G.rect(c, 724 + 8 * math.sin(R.t * 40), 776, 820, 860, (60, 64, 76), 0.6 * (1 - age / 0.7))

    wall = mix((44, 48, 60), (0, 0, 0), 0.5 * (1 - light))
    G.rect(c, -300, -300, 1380, 2220, wall)
    G.window(c, 80, 360, 1000, 1420, view, frame=(38, 38, 44), bars=(2, 2), sill=True,
             curtains=mix((90, 60, 60), (0, 0, 0), 0.5 * (1 - light)))
    gap = _p(b, "gap")
    if gap is not None:
        # la coperta sulla finestra: resta solo uno spiraglio (che si può richiudere a metà)
        close = _p(b, "close_at")
        g = gap
        if close is not None and R.bs >= close:
            g = gap * (1 - 0.5 * ease((R.bs - close) / 1.0))
        cx = _p(b, "gap_x", 540)
        blanket = (40, 34, 44)
        G.rect(c, 40, 320, cx - g / 2, 1470, blanket)
        G.rect(c, cx + g / 2, 320, 1040, 1470, blanket)
        for x in (cx - g / 2, cx + g / 2):
            c.drawLine(x, 320, x, 1470, G.P((60, 52, 64), StrokeWidth=6))
        for k in range(6):
            fx = 120 + k * 150
            if not (cx - g / 2 < fx < cx + g / 2):
                c.drawLine(fx, 330, fx + 20, 1460, G.P((32, 28, 36), 0.7, StrokeWidth=10))
    if _p(b, "clock"):
        G.wall_clock(c, 990, 240, 60, 7 * 60 + 52 + R.bs / 60)
        a = math.radians((R.t % 60) * 6)
        c.drawLine(990, 240, 990 + math.sin(a) * 50, 240 - math.cos(a) * 50, G.P((200, 40, 40), StrokeWidth=2))
    if _p(b, "you"):
        BIG.draw(c, 40, 2700, breathe(POSES["stand"], s), facing=1)
    if mood == "sunset":
        G.darkness(c, 0.25)


# ---------- strada vista dall'alto ----------

def _top_figure(c, x, y, t, walking=True, col=(232, 224, 205), scale=1.0, heading=-90.0):
    c.save()
    c.translate(x, y)
    c.rotate(heading + 90)
    c.scale(scale, scale)
    sw = math.sin(t * 7) * 9 if walking else 0.0
    ink = G.P((30, 26, 26), StrokeWidth=10, StrokeCap=skia.Paint.kRound_Cap)
    body = G.P(col, StrokeWidth=7, StrokeCap=skia.Paint.kRound_Cap)
    for side in (-1, 1):
        for p in (ink, body):
            c.drawLine(side * 7, 2, side * 8, 16 + side * sw * 0.8, p)
            c.drawLine(side * 14, -4, side * 17, 7 - side * sw, p)
    for p in (ink, body):
        c.drawLine(-14, -4, 14, -4, p)
    c.drawCircle(0, -6, 12, G.P((30, 26, 26)))
    c.drawCircle(0, -6, 9.5, G.P(col))
    c.restore()


def street_top(c, s, b, R):
    """Dall'alto: asfalto scuro, il vicino in vestaglia blu (l'unico colore) che va verso un'onda nella nebbia."""
    G.rect(c, -400, -400, 1480, 2320, (48, 58, 52))
    G.rect(c, 330, -400, 750, 2320, (52, 54, 60))
    for side in (-1, 1):
        G.rect(c, 540 + side * 210 - 26, -400, 540 + side * 210 + 26, 2320, (92, 92, 98))
    for k in range(-3, 13):
        G.rect(c, 535, k * 200, 545, k * 200 + 90, (180, 170, 110), 0.5)
    for i, y in enumerate((-200, 420, 1040, 1660)):
        for side in (-1, 1):
            x = 540 + side * 520
            roof = [(84, 74, 78), (74, 80, 94), (92, 80, 70), (70, 74, 72)][(i + (side > 0)) % 4]
            G.rect(c, x - 200, y, x + 200, y + 380, roof)
            c.drawLine(x - 200, y + 190, x + 200, y + 190, G.P(mix(roof, (0, 0, 0), 0.25), StrokeWidth=6))
    G.rrect(c, 640, 1240, 710, 1390, 16, (70, 74, 84))
    G.rrect(c, 648, 1270, 702, 1320, 8, (40, 44, 54))
    k = min(1.0, s / max(0.1, _p(b, "walk_dur", 3.2)))
    sx, sy = 880, 1010                           # parte dal suo vialetto (destra), attraversa verso sinistra
    tx, ty = 120, 760
    mx, my = sx + (tx - sx) * k, sy + (ty - sy) * k
    ring_at(c, tx - 40, ty - 30, R.t, a=0.5, r=240)
    G.fog(c, -400, -400, 1480, 2320, s + 7, a=0.4, col=(110, 118, 134), seed=9, n=14)
    _top_figure(c, mx, my, R.t, walking=True, col=BLUE_ROBE, scale=2.6,
                heading=math.degrees(math.atan2(ty - sy, tx - sx)))
    # la nebbia si stringe dai bordi
    sh = skia.GradientShader.MakeRadial((mx, my), 1000 - 450 * k, [rgba((110, 118, 134), 0), rgba((110, 118, 134), 0.95)])
    c.drawRect(skia.Rect(-400, -400, 1480, 2320), skia.Paint(Shader=sh))


# ---------- soggiorno ----------

def living(c, s, b, R):
    """Soggiorno largo (la camera si sposta): lampada e divano a sinistra, la finestra davanti al centro,
    il mobile con TV e cassa a destra. params: act = cover | strip | unplug | sit | listen | dark_phone | ellie."""
    act = _p(b, "act", "sit")
    G.room(c, (78, 70, 64), (74, 58, 48), horizon=1270, x0=-300, x1=1700, y0=-200, y1=2200)
    win = (600, 470, 1000, 1050)
    cover = _p(b, "cover", 1.0)                   # quanta finestra copre la coperta (0..1)
    if act == "cover":
        cover = 0.12 + 0.86 * ease((R.bs - 0.4) / 2.0)
    elif act == "strip":
        cover = 0.62
    shape_x = None
    if act == "strip":
        shape_x = 1150 - 560 * ease(R.bs / max(0.1, _w(R, "in.", 2.5, end=True)))

    def view(c, r):
        G.sky(c, *r, "fog")
        G.fog(c, *r, s, a=0.85, col=(110, 120, 140), seed=6)
        if shape_x is not None:
            SHAPE.draw(c, shape_x, 1900, bent(POSES["stand"], -42), facing=-1)

    G.window(c, *win, view, frame=(46, 42, 42))
    drop = _w(R, "in.", 99.0, end=True) if act == "strip" else 99.0
    if act == "strip" and R.bs >= drop - 0.3:
        cover = min(1.0, 0.62 + 0.38 * ease((R.bs - drop + 0.3) / 0.25))
    if cover > 0:
        x0, y0, x1, y1 = win
        bw = (x1 - x0 + 40) * cover
        G.rect(c, x0 - 20, y0 - 20, x0 - 20 + bw, y1 + 20, (44, 36, 48))
        for k in range(6):
            fx = x0 + k * 70
            if fx + 14 < x0 - 20 + bw:
                c.drawLine(fx, y0 - 10, fx + 14, y1 + 10, G.P((34, 28, 38), 0.7, StrokeWidth=9))
        for (tx, ty) in ((x0 - 10, y0 - 10), (x0 - 20 + bw - 10, y0 - 10), (x0 - 10, y1 + 10), (x0 - 20 + bw - 10, y1 + 10)):
            G.rect(c, tx - 14, ty - 8, tx + 24, ty + 8, (200, 196, 170), 0.85)
        if _p(b, "ring_fabric"):
            dx = _p(b, "ring_dx", 0)
            rx = (x0 + x1) / 2 + (dx * (1 - 2 * min(1.0, R.bs / 3.0)) if dx else 0)
            ring_at(c, rx, (y0 + y1) / 2, R.t, a=0.4, r=240)
    G.picture(c, 330, 560, 500, 700, inner=(110, 130, 150))
    G.couch(c, 90, 1270, 430, 240, col=(70, 82, 88))
    G.lamp(c, 40, 1270, 520, on=True)
    # mobile con TV e cassa, a destra; la presa a muro accanto
    G.rect(c, 1120, 1080, 1520, 1270, (66, 50, 40))
    G.rrect(c, 1060, 1150, 1096, 1196, 6, (210, 206, 196))
    tv_on = _p(b, "tv", 0.0)
    unplug_tv = _w(R, _p(b, "unplug_tv", "@@"), end=True)
    unplug_spk = _w(R, _p(b, "unplug_spk", "@@"), end=True)
    tv_live = tv_on > 0 and R.bs < unplug_tv
    unplugged = R.bs >= unplug_tv or _p(b, "unplugged", False)
    G.tv(c, 1150, 900, 1410, 1068, on=0.0, unplugged=True)
    if not unplugged:
        c.drawLine(1078, 1172, 1150, 1100, G.P((30, 30, 34), StrokeWidth=5))
    if tv_live:
        rng = np.random.default_rng(int(R.t * 30))
        for k in range(26):
            yy = 916 + k * 5.8
            G.rect(c, 1164, yy, 1396, yy + 4, (int(rng.uniform(90, 200)),) * 3, 0.85)
        ring_at(c, 1280, 984, R.t, a=0.4, r=150)
    elif tv_on > 0 and R.bs - unplug_tv < 0.3:
        k = (R.bs - unplug_tv) / 0.3
        G.rect(c, 1280 - 116 * (1 - k), 982, 1280 + 116 * (1 - k), 986, (230, 230, 240))
        c.drawCircle(1280, 984, 6 * (1 - k), G.P((255, 255, 255)))
    led = _p(b, "led", 0.0)
    if R.bs >= unplug_spk:
        led = 0.0
    G.smart_speaker(c, 1470, 1080, h=110, ring=led, t=R.t)
    # tu
    if act == "cover":
        J = YOU.draw(c, 800, 1560, breathe(blend(POSES["stand"], POSES["cover"], ease(R.bs / 0.5)), s), facing=-1)
    elif act == "strip":
        # solo il braccio che tiene ferma la coperta sul bordo
        arm = skia.Path()
        arm.moveTo(700, 1300)
        arm.quadTo(760, 1000, 860, 820)
        c.drawPath(arm, G.P((44, 36, 32), StrokeWidth=58, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))
        c.drawPath(arm, G.P((233, 224, 205), StrokeWidth=34, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))
        J = None
    elif act == "unplug":
        J = YOU.draw(c, 1200, 1560, breathe(POSES["kneel_reach"], s), facing=-1)
    elif act in ("sit", "listen"):
        ps = dict(POSES["sit_couch"], head=24) if act == "sit" else dict(POSES["sit_couch"], rsh=20, rel=60)
        J = YOU.draw(c, 300, 1150, breathe(ps, s), facing=1, feet=False)
    else:   # dark_phone, ellie: in piedi davanti alla finestra coperta, col telefono acceso
        J = YOU.draw(c, 470, 1560, breathe(POSES["text"], s), facing=1)
    if act in ("sit", "listen", "dark_phone", "ellie"):
        hx, hy = J["rhand"]
        G.rrect(c, hx - 14, hy - 26, hx + 14, hy + 26, 6, (20, 20, 24))
        G.rect(c, hx - 10, hy - 22, hx + 10, hy + 22, (150, 170, 230))
        G.glow(c, hx, hy, 170, (150, 170, 255), 0.4)
    dark = _p(b, "dark", 0.0)
    if dark > 0:
        lights = []
        if act in ("dark_phone", "ellie"):
            hx, hy = J["rhand"]
            lights += [(hx, hy, 560, 0.92), (800, 760, 380, 0.5)]
        G.darkness(c, dark, lights=lights)

def flashlight(c, s, b, R):
    """Primo piano della torcia: un cilindro grigio col pulsante, nel braccio che trema."""
    G.rect(c, -300, -300, 1380, 2220, (6, 6, 9))
    G.glow(c, 540, 1300, 600, (150, 170, 255), 0.18)
    tr = math.sin(R.t * 37) * 2
    c.save()
    c.translate(540 + tr, 1000)
    c.rotate(-24)
    arm = G.P((40, 34, 30), StrokeWidth=110, StrokeCap=skia.Paint.kRound_Cap)
    c.drawLine(-80, 760, -20, 160, arm)
    c.drawLine(-80, 760, -20, 160, G.P(mix((233, 224, 205), (40, 46, 70), 0.45), StrokeWidth=82, StrokeCap=skia.Paint.kRound_Cap))
    G.rrect(c, -70, -260, 70, 260, 26, (70, 72, 80))
    G.rrect(c, -86, -330, 86, -230, 18, (90, 92, 100))
    G.rect(c, -60, -250, 60, 240, (82, 84, 92))
    for k in range(6):
        c.drawLine(-60, -150 + k * 60, 60, -150 + k * 60, G.P((60, 62, 70), StrokeWidth=4))
    on = _p(b, "on_at")
    c.drawCircle(0, 20, 30, G.P((40, 40, 46)))
    c.drawCircle(0, 20, 30, G.P((160, 190, 255), 0.4 + 0.2 * math.sin(R.t * 4), StrokeWidth=4, Style=skia.Paint.kStroke_Style))
    c.restore()
    G.darkness(c, 0.5, lights=[(540, 1000, 600, 0.8)])


def front_walk(c, s, b, R):
    """Dalla finestra (coperta sollevata), il fascio della torcia nella nebbia: Ellie in fondo al vialetto.
    params: ellie = lost | turn | step; shape = 0..1 (la cosa che si alza dietro di lei) | lean; you; strike."""
    G.rect(c, -300, -300, 1380, 2220, (3, 4, 7))

    def view(c, r):
        G.sky(c, *r, "night")
        G.rect(c, 0, 1250, 1080, 1920, (22, 26, 24))
        G.rect(c, 420, 1250, 660, 1920, (54, 52, 50))           # il vialetto verso di noi
        st = _p(b, "ellie", "lost")
        k = ease(R.bs / 1.2)
        ey = 1290 + (90 * k if st == "step" else (90 if st in ("near", "lean") else 0))
        ex = 560 + 30 * math.sin(R.t * 0.4)
        if st == "lost":
            pose = bent(dict(POSES["point"], rsh=80 + 10 * math.sin(R.t * 1.3)))
            facing = -1
        else:
            pose = bent(dict(POSES["point"], rsh=78))
            facing = 1 if st in ("turn", "step", "near", "lean") else -1
        sh = _p(b, "shape", 0.0)
        if sh:
            k2 = ease((R.bs - _p(b, "shape_at", 0.0)) / 1.4) if isinstance(sh, (int, float)) else 1.0
            lean = 0.0
            if sh == "lean":
                lean = ease(R.bs / 2.0)
                k2 = 1.0
            sp = bent(blend(POSES["stand"], POSES["crouch"], 0.0), -42)
            sp["torso"] = 30 * lean
            SHAPE.shade = 0.0
            SHAPE.height = 1000
            c.saveLayerAlpha(None, int(255 * min(1.0, k2)))
            SHAPE.draw(c, ex + 120, ey - 40 + (1 - k2) * 500, sp, facing=-1)
            c.restore()
        shake = math.sin(R.t * 41) * 1.5
        J = ELLIE.draw(c, ex + shake, ey, breathe(pose, s * 2, amount=0.5), facing=facing)
        # il telefono che le si accende in mano
        hx, hy = J["lhand"]
        G.rrect(c, hx - 9, hy - 16, hx + 9, hy + 16, 4, (20, 20, 24))
        G.rect(c, hx - 6, hy - 13, hx + 6, hy + 13, (170, 190, 255))
        G.glow(c, hx, hy, 70, (150, 170, 255), 0.35)
        G.fog(c, *r, s + 4, a=0.7, col=NIGHT_FOG, seed=14)
        G.darkness(c, 0.96, lights=[(560, 1130, 560, 1.0)])
        G.beam(c, 540, 1980, -88, spread=26, length=1100, a=0.22)
        G.dust(c, 300, 700, 800, 1900, s, n=50, a=0.5, col=(220, 226, 240))

    G.window(c, 60, 300, 1020, 1700, view, frame=(24, 24, 28), bars=(1, 1), sill=False)
    # la coperta sollevata in un angolo
    G.rect(c, 40, 280, 1040, 420, (40, 34, 44))
    p = skia.Path()
    p.addPoly([skia.Point(1040, 420), skia.Point(1040, 1720), skia.Point(860, 1720), skia.Point(1040, 420)], True)
    c.drawPath(p, G.P((40, 34, 44)))
    if _p(b, "strike"):
        k = R.bs
        if k < 0.5 and int(k * 20) % 2 == 0:
            gfx.draw_text(c, "RULE #1", K.heavy(44), 980, 520, color=(255, 70, 60), alpha=0.7, align="right")
            c.drawLine(800, 505, 990, 505, G.P((255, 70, 60), 0.8, StrokeWidth=5))
    if _p(b, "you"):
        BIG.draw(c, -60, 2950, POSES["flashlight"], facing=1)


def ellie_phone(c, s, b, R):
    """Il fascio si stringe sulla mano di Ellie: ha in mano un telefono con la stessa chat, dall'altra parte."""
    G.rect(c, -300, -300, 1380, 2220, (3, 4, 7))
    G.fog(c, -200, 0, 1280, 1920, s, a=0.5, col=NIGHT_FOG, seed=30)
    G.darkness(c, 0.85, lights=[(540, 960, 760, 1.0)])
    tr = math.sin(R.t * 33) * 3
    c.save()
    c.translate(540 + tr, 980)
    c.rotate(6)
    # il braccio nell'impermeabile giallo che entra dal basso e tiene il telefono
    arm = skia.Path()
    arm.moveTo(-520, 900)
    arm.quadTo(-260, 640, -60, 430)
    c.drawPath(arm, G.P((40, 30, 10), StrokeWidth=190, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))
    c.drawPath(arm, G.P(YELLOW, StrokeWidth=170, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))
    c.drawCircle(-50, 440, 70, G.P((233, 224, 205)))

    def chat(c, r):
        G.chat_screen(c, r, "Sweetie", [("blue kite. never out loud.", True, -9), ("ok. text me every 5 min", False, -9)],
                      t=9, status="")
    G.phone(c, 0, 0, 470, 980, chat, glow_a=0.35)
    c.restore()


def window_tap(c, s, b, R):
    """Strisciata di luce, stacco secco: il cerchio della torcia su una finestra coperta, un colpo sul vetro."""
    G.rect(c, -300, -300, 1380, 2220, (2, 2, 4))
    if R.bs < 0.07:
        G.rect(c, -300, 800, 1380, 1100, (255, 255, 255), 0.8)
        return
    small = _p(b, "small", False)
    cx, cy = 540, 900
    w, h = (300, 380) if small else (520, 600)
    G.glow(c, cx, cy, 520, (230, 236, 250), 0.25)
    shiver = 0.0
    tap = _w(R, _p(b, "tap_word", "One"))
    if R.bs >= tap:
        shiver = math.sin(R.t * 60) * 4 * max(0.0, 1 - (R.bs - tap) / 0.5)
    G.rect(c, cx - w / 2 - 20, cy - h / 2 - 20, cx + w / 2 + 20, cy + h / 2 + 20, (40, 40, 44))
    G.rect(c, cx - w / 2 + shiver, cy - h / 2, cx + w / 2 + shiver, cy + h / 2, (52, 44, 58))
    for k in range(5):
        x = cx - w / 2 + k * w / 5 + 20
        c.drawLine(x + shiver, cy - h / 2, x + 18 + shiver, cy + h / 2, G.P((40, 34, 46), 0.8, StrokeWidth=10))
    if 0 <= R.bs - tap < 0.7:
        age = R.bs - tap
        c.drawCircle(cx, cy - 40, 30 + 160 * age, G.P((240, 244, 255), 0.9 * (1 - age / 0.7), StrokeWidth=6,
                                                     Style=skia.Paint.kStroke_Style))
    G.darkness(c, 0.9, lights=[(cx, cy, 420, 1.0)])


def black_title(c, s, b, R):
    G.rect(c, -300, -300, 1380, 2220, (6, 6, 8))


def endcard(c, s, b, R):
    """Cartello finale + la cassa staccata che si accende da sola mentre torna la voce."""
    R.endcard(c, s, b)
    G.fog(c, -300, 380, 1380, 760, s * 2 + 4, a=0.2, col=(140, 144, 152), seed=22, n=5, stretch=3.5)
    on = ease((s - 1.8) / 0.5) * (0.7 + 0.3 * math.sin(s * 9))
    if on > 0:
        G.rrect(c, 490, 1290, 590, 1302, 4, (230, 240, 255), on)
        G.glow(c, 540, 1296, 150, (200, 225, 255), 0.5 * on)


SCENES = {f.__name__: f for f in (bedroom, phone, house_ext, window_view, street_top, living, flashlight,
                                  front_walk, ellie_phone, window_tap, black_title, endcard)}
