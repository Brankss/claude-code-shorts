"""Audio del format "rules": voce, tappeto horror che segue la tensione, effetti e colpi sulle card.

Tutto procedurale tranne la voce (Kokoro, vedi voice.py). La musica si abbassa quando qualcuno parla
(ducking) così la voce resta sempre davanti, come nei video di riferimento.
"""

import numpy as np
from scipy.signal import butter, resample_poly, sosfilt

from . import audio as A
from . import voice
from . import whatif_audio as WA
from .rules import at_time

SR = A.SR


def _t(d):
    return np.arange(int(d * SR)) / SR


def _f(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def _place(out, sig, j):
    """Somma sig in out a partire dal campione j, tagliando quello che esce dai bordi."""
    j = max(0, int(j))
    n = min(len(sig), len(out) - j)
    if n > 0:
        out[j:j + n] += sig[:n]


# ---------- effetti ----------

def buzz(d=1.6, rng=None):
    """Telefono che vibra sul comodino: ronzio a impulsi."""
    t = _t(d)
    tone = np.sign(np.sin(2 * np.pi * 172 * t)) * 0.5 + np.sin(2 * np.pi * 344 * t) * 0.3
    gate = ((t % 0.62) < 0.38).astype(float)
    gate = _f(gate, "low", 60)
    return _f(tone * gate, "band", [120, 1800]) * 0.8


def alert(d=2.6):
    """Allarme del telefono, inventato: due note stridenti e stonate a raffiche brevi. Non è il segnale
    d'attenzione delle allerte reali (853+960 Hz), che fuori da un'emergenza vera non si può usare."""
    t = _t(d)
    x = np.sign(np.sin(2 * np.pi * 698 * t)) * 0.5 + np.sign(np.sin(2 * np.pi * 1046 * t + 0.3)) * 0.35
    x += 0.4 * np.sin(2 * np.pi * 1397 * t)
    pat = (((t % 0.5) < 0.18) | (((t % 0.5) > 0.24) & ((t % 0.5) < 0.38))).astype(float)
    pat = _f(pat, "low", 150)
    return 0.3 * _f(x, "band", [400, 4000]) * pat


def knock(n=3, gap=0.32, hard=1.0, rng=None):
    rng = rng or np.random.default_rng(3)
    out = np.zeros(int((n * gap + 0.6) * SR))
    for i in range(n):
        t = _t(0.35)
        th = np.sin(2 * np.pi * (85 + 30 * np.exp(-t * 40)) * t) * np.exp(-t * 22)
        wood = _f(rng.normal(0, 1, len(t)), "band", [500, 2600]) * np.exp(-t * 70) * 0.6
        hit = (th + wood) * (0.85 + 0.3 * rng.random()) * hard
        _place(out, hit, (i * gap + rng.uniform(0.0, 0.03)) * SR)
    return out


def siren(d=6.0, f0=620, f1=1240, period=3.2):
    """Sirena lontana."""
    t = _t(d)
    f = f0 + (f1 - f0) * (0.5 - 0.5 * np.cos(2 * np.pi * t / period))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.3 * np.sin(2 * ph)
    x = _f(x, "low", 1600)
    env = np.minimum(1, t / 1.0) * np.minimum(1, (d - t) / 1.0)
    return 0.35 * x * env


def power_down(d=1.8):
    """Blackout: il ronzio della corrente scende e muore, scatto finale."""
    t = _t(d)
    f = 120 * np.exp(-t * 2.4) + 18
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 1.2) + 0.4 * np.sin(2 * ph) * np.exp(-t * 2)
    x[: int(0.01 * SR)] += np.linspace(1, 0, int(0.01 * SR))
    return 0.7 * x


def heartbeat(n=4, bpm=72):
    out = np.zeros(int((n * 60 / bpm + 0.5) * SR))
    for i in range(n):
        for off, g in ((0.0, 1.0), (0.22, 0.7)):
            t = _t(0.25)
            th = np.sin(2 * np.pi * (48 + 20 * np.exp(-t * 30)) * t) * np.exp(-t * 18) * g
            _place(out, th, (i * 60 / bpm + off) * SR)
    return out


