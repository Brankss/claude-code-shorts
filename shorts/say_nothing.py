"""SAY NOTHING, episodio 1: la nebbia che imita le voci. Scene disegnate con pov_gfx e lo stickman.

Ogni scena è una funzione (c, s, b, R): s = secondi dall'inizio dell'inquadratura, b = beat corrente,
R = renderer (R.bs = secondi dall'inizio del beat, R.t = tempo del video). I parametri che cambiano da
un'inquadratura all'altra (ora del giorno, cosa succede) arrivano da b.params.
"""

import math

import numpy as np
import skia

from . import gfx
from . import pov_gfx as G
from .gfx import mix, rgba
from .stick import POSES, Figure, blend, breathe, ease

YOU = Figure(height=560)
FOG = (168, 172, 176)
YELLOW = (244, 198, 40)

MOODS = {
    # cielo/nebbia, colore della nebbia, luce generale (0 = buio)
    "dawn": ("fog", (150, 156, 164), 0.75),
    "noon": ("fog", (176, 178, 180), 1.0),
    "sunset": ("sunset", (226, 150, 100), 0.7),
    "night": ("night", (40, 44, 56), 0.25),
    "dark": ("night", (18, 20, 28), 0.0),
}


def _p(b, key, default=None):
    return b.params.get(key, default)


# ---------- camera da letto all'alba ----------

def bedroom(c, s, b, R):
    mood = _p(b, "mood", "dawn")
    sky, fogc, light = MOODS[mood]
    wall = mix((56, 62, 82), (0, 0, 0), 1 - light)
    G.room(c, wall, mix((64, 58, 66), (0, 0, 0), 1 - light), horizon=1260)

    def view(c, r):
        G.sky(c, *r, sky)
        G.house(c, (r[0] + r[2]) / 2 + 40, r[3] + 40, 360, 300, dark=0.35)
        G.fog(c, *r, s, a=0.95, col=fogc, seed=2)
        G.vgrad(c, *r, fogc, fogc, a=0.35)

    G.window(c, 400, 360, 760, 820, view, frame=(44, 44, 50))
    G.shaft(c, 400, 820, 760, 820, 120, 520, col=(200, 210, 225), a=0.06 * light, angle=12)
    G.bed(c, 120, 1260, 780, blanket=(58, 66, 104))
    # comodino con il telefono che si illumina
    G.rect(c, 860, 1080, 1020, 1260, (66, 50, 40))
    G.rect(c, 850, 1060, 1030, 1084, (80, 62, 50))
    on = _p(b, "phone_on", 1.0)
    G.rrect(c, 905, 1046, 975, 1060, 4, (20, 20, 24))
    if on > 0:
        pulse = 0.6 + 0.4 * abs(math.sin(R.t * 5))
        G.glow(c, 940, 1040, 180, (160, 180, 255), 0.35 * on * pulse)
    pose = _p(b, "pose", "sit_up_bed")
    if pose in ("sit_up_bed", "lie"):
        ps = POSES[pose]
        if _p(b, "wake", False):          # si tira su a sedere all'inizio
            ps = blend(POSES["lie"], POSES["sit_up_bed"], ease((R.bs - 0.2) / 0.9))
        YOU.draw(c, 360, 1062, breathe(ps, s), facing=1, feet=False)
        G.rrect(c, 120 + 160, 1260 - 220, 120 + 780 + 8, 1260 - 120, 30, (58, 66, 104))
        for k in (0.4, 0.65, 0.85):
            c.drawLine(280 + 630 * k, 1045, 260 + 630 * k, 1135, G.P((44, 50, 80), 0.6, StrokeWidth=4))
    else:
        YOU.draw(c, 520, 1500, breathe(POSES[pose], s), facing=1)
    G.darkness(c, 0.35 * (1 - light) + 0.15, lights=[(940, 1040, 300, 0.8 * on)])


# ---------- casa vista da fuori ----------

