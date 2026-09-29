"""Audio procedurale: beat, SFX sincronizzati agli eventi, mix e master."""

import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
_rng = np.random.default_rng(1234)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(d, attack=0.003, decay=8.0):
    t = _t(d)
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t * decay)


def _filt(x, kind, f, order=2):
    sos = butter(order, f, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x)


def note(n):
    """Frequenza di una nota MIDI."""
    return 440.0 * 2 ** ((n - 69) / 12)


# ---------- sintetizzatori ----------

def kick(d=0.42):
    t = _t(d)
    f = 48 + 120 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh(1.6 * np.sin(ph) * np.exp(-t * 7.5)) + 0.3 * _filt(_rng.normal(0, 1, len(t)), "high", 2000) * np.exp(-t * 180)


def hat(d=0.06, open_=False):
    t = _t(0.22 if open_ else d)
    n = _filt(_rng.normal(0, 1, len(t)), "high", 7000)
    return 0.5 * n * np.exp(-t * (14 if open_ else 70))


def clap(d=0.25):
    t = _t(d)
    n = _filt(_rng.normal(0, 1, len(t)), "band", [900, 2600])
    e = np.exp(-t * 22)
    for off in (0.0, 0.012, 0.024):
        e += 0.6 * np.exp(-np.maximum(0, t - off) * 150) * (t >= off)
    return 0.7 * n * e


def bass(freq, d):
    t = _t(d)
    x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t) + 0.15 * np.sin(6 * np.pi * freq * t)
    return np.tanh(1.4 * x) * _env(d, 0.004, 5.0) * 0.8


def pluck(freq, d=0.3):
    t = _t(d)
    x = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(4 * np.pi * freq * t) * np.exp(-t * 20) \
        + 0.2 * np.sin(6 * np.pi * freq * t) * np.exp(-t * 30)
    return x * _env(d, 0.002, 14.0)


def pad(freqs, d):
    t = _t(d)
    x = np.zeros_like(t)
    for fr in freqs:
        for det in (-0.12, 0.12):
            ph = 2 * np.pi * fr * (1 + det / 100) * t
            x += 2 / np.pi * np.arctan(np.tan(ph / 2))  # dente di sega
    x = _filt(x, "low", 1400)
    env = np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.2)
    return 0.12 * x * env / len(freqs)


def boom(d=1.4):
    t = _t(d)
    f = 34 + 90 * np.exp(-t * 14)
    ph = 2 * np.pi * np.cumsum(f) / SR
    low = np.sin(ph) * np.exp(-t * 3.2)
    noise = _filt(_rng.normal(0, 1, len(t)), "low", 1800) * np.exp(-t * 6)
    return np.tanh(1.8 * low + 0.5 * noise)


def crash(d=1.8):
    t = _t(d)
    return 0.35 * _filt(_rng.normal(0, 1, len(t)), "high", 4500) * np.exp(-t * 2.6)


def riser(d=0.9):
    t = _t(d)
    n = _rng.normal(0, 1, len(t))
    out = np.zeros_like(t)
    seg = 8
    for i in range(seg):
        a, b = i * len(t) // seg, (i + 1) * len(t) // seg
        out[a:b] = _filt(n[a:b], "band", [400 + 700 * i, 1400 + 1400 * i])
    f = 180 * 2 ** (3 * t / d)
    tone = 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR)
    return (0.6 * out + tone) * (t / d) ** 2


def zap(d=0.45):
    t = _t(d)
    f = 900 * np.exp(-t * 7) + 60
    ph = 2 * np.pi * np.cumsum(f) / SR
    return 0.7 * np.tanh(2 * np.sin(ph)) * np.exp(-t * 5)


def whoosh(d=0.35):
    t = _t(d)
    n = _rng.normal(0, 1, len(t))
    x = _filt(n, "band", [500, 3000]) * np.sin(np.pi * t / d) ** 2
    return 0.5 * x


def heartbeat():
    t = _t(0.5)
    one = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 18)
    out = one.copy()
    shift = int(0.16 * SR)
    out[shift:] += 0.7 * one[:-shift]
    return out


# ---------- mixer ----------

class Mixer:
    def __init__(self, duration):
        self.n = int(duration * SR)
        self.music = np.zeros((self.n + SR * 3, 2))
        self.sfx = np.zeros_like(self.music)
        self.duck = np.ones(self.n + SR * 3)

    def add(self, bus, t, sig, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i >= self.n or i < 0:
            return
        sig = sig[: len(self.music) - i] * gain
        a = (pan + 1) * np.pi / 4
        buf = self.music if bus == "music" else self.sfx
        buf[i:i + len(sig), 0] += sig * np.cos(a)
        buf[i:i + len(sig), 1] += sig * np.sin(a)

    def sidechain(self, t, depth=0.55, d=0.22):
        i = int(t * SR)
        tt = _t(d)
        env = 1 - depth * np.exp(-tt * 14)
        seg = self.duck[i:i + len(env)]
        self.duck[i:i + len(env)] = np.minimum(seg, env[: len(seg)])

    def master(self):
        music = self.music * self.duck[:, None]
        ir_t = _t(1.3)
        ir = np.stack([_rng.normal(0, 1, len(ir_t)), _rng.normal(0, 1, len(ir_t))], 1) * np.exp(-ir_t * 4.5)[:, None]
        ir /= np.sqrt((ir ** 2).sum(0))
        wet = np.stack([fftconvolve(self.sfx[:, ch], ir[:, ch])[: len(self.sfx)] for ch in (0, 1)], 1)
        out = 0.9 * music + self.sfx + 0.22 * wet
        out = out[: self.n]
        out = np.tanh(out * 1.1)
        out /= max(1e-9, np.abs(out).max()) / 0.89
        fade = int(0.02 * SR)
        out[:fade] *= np.linspace(0, 1, fade)[:, None]
        out[-fade:] *= np.linspace(1, 0, fade)[:, None]
        return out


def write_wav(path, audio):
    data = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