def glitch(d=0.6, rng=None):
    rng = rng or np.random.default_rng(9)
    x = np.zeros(int(d * SR))
    i = 0
    while i < len(x):
        n = int(rng.uniform(0.015, 0.07) * SR)
        kind = rng.integers(3)
        t = np.arange(n) / SR
        if kind == 0:
            seg = rng.normal(0, 0.6, n)
        elif kind == 1:
            seg = np.sign(np.sin(2 * np.pi * rng.uniform(200, 1800) * t)) * 0.4
        else:
            seg = np.zeros(n)
        x[i:i + n] = seg[: len(x) - i]
        i += n
    return np.round(x * 6) / 6


def chime():
    """Ding-dong da altoparlante."""
    out = np.zeros(int(1.9 * SR))
    for off, n in ((0.0, 76), (0.45, 72)):
        _place(out, A.bell(A.note(n), 1.4), off * SR)
    return speaker(out) * 1.4


def speaker(x):
    """Altoparlante d'ambiente: banda telefonica, un filo di distorsione."""
    y = _f(x, "band", [320, 3400], order=3)
    return np.tanh(y * 2.2) / 2.2


def hum(d, f=120.0):
    """Ronzio di neon."""
    t = _t(d)
    x = sum(np.sin(2 * np.pi * f * k * t) / k for k in (1, 2, 3, 5))
    return 0.15 * x * (1 + 0.1 * np.sin(2 * np.pi * 0.3 * t))


def noise_bed(d, lo, hi, rng, am=0.0, rate=0.2):
    t = _t(d)
    x = _f(rng.normal(0, 1, len(t)), "band", [lo, hi])
    if am:
        x *= 1 + am * np.sin(2 * np.pi * rate * t + rng.uniform(0, 6))
    return x / (np.abs(x).max() + 1e-9)


def drag(d=1.2, rng=None):
    """Mobile trascinato sul pavimento."""
    rng = rng or np.random.default_rng(4)
    t = _t(d)
    x = _f(rng.normal(0, 1, len(t)), "band", [180, 1400])
    jit = _f(rng.random(len(t)), "low", 18)
    return 0.8 * x * (0.4 + jit) * np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.15)


def creak(d=1.4):
    t = _t(d)
    f = 90 + 70 * np.sin(2 * np.pi * 0.6 * t) ** 2
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (ph / (2 * np.pi) % 1.0) * 2 - 1
    x = _f(x, "band", [600, 1600], order=3)
    return 0.6 * x * np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.2)


def thud(d=1.2):
    return WA.boom(d) * 0.8


def footsteps(n=6, gap=0.5, rng=None):
    rng = rng or np.random.default_rng(6)
    out = np.zeros(int((n * gap + 0.4) * SR))
    for i in range(n):
        t = _t(0.2)
        s = _f(rng.normal(0, 1, len(t)), "low", 500) * np.exp(-t * 35)
        _place(out, s * (0.7 + 0.3 * rng.random()), i * gap * SR)
    return out


def scrape(d=2.0, rng=None):
    """Qualcosa che striscia: graffi lenti."""
    rng = rng or np.random.default_rng(7)
    t = _t(d)
    x = _f(rng.normal(0, 1, len(t)), "band", [900, 4000])
    g = (np.sin(2 * np.pi * 1.3 * t) > 0.3).astype(float)
    return 0.5 * x * _f(g, "low", 25) * np.minimum(1, t / 0.3)


def tap(hard=1.0, rng=None):
    """Colpo di nocca sul vetro: tintinnio acuto più il tonfo del telaio."""
    rng = rng or np.random.default_rng(13)
    t = _t(0.4)
    ting = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((2350, 38), (3710, 55), (5200, 70)))
    body = np.sin(2 * np.pi * 160 * t) * np.exp(-t * 30)
    click = _f(rng.normal(0, 1, len(t)), "high", 3000) * np.exp(-t * 400)
    return (0.25 * ting + 0.7 * body + 0.4 * click) * hard


def text_ping():
    """Messaggio arrivato: due note brevi e luminose."""
    out = np.zeros(int(0.5 * SR))
    for off, n in ((0.0, 88), (0.09, 93)):
        t = _t(0.3)
        _place(out, np.sin(2 * np.pi * A.note(n) * t) * np.exp(-t * 18) * 0.5, off * SR)
    return out


def unplug():
    """Spina staccata: un tonfo sordo e lo scatto della plastica."""
    t = _t(0.25)
    x = np.sin(2 * np.pi * 90 * t) * np.exp(-t * 40)
    _place(x, WA.click(1800, 0.015) * 0.5, 0)
    return x