def house_ext(c, s, b, R):
    mood = _p(b, "mood", "dawn")
    sky, fogc, light = MOODS[mood]
    G.sky(c, 0, 0, 1080, 1920, sky)
    dark = 1 - light
    lights_on = _p(b, "lights", 1.0)
    G.house(c, -140, 1300, 560, 440, dark=0.3 + 0.5 * dark, lit=() if lights_on < 1 else (0,))
    G.house(c, 560, 1320, 640, 500, lit=_p(b, "lit", (3,)), porch_light=_p(b, "porch", 0.0), dark=0.15 + 0.6 * dark)
    G.house(c, 1220, 1300, 560, 440, dark=0.3 + 0.5 * dark)
    G.rect(c, -200, 1320, 1280, 1500, mix((70, 82, 72), (0, 0, 0), dark * 0.8))
    G.rect(c, -200, 1500, 1280, 2200, mix((62, 64, 70), (0, 0, 0), dark * 0.8))
    for i, x in enumerate((60, 940)):
        die = _p(b, "lamps_die_at")
        on = 1.0 if die is None else (1.0 if R.bs < die + i * 0.6 else 0.0)
        if die is not None and 0 <= R.bs - (die + i * 0.6) < 0.25:
            on = 0.5 * (1 + math.sin(R.t * 80))
        G.streetlight(c, x, 1500, 620, on=on * (1 if mood in ("night", "dark", "sunset") else 0.3))
    G.fog(c, -100, 500, 1180, 1900, s + 3, a=0.6, col=fogc, seed=5)
    pin = _p(b, "pin")
    if pin:
        G.pin(c, 560, 1060, pin, a=min(1.0, R.bs / 0.4))


# ---------- telefono ----------

def phone(c, s, b, R):
    """Telefono appoggiato sul comodino (cavo, luce dello schermo). params: ui = lock | alert | chat."""
    c.drawRect(skia.Rect(-200, -200, 1280, 2120), G.P((24, 20, 22)))
    G.vgrad(c, 0, 0, 1080, 1920, (34, 28, 30), (12, 10, 12))
    p = skia.Path()
    p.moveTo(560, 1520)
    p.cubicTo(600, 1700, 420, 1760, 470, 2000)
    c.drawPath(p, G.P((210, 210, 214), StrokeWidth=12, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))
    c.drawCircle(940, 1460, 110, G.P((30, 26, 28)))
    c.drawCircle(940, 1460, 110, G.P((60, 52, 50), StrokeWidth=4, Style=skia.Paint.kStroke_Style))
    ui = _p(b, "ui", "lock")
    t = R.bs
    buzz = _p(b, "buzz", 0.0)
    jx = math.sin(R.t * 70) * 3 * buzz if (R.t * 1.6) % 1 < 0.6 else 0.0
    if ui == "lock":
        notifs = _p(b, "notifs", [])
        G.phone(c, 540 + jx, 900, 560, 1180, lambda c, r: G.lock_screen(c, r, _p(b, "time", "6:42"), _p(b, "date", "Tuesday"),
                                                                           notifs, t=t), tilt=-5, glow_a=0.3)
    elif ui == "alert":
        lines = _p(b, "lines", [])
        G.phone(c, 540 + jx, 900, 560, 1180, lambda c, r: G.alert_screen(c, r, _p(b, "title", "EMERGENCY ALERT"),
                                                                            _p(b, "kind", "EXTREME THREAT"), lines, t=t),
                tilt=-5, glow_a=0.45, glow_col=(255, 60, 50))
    else:
        G.phone(c, 540 + jx, 900, 560, 1180, lambda c, r: G.chat_screen(c, r, _p(b, "name", "Mom"), _p(b, "msgs", []), t=t,
                                                                           typing_at=_p(b, "typing"),
                                                                           status=_p(b, "status", "online")),
                tilt=-5, glow_a=0.3)


# ---------- strada vista dall'alto ----------

def _top_figure(c, x, y, t, walking=True, col=(232, 224, 205), scale=1.0, coat=None, heading=-90.0):
    """Persona vista dall'alto: testa tonda, spalle, braccia e gambe che si alternano camminando."""
    c.save()
    c.translate(x, y)
    c.rotate(heading + 90)
    c.scale(scale, scale)
    sw = math.sin(t * 7) * 9 if walking else 0.0
    ink = G.P((40, 34, 30), StrokeWidth=9, StrokeCap=skia.Paint.kRound_Cap)
    body = G.P(coat or col, StrokeWidth=6, StrokeCap=skia.Paint.kRound_Cap)
    for side in (-1, 1):
        for p in (ink, body):
            c.drawLine(side * 7, 2, side * 8, 14 + side * sw * 0.8, p)     # gambe
            c.drawLine(side * 13, -4, side * 16, 6 - side * sw, p)          # braccia
    for p in (ink, body):
        c.drawLine(-13, -4, 13, -4, p)
    c.drawCircle(0, -6, 11, G.P((40, 34, 30)))
    c.drawCircle(0, -6, 8.5, G.P(coat or col))
    c.restore()


