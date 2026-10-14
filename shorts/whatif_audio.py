"""Audio di What If: niente voce, solo sound design legato a quello che succede a schermo.

- strada: rombo del traffico, clacson (quelli veri della simulazione), freccia dell'eroe
- escalation: pad che cresce mentre lo zoom esce, una campana più acuta a ogni salto di tempo
- spazio: bordone sottile e luminoso
- movimenti di camera: whoosh; didascalie a macchina da scrivere: ticchettio leggero
- rewind: nastro che riavvolge; twist e ultima frase: colpo basso
Il loop è senza stacchi: l'ambiente che sfora la fine rientra in dissolvenza all'inizio.
"""

import math

import numpy as np
from scipy.signal import butter, sosfilt

from . import audio as A
from .whatif import CPS

SR = A.SR


def _bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def _lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def _hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


def _sweep_lp(x, f0, f1):
    """Passa-basso a un polo con taglio che scorre (esponenziale) da f0 a f1."""
    n = len(x)
    fc = f0 * (f1 / f0) ** (np.arange(n) / max(1, n - 1))
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def whoosh(d, rng, up=True):
    n = int(d * SR)
    t = np.arange(n) / n
    x = _sweep_lp(rng.normal(0, 1, n), 250 if up else 3500, 3500 if up else 250)
    return x * np.sin(np.pi * t) ** 2 * 1.6


def horn(d=0.32, f=410.0):
    """Clacson: due note stonate ricche di armoniche, filtrate."""
    t = np.arange(int(d * SR)) / SR
    x = np.zeros_like(t)
    for fr in (f, f * 1.26):
        for k in range(1, 7):
            x += np.sin(2 * np.pi * fr * k * t) / k
    x = _bp(x, 300, 2800)
    env = np.minimum(1, t / 0.012) * np.clip((d - t) / 0.05, 0, 1)
    return x * env / 3


def click(f=2200.0, d=0.012):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 500)


def tick(rng):
    x = _hp(rng.normal(0, 1, int(0.006 * SR)), 2500)
    return x * np.exp(-np.arange(len(x)) / SR * 700)


def boom(d=1.6):
    t = np.arange(int(d * SR)) / SR
    f = 44 + 40 * np.exp(-t * 9)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.8)
    return x * np.minimum(1, t / 0.004)


def rewind(d, rng):
    """Nastro che riavvolge: tono che sale veloce e trilla, più fruscio."""
    n = int(d * SR)
    t = np.arange(n) / SR
    k = t / d
    f = 180 + 2600 * k ** 1.5 * (0.75 + 0.25 * np.sin(2 * np.pi * 11 * t))
    x = 0.5 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR))
    x = _bp(x, 200, 5000) + 0.5 * _hp(rng.normal(0, 1, n), 1500)
    env = np.minimum(1, t / 0.08) * np.clip((d - t) / 0.12, 0, 1)
    return x * env * 0.5


def _env(ts, vals, n):
    return np.interp(np.arange(n) / SR, ts, vals)


