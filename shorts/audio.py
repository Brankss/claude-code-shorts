"""Audio procedurale morbido: pad ambient, note tipo kalimba, campane, mix e master."""

import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
_rng = np.random.default_rng(1234)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def note(n):
    """Frequenza di una nota MIDI."""
    return 440.0 * 2 ** ((n - 69) / 12)


# ---------- sintetizzatori ----------

def kalimba(freq, d=1.3):
    """Nota pizzicata morbida: fondamentale lunga, armonica acuta che sparisce subito."""
    t = _t(d)
    x = np.sin(2 * np.pi * freq * t) * np.exp(-t * 4.5)
    x += 0.25 * np.sin(2 * np.pi * freq * 3.02 * t) * np.exp(-t * 22)
    return x * np.minimum(1, t / 0.004)


def bell(freq, d=3.0):
    """Campana dolce (parziali inarmoniche con decadimenti diversi)."""
    t = _t(d)
    x = np.zeros_like(t)
    for ratio, amp, dec in ((1.0, 1.0, 1.4), (2.0, 0.35, 2.2), (2.76, 0.18, 3.5), (5.4, 0.06, 6.0)):
        x += amp * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t * dec)
    return 0.6 * x * np.minimum(1, t / 0.006)


def tock(freq=190.0):
    """Colpetto legnoso, corto."""
    t = _t(0.18)
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 32) * np.minimum(1, t / 0.002)


def pad(freqs, d, attack=1.2, release=1.6, cutoff=900):
    """Accordo tenuto, filtrato, con attacco e rilascio lenti."""
    t = _t(d + release)
    x = np.zeros_like(t)
    for fr in freqs:
        for det in (-0.08, 0.08):
            ph = 2 * np.pi * fr * (1 + det / 100) * t
            x += np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)
    x = _filt(x, "low", cutoff)
    env = np.minimum(1, t / attack) * np.clip((d + release - t) / release, 0, 1)
    return x * env / (2 * len(freqs))


# ---------- mixer ----------

class Mixer:
    def __init__(self, duration):
        self.n = int(duration * SR)
        self.dry = np.zeros((self.n + SR * 6, 2))
        self.send = np.zeros_like(self.dry)

    def add(self, t, sig, gain=1.0, pan=0.0, reverb=0.3):
        i = int(t * SR)
        if i >= self.n or i < 0:
            return
        sig = sig[: len(self.dry) - i] * gain
        a = (pan + 1) * np.pi / 4
        st = np.stack([sig * np.cos(a), sig * np.sin(a)], 1)
        self.dry[i:i + len(sig)] += st
        self.send[i:i + len(sig)] += st * reverb

    def master(self, loop_tail=True):
        ir_t = _t(3.2)
        ir = np.stack([_rng.normal(0, 1, len(ir_t)), _rng.normal(0, 1, len(ir_t))], 1)
        ir *= np.exp(-ir_t * 2.2)[:, None]
        ir[:, 0] = _filt(ir[:, 0], "low", 5000)
        ir[:, 1] = _filt(ir[:, 1], "low", 5000)
        ir /= np.sqrt((ir ** 2).sum(0))
        wet = np.stack([fftconvolve(self.send[:, ch], ir[:, ch])[: len(self.send)] for ch in (0, 1)], 1)
        out = self.dry + wet
        if loop_tail:
            # La coda che sfora la fine rientra all'inizio: il loop non ha tagli.
            tail = out[self.n:]
            out = out[: self.n].copy()
            m = min(len(tail), self.n)
            out[:m] += tail[:m]
        else:
            out = out[: self.n]
        out /= max(1e-9, np.abs(out).max()) / 0.84
        return out


def write_wav(path, audio):
    data = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