def tape(rng=None):
    """Nastro adesivo strappato dal rotolo."""
    rng = rng or np.random.default_rng(16)
    t = _t(0.7)
    x = _f(rng.normal(0, 1, len(t)), "band", [1500, 7000]) * (rng.random(len(t)) > 0.6)
    return 0.6 * x * np.minimum(1, t / 0.05) * np.minimum(1, (0.7 - t) / 0.1)


def static(d=3.0, rng=None):
    rng = rng or np.random.default_rng(17)
    t = _t(d)
    return 0.35 * _f(rng.normal(0, 1, len(t)), "band", [300, 6000]) * np.minimum(1, t / 0.05)


SFX = {
    "tape": lambda rng: tape(rng),
    "static": lambda rng: static(3.0, rng),
    "power_off": lambda rng: np.concatenate([A.bell(A.note(84), 0.25) * 0.5, A.bell(A.note(77), 0.4) * 0.5]),
    "tap": lambda rng: tap(1.0, rng),
    "tap_soft": lambda rng: tap(0.5, rng),
    "tap_hard": lambda rng: tap(1.6, rng),
    "text": lambda rng: text_ping(),
    "unplug": lambda rng: unplug(),
    "fog": lambda rng: noise_bed(6.0, 150, 900, rng, am=0.5, rate=0.15) * 0.5 * np.minimum(1, _t(6.0) / 1.0) *
    np.minimum(1, (6.0 - _t(6.0)) / 1.5),
    "buzz": lambda rng: buzz(1.8),
    "buzz_long": lambda rng: buzz(3.2),
    "alert": lambda rng: alert(2.6),
    "knock": lambda rng: knock(3, rng=rng),
    "knock_hard": lambda rng: knock(4, gap=0.24, hard=1.5, rng=rng),
    "knock_soft": lambda rng: knock(2, gap=0.45, hard=0.5, rng=rng),
    "siren": lambda rng: siren(7.0),
    "power_down": lambda rng: power_down(),
    "heartbeat": lambda rng: heartbeat(5),
    "glitch": lambda rng: glitch(0.7, rng),
    "chime": lambda rng: chime(),
    "boom": lambda rng: WA.boom(2.2),
    "hit": lambda rng: WA.boom(1.4) * 0.8,
    "whoosh": lambda rng: WA.whoosh(0.7, rng, up=True),
    "whoosh_down": lambda rng: WA.whoosh(0.9, rng, up=False),
    "drag": lambda rng: drag(1.3, rng),
    "creak": lambda rng: creak(1.4),
    "thud": lambda rng: thud(),
    "steps": lambda rng: footsteps(6, rng=rng),
    "scrape": lambda rng: scrape(2.4, rng),
    "click": lambda rng: WA.click(1500, 0.02) * 2,
    "tick": lambda rng: WA.tick(rng),
}


# ---------- musica ----------