def build(r):
    st, tl = r.story, r.tl
    D = st.duration
    n = int(D * SR)
    mx = A.Mixer(D)
    rng = np.random.default_rng(5)

    # Inviluppi di ambiente dalla camera (50 al secondo).
    ts = np.arange(0, D + 0.02, 0.02)
    road, mid, space = np.zeros(len(ts)), np.zeros(len(ts)), np.zeros(len(ts))
    for i, vt in enumerate(ts):
        cam = tl.camera(min(vt, D - 1e-3))
        lw = math.log10(cam.w)
        _, _, where = tl.scene_state(vt)
        road[i] = np.clip(1 - (lw - 2.2) / 1.6, 0, 1) * (where == "earth")
        space[i] = max(float(np.clip((lw - 7.2) / 1.0, 0, 1)), 0.8 * (where == "moon"))
        mid[i] = np.clip((lw - 2.6) / 1.2, 0, 1) * (1 - space[i])

    # Rombo del traffico: rumore marrone filtrato + fruscio di gomme, un secondo in più per il loop.
    m = n + SR
    brown = np.cumsum(rng.normal(0, 1, m))
    brown = _hp(brown, 25)
    brown /= np.abs(brown).max()
    amb = _lp(brown, 380) * 1.4 + 0.10 * _bp(rng.normal(0, 1, m), 700, 2600)
    amb *= 1 + 0.25 * np.sin(2 * np.pi * np.arange(m) / SR / 7.3)
    e = np.concatenate([_env(ts, road, n), np.full(SR, road[-1])])
    fade = np.ones(m)
    fade[:SR] = np.linspace(0, 1, SR)
    fade[n:] = np.linspace(1, 0, SR)
    mx.add(0.0, amb * e * fade * 0.55, reverb=0.05)

    # Pad dell'escalation e bordone dello spazio (stessa tonalità: Re minore).
    pad = A.pad([A.note(50), A.note(57), A.note(62), A.note(65)], D, attack=0.01, release=0.01, cutoff=1100)[:n]
    mx.add(0.0, pad * _env(ts, mid, len(pad)) * 0.9, reverb=0.35)
    t = np.arange(n) / SR
    drone = sum(np.sin(2 * np.pi * A.note(n0) * t + ph) * g
                for n0, g, ph in ((74, 0.5, 0), (81, 0.3, 1.3), (86, 0.18, 2.1), (93, 0.08, 0.7)))
    drone *= 0.75 + 0.25 * np.sin(2 * np.pi * t / 5.0)
    mx.add(0.0, drone * _env(ts, space, n) * 0.22, reverb=0.6)

    # Campane: una a ogni salto di tempo, ogni volta più acuta.
    steps = [62, 65, 69, 72, 74, 77, 81]
    k = 0
    for b in tl.beats:
        if b.jump:
            mx.add(b.at + 0.15, A.bell(A.note(steps[min(k, len(steps) - 1)]), 3.0), 0.45, pan=0.2 * (-1) ** k,
                   reverb=0.55)
            k += 1

    # Whoosh sui grandi movimenti di camera.
    prev_w = None
    for t0, spec, mv in tl.cam:
        w = spec["w"]
        if prev_w is not None and abs(math.log10(w / prev_w)) > 0.7:
            mx.add(t0, whoosh(mv, rng, up=w > prev_w), 0.22 * min(1.0, abs(math.log10(w / prev_w)) / 3), reverb=0.3)
        prev_w = w

    # Macchina da scrivere: didascalie a sinistra, salti di tempo e seconda metrica.
    for cap in tl.captions:
        if cap["layout"] == "left":
            for i, ch in enumerate(cap["text"]):
                if ch != " " and i % 2 == 0:
                    mx.add(cap["t0"] + 0.25 + i / CPS, tick(rng), 0.05, pan=-0.3, reverb=0.05)
    for t0, val in tl.kpi2:
        if val:
            for i in range(0, len(val[0]) + len(val[1]), 2):
                mx.add(t0 + i / (CPS * 1.4), tick(rng), 0.035, pan=0.4, reverb=0.05)

    # Clacson e freccia, presi dalla simulazione mentre la strada è in vista.
    scene = r.scene
    last = None
    for i, vt in enumerate(ts[:-1]):
        rec, ts_sim, where = tl.scene_state(vt)
        if road[i] < 0.3 or where != "earth":
            last = None
            continue
        if last is not None and last[0] == rec and 0 < ts_sim - last[1] < 0.1:
            for ht, _ in scene.recs[rec].honks:
                if last[1] < ht <= ts_sim:
                    mx.add(vt, horn(rng.uniform(0.18, 0.4), rng.uniform(370, 450)), 0.32 * road[i],
                           pan=rng.uniform(0.1, 0.5), reverb=0.12)
            sw = scene.switch_sim
            if rec == "A" and sw is not None:
                for j in range(12):
                    tk = sw - 0.3 + j / 4.8
                    if last[1] < tk <= ts_sim and tk < sw + 3.8:
                        mx.add(vt, click(2400 if j % 2 == 0 else 1700), 0.12, pan=0.1, reverb=0.02)
        last = (rec, ts_sim)

    # Rewind e colpi.
    for t0, kind, d in tl.fx:
        if kind == "rewind":
            mx.add(t0, rewind(d, rng), 0.35, reverb=0.25)
        elif kind == "hit":
            mx.add(t0, boom(), 0.7, reverb=0.3)
    return mx.master()
