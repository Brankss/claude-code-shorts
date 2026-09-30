"""Colonna sonora di Contagio: calma, sincronizzata con la timeline del video."""

from . import audio as A
from .contagio import W
from .base import TOTAL

# Accordi ambient (4s ciascuno): Am9, Fmaj7, Cmaj7, G6.
CHORDS = [[45, 57, 60, 64, 71], [41, 57, 60, 64, 69], [48, 55, 59, 64, 67], [43, 55, 59, 62, 64]]
CHORD_LEN = 4.0
# La minore pentatonica: una nota per squadra, così ognuna ha la sua "voce".
PENTA = [69, 72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96]


def build(tl):
    rec = tl.rec
    mx = A.Mixer(TOTAL)

    # Pad di sottofondo continuo; dopo la vittoria sale un accordo maggiore.
    t, i = 0.0, 0
    while t < tl.vt_win:
        d = min(CHORD_LEN, tl.vt_win - t + 0.3)
        mx.add(t, A.pad([A.note(n) for n in CHORDS[i % 4]], d), 0.55, reverb=0.25)
        t += CHORD_LEN
        i += 1
    mx.add(tl.vt_win, A.pad([A.note(n) for n in (45, 57, 61, 64, 71)], TOTAL - tl.vt_win - 0.5,
                            attack=0.8, cutoff=1300), 0.6, reverb=0.3)

    # Una nota a ogni conversione (con un minimo di distanza per non impastare).
    last = -1.0
    for t0, x, y, wt, lt, ball in rec.conversions:
        if t0 > rec.t_end:
            break
        vt = tl.vt(t0)
        if vt - last < 0.07:
            continue
        last = vt
        n = PENTA[int(wt) % len(PENTA)] - 12
        mx.add(vt, A.kalimba(A.note(n)), 0.16, pan=(x / W * 2 - 1) * 0.5, reverb=0.45)

    last = -1.0
    for t0, ball, team, x, y in rec.escapes:
        vt = tl.vt(t0)
        if t0 > rec.t_end or vt - last < 0.08:
            continue
        last = vt
        mx.add(vt, A.tock(), 0.22, pan=(x / W * 2 - 1) * 0.6, reverb=0.3)

    for et, team, x, y in rec.eliminations:
        if et < rec.t_end:
            mx.add(tl.vt(et), A.bell(A.note(45 + [0, 3, 5, 7, 10][team % 5])), 0.32, reverb=0.5)

    for v0, _ in tl.captions:
        mx.add(v0, A.bell(A.note(76), 2.0), 0.12, pan=-0.2, reverb=0.6)
        mx.add(v0 + 0.14, A.bell(A.note(81), 2.0), 0.12, pan=0.2, reverb=0.6)

    # Vittoria: arpeggio di campane lento.
    for k, n in enumerate((57, 61, 64, 69, 73, 76)):
        mx.add(tl.vt_win + 0.1 + k * 0.13, A.bell(A.note(n), 3.5), 0.28, pan=0.3 * (-1) ** k, reverb=0.55)

    return mx.master()