def music(dur, tension_t, tension_v, rng):
    """Tappeto: bordone grave in re minore, filtro che respira, battito sotto quando sale la tensione,
    cluster dissonante acuto nei momenti peggiori."""
    t = _t(dur)
    n = len(t)
    ten = np.interp(t, tension_t, tension_v)
    ten = _f(ten, "low", 0.6, order=1)
    # bordone
    drone = np.zeros(n)
    for fr, g in ((A.note(38), 1.0), (A.note(45), 0.55), (A.note(50), 0.35), (A.note(53), 0.22)):
        for det in (-0.12, 0.13):
            ph = 2 * np.pi * fr * (1 + det / 100) * t
            drone += g * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * t / 9.0)
    drone = _f(drone, "low", 420) * (0.55 + 0.25 * lfo) + _f(drone, "band", [400, 1400]) * 0.25 * ten
    # dissonanza acuta (seconda minore) che entra con la tensione
    cl = sum(np.sin(2 * np.pi * A.note(m) * t + i) for i, m in enumerate((74, 75, 81)))
    cl *= (0.5 + 0.5 * np.sin(2 * np.pi * t / 5.3)) * np.clip((ten - 0.45) / 0.55, 0, 1) ** 1.5
    # battito
    pulse = np.zeros(n)
    bpm = 64
    for i in range(int(dur * bpm / 60)):
        t0 = i * 60 / bpm
        k = int(t0 * SR)
        g = float(np.clip((np.interp(t0, tension_t, tension_v) - 0.35) / 0.65, 0, 1))
        if g <= 0:
            continue
        for off, gg in ((0.0, 1.0), (0.24, 0.6)):
            tt = _t(0.3)
            th = np.sin(2 * np.pi * (44 + 16 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14) * g * gg
            _place(pulse, th, k + off * SR)
    air = noise_bed(dur, 2500, 7000, rng, am=0.6, rate=0.07) * 0.05
    # sub: re grave sotto tutto, quello che "si sente nello stomaco" nei video di riferimento
    sub = np.sin(2 * np.pi * A.note(26) * t) * (0.6 + 0.4 * ten) * (0.8 + 0.2 * np.sin(2 * np.pi * t / 7.0))
    x = drone / 6.0 + cl * 0.025 + pulse * 0.55 + air * (0.4 + ten) + sub * 0.22
    return x * np.minimum(1, t / 1.5)


def limit(x, target_db=-16.5, ceiling=0.94):
    """Porta il volume medio a target_db e limita i picchi senza tagliarli: la gain scende subito
    (con 2-3 ms di anticipo) e risale piano (~120 ms)."""
    y = x * 10 ** ((target_db - 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)) / 20)
    return _peaks(y, ceiling)


def _peaks(y, ceiling):
    from scipy.ndimage import maximum_filter1d, minimum_filter1d
    mono = np.abs(y).max(1) if y.ndim > 1 else np.abs(y)
    inst = np.minimum(1.0, ceiling / (maximum_filter1d(mono, int(0.005 * SR)) + 1e-9))
    held = minimum_filter1d(inst, int(0.05 * SR))
    slow = sosfilt(butter(1, 1 / 0.12, "low", fs=SR, output="sos"), held - 1) + 1
    g = np.minimum(inst, slow)
    y = y * (g[:, None] if y.ndim > 1 else g)
    return np.clip(y, -0.99, 0.99)


def lufs(x):
    """Loudness integrata ITU-R BS.1770-4 (LUFS): filtro K, blocchi da 400 ms al 75%, gate assoluto
    a -70 e relativo a -10. I coefficienti del filtro K sono quelli della norma a 48 kHz."""
    assert SR == 48000
    x = x if x.ndim > 1 else x[:, None]
    from scipy.signal import lfilter
    k = lfilter([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621],
                lfilter([1.53512485958697, -2.69169618940638, 1.19839281085285],
                        [1.0, -1.69065929318241, 0.73248077421585], x, axis=0), axis=0)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    p = np.cumsum(np.concatenate([np.zeros((1, k.shape[1])), k ** 2]), axis=0)
    starts = np.arange(0, len(k) - blk + 1, hop)
    z = ((p[starts + blk] - p[starts]) / blk).sum(1)
    loud = -0.691 + 10 * np.log10(z + 1e-20)
    z = z[loud > -70]
    if not len(z):
        return -70.0
    rel = -0.691 + 10 * np.log10(z.mean()) - 10
    z = z[-0.691 + 10 * np.log10(z) > rel]
    return float(-0.691 + 10 * np.log10(z.mean()))


def true_peak(x):
    """Picco vero in dBTP (sovracampionato 4x)."""
    return 20 * np.log10(np.abs(resample_poly(x, 4, 1, axis=0)).max() + 1e-12)


def loudness(x, target=-14.0, tp=-1.0):
    """Master per le piattaforme: -14 LUFS integrati e picchi veri sotto -1 dBTP (il reference è a -14,2)."""
    ceiling = 10 ** ((tp - 0.4) / 20)
    y = x
    for _ in range(6):
        y = _peaks(y * 10 ** ((target - lufs(y)) / 20), ceiling)
        if abs(lufs(y) - target) < 0.15 and true_peak(y) <= tp:
            break
        if true_peak(y) > tp:
            ceiling *= 10 ** (-0.3 / 20)
    return y


