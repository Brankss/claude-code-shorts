"""Effetti di LOW TIDE, tutti procedurali: campana di bronzo, onde, risacca, allarme dell'auto, corsa, scala
di legno, cane, zip, graffi bagnati. Si registrano nella tabella SFX di rules_audio all'import."""

import numpy as np

from . import rules_audio as RA
from . import whatif_audio as WA

SR = RA.SR
_t, _f, _place = RA._t, RA._f, RA._place


def bell(d=5.0, f=262.0):
    """Campana di bronzo grande: parziali da campana (hum, prime, terza minore, quinta, nominale) che
    decadono a velocità diverse, più il colpo del batacchio."""
    t = _t(d)
    x = np.zeros_like(t)
    for ratio, amp, dec in ((0.5, 0.55, 0.45), (1.0, 0.8, 0.8), (1.19, 0.45, 1.1), (1.5, 0.3, 1.4),
                            (2.0, 0.6, 1.2), (2.52, 0.2, 2.0), (3.0, 0.15, 2.6), (4.07, 0.08, 3.5)):
        x += amp * np.sin(2 * np.pi * f * ratio * t + ratio) * np.exp(-t * dec)
    hit = _f(np.random.default_rng(1).normal(0, 1, len(t)), "band", [1500, 6000]) * np.exp(-t * 60) * 0.5
    x = (x + hit) * np.minimum(1, t / 0.003)
    return 0.32 * x


def wave(d=2.2, rng=None):
    """Onda che monta e si rompe: fruscio che sale e poi lo schianto bianco."""
    rng = rng or np.random.default_rng(4)
    t = _t(d)
    n = rng.normal(0, 1, len(t))
    swell = _f(n, "low", 900) * np.minimum(1, t / 0.6) ** 2 * np.exp(-np.maximum(0, t - 0.6) * 2.2)
    crash = _f(n, "band", [600, 6000]) * (t > 0.55) * np.exp(-np.maximum(0, t - 0.55) * 3.2)
    return 0.5 * swell + 0.35 * crash


def drain(d=2.0, rng=None):
    """Il mare che si ritira: risucchio che scende di tono e gorgoglii."""
    rng = rng or np.random.default_rng(5)
    t = _t(d)
    x = WA.whoosh(d, rng, up=False) * 0.6
    for k in range(18):
        at = rng.uniform(0.1, d - 0.2)
        g = _t(0.06)
        f = rng.uniform(300, 900)
        _place(x, np.sin(2 * np.pi * f * (1 + 2 * g) * g) * np.exp(-g * 70) * 0.25, at * SR)
    return x * np.minimum(1, t / 0.2)


def run_steps(n=7, gap=0.17, rng=None):
    return RA.footsteps(n, gap, rng or np.random.default_rng(6)) * 0.9


def run_crowd(d=2.6, rng=None):
    """Tanti che corrono sulla pietra bagnata: passi fitti e casuali, un brontolio sotto."""
    rng = rng or np.random.default_rng(7)
    out = np.zeros(int(d * SR))
    for k in range(60):
        at = rng.uniform(0, d - 0.3)
        g = _t(0.09)
        step = _f(rng.normal(0, 1, len(g)), "band", [120, 1800]) * np.exp(-g * 45)
        _place(out, step * rng.uniform(0.2, 0.6), at * SR)
    t = _t(d)
    rumble = _f(rng.normal(0, 1, len(t)), "low", 160) * 0.3
    env = np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.5)
    return (out + rumble) * env


def car_alarm(d=3.0, rng=None):
    """Allarme dell'auto generico: un "whoop" veloce che sale e scende, poi chirp a raffica."""
    t = _t(d)
    f = 900 + 500 * np.sin(2 * np.pi * 4.0 * t)
    f = np.where((t % 1.5) < 0.9, f, 1300 * ((t * 12) % 1 < 0.5) + 700)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.4 + 0.3 * np.sin(2 * ph)
    x = _f(x, "band", [500, 4000])
    env = np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.1)
    return 0.22 * x * env


def alarm_stop(rng=None):
    """L'allarme che si spegne: un ultimo chirp che cala."""
    t = _t(0.5)
    f = 1300 - 900 * t
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 6)
    return 0.2 * _f(x, "band", [400, 3500])


def water_rush(d=2.4, rng=None):
    rng = rng or np.random.default_rng(8)
    t = _t(d)
    x = _f(rng.normal(0, 1, len(t)), "band", [250, 3200])
    am = 0.7 + 0.3 * np.sin(2 * np.pi * 3.1 * t) * np.sin(2 * np.pi * 0.7 * t)
    return 0.35 * x * am * np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 0.6)


