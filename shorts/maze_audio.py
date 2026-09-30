"""Colonna sonora del Labirinto: ogni colore è una voce che suona mentre avanza."""

import numpy as np

from . import audio as A
from .base import TOTAL
from .maze import CELL, X0
from .maze_render import VT_WIN

# Re maggiore ambient: Dmaj9, Bm9, Gmaj7, A6sus (4s ciascuno).
CHORDS = [[50, 57, 62, 66, 69, 76], [47, 54, 59, 62, 66, 73], [43, 55, 59, 62, 66, 71], [45, 57, 62, 64, 69, 71]]
PENTA = [62, 64, 66, 69, 71]                       # Re pentatonica maggiore
VOICES = [(0, 12), (2, 12), (1, 24), (3, 24)]      # grado di partenza e ottava per ogni colore
EVERY = 4                                          # una nota ogni N celle occupate


def build(tl):
    m = tl.m
    mx = A.Mixer(TOTAL)
    t, i = 0.0, 0
    while t < VT_WIN + 0.5:
        mx.add(t, A.pad([A.note(n) for n in CHORDS[i % 4]], 4.0), 0.5, reverb=0.25)
        t += 4.0
        i += 1
    mx.add(VT_WIN, A.pad([A.note(n) for n in (50, 57, 62, 66, 69, 74)], TOTAL - VT_WIN - 0.5,
                         attack=0.8, cutoff=1300), 0.6, reverb=0.3)

    # Ogni colore suona un arpeggio che avanza con lui.
    count = [0] * len(tl.teams)
    last = [-1.0] * len(tl.teams)
    for a, r, c in tl.cells:
        team = int(m.owner[r, c])
        count[team] += 1
        vt = a * tl.scale
        if count[team] % EVERY or vt - last[team] < 0.22:
            continue
        last[team] = vt
        start, octave = VOICES[team]
        step = count[team] // EVERY
        n = PENTA[(start + step * 2) % 5] + octave - 12 + 12 * ((start + step * 2) // 5 % 2)
        pan = ((X0 + c * CELL) / 1080 * 2 - 1) * 0.6
        mx.add(vt, A.kalimba(A.note(n)), 0.13, pan=pan, reverb=0.45)

    for vt, team, what in tl.news:
        if team is None:
            mx.add(vt, A.bell(A.note(78), 2.0), 0.12, pan=-0.2, reverb=0.6)
            mx.add(vt + 0.14, A.bell(A.note(83), 2.0), 0.12, pan=0.2, reverb=0.6)
        else:
            mx.add(vt, A.bell(A.note(38 + [0, 4, 7, 9][team])), 0.3, reverb=0.5)

    # Vittoria: campane e una scala che sale lungo il percorso.
    for k, n in enumerate((50, 54, 57, 62, 66, 69)):
        mx.add(VT_WIN + 0.05 + k * 0.13, A.bell(A.note(n), 3.5), 0.26, pan=0.3 * (-1) ** k, reverb=0.55)
    steps = np.linspace(0, 1.8, 10)
    for k, s in enumerate(steps):
        n = PENTA[k % 5] + 12 * (1 + k // 5)
        mx.add(VT_WIN + 0.3 + s, A.kalimba(A.note(n)), 0.1, pan=0.4 * np.sin(k), reverb=0.5)
    return mx.master()