def far(x, rng=None):
    """Voce che arriva da fuori, lontana, nella nebbia: niente alti, eco lunga, un po' di ritardo."""
    rng = rng or np.random.default_rng(2)
    y = _f(x, "low", 1800, order=3)
    ir_t = _t(1.6)
    ir = rng.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 3.0)
    ir = _f(ir, "low", 2500)
    wet = np.convolve(y, ir / np.sqrt((ir ** 2).sum()))[: len(y) + int(1.2 * SR)]
    out = np.zeros(len(wet))
    out[: len(y)] += 0.55 * y
    out += 0.6 * wet
    return out / (np.abs(out).max() + 1e-9) * np.abs(x).max() * 0.7


def glass(x):
    """Voce attraverso il vetro: come la porta ma un po' più chiara."""
    y = _f(x, "low", 2400, order=3) + 0.3 * _f(x, "band", [200, 600])
    return y / (np.abs(y).max() + 1e-9) * np.abs(x).max() * 0.85


def _voice_track(tl, story, n):
    v = np.zeros(n)
    for entry in tl.beats:
        for t0, aud, who, filt in entry["takes"]:
            a = aud
            if filt == "door":
                a = voice.through_door(a)
            a = resample_poly(a, SR, voice.SR)
            if filt == "speaker":
                a = speaker(a) * 1.6
            elif filt == "far":
                a = far(a)
            elif filt == "glass":
                a = glass(a)
            _place(v, a, t0 * SR)
    return v


def echo_wrong(tl, text=None):
    """Una battuta del narratore che torna, più lenta e più bassa: qualcosa la sta copiando.
    text = la battuta esatta (Story.end_echo); None = l'ultima detta dal narratore."""
    last = None
    for entry in tl.beats:
        takes = [aud for t0, aud, who, filt in entry["takes"] if who == "narrator"]
        if takes and (text is None or entry["beat"].text.strip() == text.strip()):
            last = np.concatenate(takes)
    if last is None:
        return np.zeros(1)
    a = resample_poly(last, SR, voice.SR)
    a = resample_poly(a, 9, 8)                      # 12% più lenta e più grave
    return speaker(a) * 1.8                         # esce dalla cassa staccata


def echo_word(entry, word):
    """Una parola appena detta dal narratore che torna da fuori, più grave e lontana."""
    for w in entry["words"]:
        if word.lower() in w.text.lower():
            for t0, aud, who, filt in entry["takes"]:
                i0, i1 = int((w.start - t0) * voice.SR), int((w.end - t0 + 0.05) * voice.SR)
                if 0 <= i0 < len(aud) and i1 <= len(aud) + voice.SR:
                    seg = resample_poly(aud[i0:i1], SR, voice.SR)
                    seg = resample_poly(seg, 6, 5)       # più lenta e più grave
                    return far(seg) * 0.8, w.end + 0.35
    return np.zeros(1), 0.0