def street_top(c, s, b, R):
    """Strada vista dall'alto nella nebbia: tetti, prati, auto; un uomo cammina verso un'onda sonora."""
    rng = np.random.default_rng(12)
    G.rect(c, -300, -300, 1380, 2220, (62, 74, 64))
    G.rect(c, 380, -300, 700, 2220, (58, 60, 66))
    for side in (-1, 1):
        G.rect(c, 540 + side * 160 - 22, -300, 540 + side * 160 + 22, 2220, (110, 110, 114))
    for k in range(-2, 12):
        G.rect(c, 535, k * 200, 545, k * 200 + 90, (200, 190, 120), 0.6)
    for i, y in enumerate((80, 620, 1160, 1700)):
        for side in (-1, 1):
            x = 540 + side * 380
            roof = [(110, 96, 100), (96, 104, 120), (120, 104, 92), (90, 96, 92)][(i + (side > 0)) % 4]
            G.rect(c, x - 150, y, x + 150, y + 330, roof)
            c.drawLine(x - 150, y + 165, x + 150, y + 165, G.P(mix(roof, (0, 0, 0), 0.25), StrokeWidth=6))
            G.rect(c, x - side * 150 - (30 if side > 0 else -10), y + 140, x - side * 150 + (10 if side > 0 else 30), y + 190,
                   (150, 146, 140))   # vialetto verso la strada
    for x, y, col in ((470, 380, (150, 40, 40)), (610, 990, (60, 80, 120)), (470, 1480, (200, 200, 205))):
        G.rrect(c, x - 34, y - 70, x + 34, y + 70, 16, col)
        G.rrect(c, x - 26, y - 40, x + 26, y + 10, 8, mix(col, (20, 30, 40), 0.6))
    # l'uomo che segue la voce e la moglie sul vialetto
    k = min(1.0, s / max(0.1, _p(b, "walk_dur", 4.0)))
    mx, my = 300 + 240 * k, 1060 - 520 * k
    ring = _p(b, "ring", (560, 380))
    G.sound_rings(c, ring[0], ring[1], R.t, col=(220, 230, 255), n=3, r_max=200, a=0.5)
    _top_figure(c, mx, my, R.t, walking=True, heading=math.degrees(math.atan2(-520, 240)))
    _top_figure(c, 170, 1100, R.t, walking=False, col=(200, 196, 210), heading=-20)
    # l'impermeabile giallo minuscolo che nessuno nomina (per chi riguarda il video)
    ex = 900 + 60 * k
    _top_figure(c, ex, 1700 - 300 * k, R.t + 1, walking=True, coat=YELLOW, scale=0.75, heading=-75)
    G.fog(c, -200, -200, 1280, 2120, s + 7, a=0.55, col=FOG, seed=9, n=16)
    # la nebbia si chiude sull'uomo man mano che arriva all'onda
    G.glow(c, ring[0], ring[1], 260 + 120 * k, FOG, 0.5 + 0.4 * k, plus=False)


# ---------- finestra sulla casa di Ellie (il misuratore della giornata) ----------