def ladder(rng=None):
    """Scala di corda con i pioli di legno che sbattono: colpi secchi irregolari e lo strofinio della corda."""
    rng = rng or np.random.default_rng(9)
    out = np.zeros(int(1.0 * SR))
    at = 0.0
    for k in range(9):
        at += rng.uniform(0.05, 0.12)
        g = _t(0.12)
        f = rng.uniform(380, 720)
        knock = np.sin(2 * np.pi * f * g) * np.exp(-g * 55) + _f(rng.normal(0, 1, len(g)), "band", [800, 3000]) * np.exp(-g * 90) * 0.4
        _place(out, knock * rng.uniform(0.4, 0.9), at * SR)
    t = _t(1.0)
    rope = _f(rng.normal(0, 1, len(t)), "band", [1500, 5000]) * 0.08 * np.sin(np.pi * t)
    return 0.7 * (out + rope)


def yip(rng=None):
    """Biscuit che comincia ad abbaiare: due guaiti corti che scendono di tono."""
    out = np.zeros(int(0.5 * SR))
    for k, at in enumerate((0.0, 0.2)):
        g = _t(0.13)
        f = 760 - 260 * g / 0.13
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)
        x = x * np.sin(np.pi * g / 0.13) ** 0.5
        _place(out, x * (1.0 if k == 0 else 0.7), at * SR)
    return 0.3 * _f(out, "band", [300, 4000])


def zip_(rng=None):
    """La zip della giacca che sale sul muso: scatti fitti che accelerano."""
    rng = rng or np.random.default_rng(10)
    out = np.zeros(int(0.45 * SR))
    at = 0.0
    gap = 0.03
    while at < 0.38:
        g = _t(0.01)
        _place(out, _f(rng.normal(0, 1, len(g)), "band", [2000, 8000]) * np.exp(-g * 500), at * SR)
        at += gap
        gap *= 0.93
    return 0.5 * out


def water_rise(d=2.2, rng=None):
    rng = rng or np.random.default_rng(11)
    t = _t(d)
    x = _f(rng.normal(0, 1, len(t)), "low", 500) * 0.5
    for k in range(12):
        at = rng.uniform(0, d - 0.2)
        g = _t(0.08)
        _place(x, np.sin(2 * np.pi * rng.uniform(180, 420) * (1 + 3 * g) * g) * np.exp(-g * 50) * 0.3, at * SR)
    return 0.4 * x * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.5)


def gulp(rng=None):
    """L'acqua che si chiude sopra le teste: un tonfo cupo e bolle."""
    rng = rng or np.random.default_rng(12)
    t = _t(1.0)
    x = np.sin(2 * np.pi * (90 + 60 * np.exp(-t * 8)) * t) * np.exp(-t * 5)
    for k in range(8):
        at = rng.uniform(0.05, 0.7)
        g = _t(0.05)
        _place(x, np.sin(2 * np.pi * rng.uniform(250, 600) * (1 + 4 * g) * g) * np.exp(-g * 80) * 0.3, at * SR)
    return 0.5 * _f(x, "low", 1200)


def wet_scrape(rng=None):
    """Graffio bagnato sul legno: unghie che strisciano e uno schiocco d'acqua."""
    rng = rng or np.random.default_rng(13)
    t = _t(0.45)
    x = _f(rng.normal(0, 1, len(t)), "band", [700, 3500]) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * t) ** 2)
    x *= np.sin(np.pi * t / 0.45)
    drip_ = np.sin(2 * np.pi * 520 * (1 + 2 * t) * t) * np.exp(-t * 30) * 0.4
    return 0.45 * (x + drip_)


def drip(rng=None):
    t = _t(0.3)
    return 0.35 * np.sin(2 * np.pi * (900 + 1500 * t) * t) * np.exp(-t * 25)


def beam(rng=None):
    """Il fascio del faro che passa: un soffio d'aria morbido."""
    return WA.whoosh(1.1, rng or np.random.default_rng(14), up=True) * 0.4


def splash(rng=None):
    rng = rng or np.random.default_rng(15)
    t = _t(0.6)
    return 0.4 * _f(rng.normal(0, 1, len(t)), "band", [500, 5000]) * np.exp(-t * 9)


RA.SFX.update({
    "bell": lambda rng: bell(),
    "wave": lambda rng: wave(rng=rng),
    "drain": lambda rng: drain(rng=rng),
    "run_steps": lambda rng: run_steps(rng=rng),
    "run_crowd": lambda rng: run_crowd(rng=rng),
    "car_alarm": lambda rng: car_alarm(),
    "alarm_stop": lambda rng: alarm_stop(),
    "water_rush": lambda rng: water_rush(rng=rng),
    "ladder": lambda rng: ladder(rng),
    "yip": lambda rng: yip(),
    "zip": lambda rng: zip_(rng),
    "water_rise": lambda rng: water_rise(rng=rng),
    "gulp": lambda rng: gulp(rng),
    "wet_scrape": lambda rng: wet_scrape(rng),
    "drip": lambda rng: drip(),
    "beam": lambda rng: beam(rng),
    "splash": lambda rng: splash(rng),
})