def build(r):
    story, tl = r.story, r.tl
    D = tl.duration
    n = int(D * SR)
    mx = A.Mixer(D)
    rng = np.random.default_rng(11)

    vo = _voice_track(tl, story, n)
    peak = np.abs(vo).max() + 1e-9
    vo = vo / peak

    # tensione per beat (con valore che resta finché un beat non lo cambia)
    tt, tv, cur = [0.0], [0.25], 0.25
    for e in tl.beats:
        if e["beat"].music is not None:
            tt += [e["t0"], e["t0"] + 1.2]
            tv += [cur, e["beat"].music]
            cur = e["beat"].music
    tt.append(D)
    tv.append(cur)
    mus = music(D + 1, tt, tv, rng)[:n]
    # ducking: la musica scende di ~7 dB sotto la voce
    env = _f(np.abs(vo), "low", 4, order=1)
    env = np.clip(env / (env.max() + 1e-9) * 3, 0, 1)
    mus *= 1 - 0.55 * env
    # Beat.duck: musica ed effetti si abbassano sulle parole che parlano di silenzio (la voce resta)
    duck = np.ones(n)
    for e in tl.beats:
        for at, dur, depth in e["beat"].duck:
            i0 = int((e["t0"] + at_time(e, at)) * SR)
            shape = np.concatenate([np.linspace(1, 0, int(0.06 * SR)), np.zeros(int(dur * SR)),
                                    np.linspace(0, 1, int(0.25 * SR))])
            seg = 1 - depth * (1 - shape)
            j1 = min(n, i0 + len(seg))
            if j1 > i0 >= 0:
                duck[i0:j1] = np.minimum(duck[i0:j1], seg[: j1 - i0])
    mus *= duck
    mx.add(0.0, mus, 0.55, reverb=0.25)
    mx.add(0.0, vo, 1.0, reverb=0.04)

    def ducked(t):
        return float(duck[min(n - 1, max(0, int(t * SR)))])

    # effetti dei beat
    for j, e in enumerate(tl.beats):
        b = e["beat"]
        for item in b.sfx:
            if item[0] == "echo_last" and item[1] == "end":
                # l'eco finisce con il video: è l'ultima cosa che si sente
                sig = echo_wrong(tl, story.end_echo)
                gain = item[2] if len(item) > 2 else 0.6
                mx.add(max(0.0, D - len(sig) / SR - 0.05), sig, gain, pan=0.0, reverb=0.25)
                continue
            name, off = item[0], at_time(e, item[1])     # secondi o "@parola[:end][+x]"
            if name.startswith("say:"):       # voce lontana nella nebbia: "say:voce:testo"
                _, vid, text = name.split(":", 2)
                words, aud = voice.say(text, vid, 0.95)
                sig = far(resample_poly(aud, SR, voice.SR))
                gain = item[2] if len(item) > 2 else 0.35
                pan = item[3] if len(item) > 3 else float(rng.uniform(-0.6, 0.6))
                mx.add(e["t0"] + off, sig, gain * ducked(e["t0"] + off), pan=pan, reverb=0.5)
                continue
            gain = item[2] if len(item) > 2 else 0.5
            pan = item[3] if len(item) > 3 else float(rng.uniform(-0.2, 0.2))
            if name.startswith("echo:"):
                sig, at = echo_word(e, name[5:])
                mx.add(at, sig, gain, pan=0.5, reverb=0.4)
                continue
            sig = echo_wrong(tl, story.end_echo) if name == "echo_last" else SFX[name](rng)
            mx.add(e["t0"] + off, sig, gain * ducked(e["t0"] + off), pan=pan, reverb=0.25)
        card = b.card or {}
        kind = card.get("kind")
        boom = card.get("boom", True)
        at = e["t0"] + card.get("at", 0.0) if not isinstance(card.get("at", 0.0), str) else r.when(j, card["at"])
        if kind == "rule":
            if boom:
                mx.add(at, WA.boom(1.8), 0.5, reverb=0.35)
            mx.add(at, WA.click(900, 0.04), 0.4, reverb=0.2)
            if card.get("reveal") is not None and card.get("reveal_boom", True):
                mx.add(at + card["reveal"], WA.boom(1.4), 0.55, reverb=0.4)
        elif kind == "title" and boom:
            mx.add(at, WA.boom(2.6), 0.6, reverb=0.5)
        elif kind == "question" and boom:
            mx.add(at, WA.boom(2.0), 0.5, reverb=0.4)
        elif kind == "black_reveal" and boom:
            # il colpo più forte dell'episodio, nello stesso fotogramma della seconda riga
            mx.add(r.when(j, card.get("l2_at", 1.0)), WA.boom(2.6), 0.8, reverb=0.5)
        elif kind == "ledger":
            for row in card["rows"]:
                if "to" in row:   # un tick quando il numero si ferma sulla parola
                    mx.add(r.when(j, row.get("at", 0.0)), WA.click(1800, 0.02), 0.35, reverb=0.15)
        if b.cut == "black":
            mx.add(e["t0"], WA.whoosh(0.6, rng, up=False), 0.15, reverb=0.3)
    out = mx.master(loop_tail=False)
    # Beat.mute: silenzio assoluto di tutto il mix (anche il tappeto), con bordi da 15 ms
    gate = np.ones(len(out))
    for e in tl.beats:
        for at, dur in e["beat"].mute:
            i0, i1 = int((e["t0"] + at_time(e, at)) * SR), int((e["t0"] + at_time(e, at) + dur) * SR)
            f = int(0.015 * SR)
            i0, i1 = max(0, i0), min(len(gate), i1)
            if i1 > i0:
                gate[i0:i1] = 0
                gate[max(0, i0 - f):i0] = np.minimum(gate[max(0, i0 - f):i0], np.linspace(1, 0, i0 - max(0, i0 - f)))
                gate[i1:i1 + f] = np.minimum(gate[i1:i1 + f], np.linspace(0, 1, len(gate[i1:i1 + f])))
    out = out * gate[:, None]
    return loudness(out)