def window_view(c, s, b, R):
    mood = _p(b, "mood", "dawn")
    sky, fogc, light = MOODS[mood]
    vis = _p(b, "vis", 1.0)          # 1 = la casa si vede bene, 0 = solo nebbia
    wall = mix((50, 54, 66), (0, 0, 0), 0.6 * (1 - light))

    def view(c, r):
        x0, y0, x1, y1 = r
        G.sky(c, *r, sky)
        G.house(c, 560, 1260, 620, 500, dark=0.2 + 0.6 * (1 - light), lit=_p(b, "lit", ()), porch_light=_p(b, "porch", 0.0),
                siding=(120, 140, 160))
        G.rect(c, 0, 1260, 1080, 1920, mix((70, 82, 72), (0, 0, 0), 1 - light))
        # altalena, bici, impermeabile giallo appeso al portico
        sw = _p(b, "swing", 1.0)
        if sw > 0:
            c.drawLine(140, 1260, 200, 1020, G.P((60, 60, 64), sw, StrokeWidth=8))
            c.drawLine(300, 1260, 240, 1020, G.P((60, 60, 64), sw, StrokeWidth=8))
            c.drawLine(190, 1020, 250, 1020, G.P((60, 60, 64), sw, StrokeWidth=8))
            ang = math.sin(R.t * 1.4) * 8 * _p(b, "swing_move", 0.0)
            c.save()
            c.translate(220, 1020)
            c.rotate(ang)
            c.drawLine(-14, 0, -14, 150, G.P((40, 40, 44), sw, StrokeWidth=3))
            c.drawLine(14, 0, 14, 150, G.P((40, 40, 44), sw, StrokeWidth=3))
            G.rect(c, -24, 150, 24, 160, (120, 60, 50), sw)
            c.restore()
        if _p(b, "coat_hook", True):
            G.rrect(c, 760, 920, 800, 1010, 12, YELLOW)
            c.drawCircle(780, 925, 16, G.P(YELLOW))
        if _p(b, "rings", False):
            for wx, wy in ((430, 880), (690, 880), (430, 1090)):
                G.sound_rings(c, wx, wy, R.t + wx * 0.01, col=(220, 230, 255), n=3, r_max=150, a=0.45)
        G.fog(c, *r, s + 2, a=0.55 + 0.45 * (1 - vis), col=fogc, seed=3)
        G.vgrad(c, *r, fogc, fogc, a=0.1 + 0.6 * (1 - vis))

    G.rect(c, -200, -200, 1280, 2120, wall)
    G.window(c, 110, 380, 970, 1460, view, frame=(40, 40, 46), bars=(2, 2), sill=True,
             curtains=mix((90, 60, 60), (0, 0, 0), 0.5 * (1 - light)))
    if _p(b, "you", False):
        YOU.shade = 0.6
        YOU.draw(c, 220, 2000, breathe(POSES["stand"], s), facing=1)
        YOU.shade = 0.0


# ---------- soggiorno ----------

def living(c, s, b, R):
    """Soggiorno: TV e smart speaker da staccare, porta d'ingresso con l'asciugamano sotto, tu col telefono."""
    mood = _p(b, "mood", "dawn")
    sky, fogc, light = MOODS[mood]
    G.room(c, mix((92, 84, 74), (0, 0, 0), 0.55 * (1 - light)), mix((86, 64, 50), (0, 0, 0), 0.5 * (1 - light)),
           horizon=1270)
    G.window(c, 700, 420, 1000, 900, lambda c, r: (G.sky(c, *r, sky), G.fog(c, *r, s, a=1.0, col=fogc, seed=6),
                                                    G.vgrad(c, *r, fogc, fogc, a=0.5)), frame=(48, 44, 44))
    G.door(c, 80, 560, 340, 1270, light_under=0.0, chain=True)
    towel = _p(b, "towel", 0.0)
    if towel > 0:
        G.rrect(c, 80 - 10, 1250, 80 + 260 * min(1, towel) + 10, 1286, 14, (190, 210, 220))
    G.picture(c, 420, 520, 600, 660, inner=(110, 130, 150))
    G.couch(c, 640, 1270, 400, 240, col=(70, 82, 88))
    tv_on = _p(b, "tv_on", 0.0)
    G.tv(c, 400, 860, 640, 1010, on=tv_on, t=R.t, unplugged=_p(b, "unplugged", False))
    G.rect(c, 390, 1010, 650, 1270, (70, 52, 42))
    spk = _p(b, "speaker_ring", 0.0)
    G.smart_speaker(c, 600, 1010, h=96, ring=spk, t=R.t)
    if spk > 0:
        G.sound_rings(c, 600, 950, R.t, col=(120, 200, 255), n=2, r_max=140, a=0.35 * spk)
    pose = _p(b, "pose", "text")
    x = _p(b, "x", 560)
    if isinstance(pose, tuple):     # (posa_da, posa_a, durata): cambia posa durante il beat
        p0, p1, d = pose
        ps = blend(POSES[p0], POSES[p1], ease(R.bs / d))
    else:
        ps = POSES[pose]
    YOU.draw(c, x, 1500, breathe(ps, s), facing=_p(b, "facing", -1))
    if _p(b, "phone_glow", True) and light < 0.9:
        G.glow(c, x - 40, 1080, 200, (160, 180, 255), 0.25)
    dark = _p(b, "dark", 0.0)
    if dark > 0:
        lights = [(600, 920, 260, spk)] if spk > 0 else []
        G.darkness(c, dark, lights=lights)


# ---------- cucina al buio ----------

