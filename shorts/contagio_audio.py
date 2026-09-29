"""Colonna sonora di Contagio, sincronizzata con la timeline del video."""

import numpy as np

from . import audio as A
from .contagio import W
from .contagio_render import TOTAL

BPM = 128
BEAT = 60 / BPM
# La minore: Am - F - C - G (una battuta per accordo).
PROGRESSION = [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])]
PENTA = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84]  # una nota per squadra


def build(tl):
    rec = tl.rec
    mx = A.Mixer(TOTAL)
    t_slow, t_win = tl.vt_slow, tl.vt_win
    ev = {kind: tl.vt(t) for t, kind, _ in rec.events}
    t_speed = ev.get("speed", 99)
    t_gap = ev.get("gap", 99)

    # ---------- musica ----------
    beat_i = 0
    t = 0.0
    while t < TOTAL:
        playing = t < t_slow - 0.05 or t >= t_win
        bar, pos = divmod(beat_i, 4)
        root, chord = PROGRESSION[bar % 4]
        hot = t >= t_speed or t >= t_win
        max_ = t >= t_gap or t >= t_win
        if playing:
            mx.add("music", t, A.kick(), 0.9)
            mx.sidechain(t)
            for sub in (0.5,):
                mx.add("music", t + BEAT * sub, A.bass(A.note(root), BEAT * 0.45), 0.55)
            mx.add("music", t + BEAT * 0.5, A.hat(), 0.35, pan=0.2)
            if hot:
                for sub in (0.25, 0.75):
                    mx.add("music", t + BEAT * sub, A.hat(), 0.18, pan=-0.2)
                if pos in (1, 3):
                    mx.add("music", t, A.clap(), 0.45)
            if pos == 0 and hot:
                mx.add("music", t, A.pad([A.note(n) for n in chord], BEAT * 4), 1.0)
            if max_:
                for k in range(4):
                    n = chord[(beat_i * 4 + k) % 3] + 12
                    mx.add("music", t + k * BEAT / 4, A.pluck(A.note(n), 0.18), 0.12, pan=0.3 * (-1) ** k)
        t += BEAT
        beat_i += 1

    # Slow-mo: silenzio musicale, battito e riser fino al colpo finale.
    hb = t_slow
    while hb < t_win - 0.3:
        mx.add("sfx", hb, A.heartbeat(), 0.8)
        hb += 0.62
    mx.add("sfx", max(t_slow, t_win - 1.6), A.riser(min(1.6, t_win - t_slow)), 0.55)

    # ---------- SFX ----------
    mx.add("sfx", 0.0, A.boom(), 0.7)
    mx.add("sfx", 0.0, A.crash(), 0.5)

    last = -1.0
    for c in rec.conversions:
        t0, x, y, wt, lt, ball = c
        if t0 > rec.t_end:
            break
        vt = tl.vt(t0)
        if vt - last < 0.035:
            continue
        last = vt
        pan = (x / W * 2 - 1) * 0.6
        mx.add("sfx", vt, A.pluck(A.note(PENTA[int(wt) % len(PENTA)] - 12 + 12 * (int(wt) >= 6))), 0.22, pan)

    last = -1.0
    for e in rec.escapes:
        vt = tl.vt(e[0])
        if e[0] > rec.t_end or vt - last < 0.06:
            continue
        last = vt
        mx.add("sfx", vt, A.whoosh(), 0.35, (e[3] / W * 2 - 1) * 0.7)

    for et, team, x, y in rec.eliminations:
        if et >= rec.t_end:
            continue
        vt = tl.vt(et)
        mx.add("sfx", vt, A.zap(), 0.4)
        mx.add("sfx", vt, A.kick(), 0.5)

    for v0, kind, label, extra in tl.banners:
        mx.add("sfx", max(0.0, v0 - 0.8), A.riser(0.8), 0.35)
        mx.add("sfx", v0, A.boom(), 0.75)
        mx.add("sfx", v0, A.crash(), 0.45)

    # Vittoria: impatto enorme + accordo maggiore + arpeggio.
    mx.add("sfx", t_win, A.boom(2.0), 1.0)
    mx.add("sfx", t_win, A.crash(2.4), 0.7)
    mx.add("sfx", t_win + 0.05, A.pad([A.note(n) for n in (57, 61, 64, 69)], 3.0), 3.0)
    for k, n in enumerate([69, 73, 76, 81, 85, 88]):
        mx.add("sfx", t_win + 0.3 + k * 0.07, A.pluck(A.note(n), 0.5), 0.2, pan=0.4 * np.sin(k))

    return mx.master()