def kitchen(c, s, b, R):
    """Cucina: frigo, piano di lavoro, due finestre sulla nebbia. Con la torcia e i colpi ai vetri."""
    G.room(c, (70, 76, 72), (74, 70, 66), horizon=1300)
    for i, (x0, x1) in enumerate(((120, 420), (640, 940))):
        def view(c, r, i=i):
            G.sky(c, *r, "night")
            G.fog(c, *r, s + i * 3, a=1.0, col=(60, 64, 76), seed=10 + i)
        G.window(c, x0, 420, x1, 820, view, frame=(52, 52, 56))
    G.counter(c, 40, 1040, 1300, h=330)
    fl = _p(b, "fridge_light", 0.0)
    G.fridge(c, 860, 760, 1060, 1300, light=fl)
    tap = _p(b, "tap", None)       # (finestra, istante) del colpo sul vetro
    beam_to = _p(b, "beam", None)
    ang = None
    if beam_to is not None:
        ang = beam_to + math.sin(R.t * 1.3) * 3 if not isinstance(beam_to, tuple) else \
            beam_to[0] + (beam_to[1] - beam_to[0]) * ease(R.bs / beam_to[2])
    facing = 1 if ang is None or math.cos(math.radians(ang)) >= 0 else -1
    pose = dict(POSES[_p(b, "pose", "flashlight")])
    if ang is not None:
        # il braccio punta dove va la luce
        up = -math.degrees(math.asin(max(-1, min(1, math.sin(math.radians(ang))))))
        pose["rsh"], pose["rel"] = 90 + up, 0
    J = YOU.draw(c, _p(b, "x", 560), 1560, breathe(pose, s), facing=facing)
    if ang is not None:
        hx, hy = J["rhand"]
        G.darkness(c, 0.94, lights=[(hx + math.cos(math.radians(ang)) * 420, hy + math.sin(math.radians(ang)) * 420,
                                     440, 0.9), (hx, hy, 260, 0.5)])
        G.beam(c, hx, hy, ang, spread=26, length=1100, a=0.32)
    else:
        G.darkness(c, _p(b, "dark", 0.0))
    if tap is not None:
        wi, at = tap
        age = R.bs - at
        if 0 <= age < 0.6:
            x0, x1 = ((120, 420), (640, 940))[wi]
            G.glow(c, (x0 + x1) / 2, 620, 260, (200, 210, 230), 0.25 * (1 - age / 0.6))
            for k in range(4):     # impronta di una mano sul vetro appannato
                c.drawCircle((x0 + x1) / 2 - 30 + k * 20, 590, 9, G.P((220, 225, 235), 0.5 * (1 - age / 0.6)))
            G.rrect(c, (x0 + x1) / 2 - 40, 600, (x0 + x1) / 2 + 40, 680, 30, (220, 225, 235), 0.4 * (1 - age / 0.6))


# ---------- il portico con la torcia ----------

def porch(c, s, b, R):
    """Dalla finestra di casa, la torcia trova Ellie in fondo ai gradini del portico. Asciutta, nella nebbia."""
    G.rect(c, -200, -200, 1280, 2120, (4, 5, 8))

    def view(c, r):
        G.sky(c, *r, "night")
        G.rect(c, 0, 1240, 1080, 1920, (24, 28, 26))
        for k in range(5):     # i gradini del portico che scendono verso il prato
            G.rect(c, 260 - k * 40, 1500 + k * 60, 820 + k * 40, 1560 + k * 60, (84, 80, 76))
            G.rect(c, 260 - k * 40, 1500 + k * 60, 820 + k * 40, 1512 + k * 60, (104, 100, 96))
        G.fog(c, *r, s + 4, a=0.8, col=(70, 74, 84), seed=14)
        pose = POSES[_p(b, "kid_pose", "wave")] if R.bs > _p(b, "wave_at", 0.0) else POSES["stand"]
        Ellie.draw(c, 540, 1480, breathe(pose, s * 2, amount=0.6), facing=1)
        G.darkness(c, 0.95, lights=[(540, 1300, 430, 1.0)])
        G.beam(c, 540, 1950, -90, spread=24, length=900, a=0.18)
    G.window(c, 60, 300, 1020, 1700, view, frame=(30, 30, 34), bars=(1, 1), sill=False)
    # gocce sul vetro (fuori è fradicio; lei no)
    rng = np.random.default_rng(15)
    for k in range(40):
        x, y = rng.uniform(70, 1010), rng.uniform(310, 1690)
        r = rng.uniform(2, 5)
        c.drawCircle(x, y, r, G.P((150, 160, 180), 0.2))
        c.drawLine(x, y, x + rng.uniform(-2, 2), y + rng.uniform(10, 40), G.P((150, 160, 180), 0.12, StrokeWidth=r))


Ellie = Figure(height=420, coat=YELLOW, face=None)
