"""Voce narrante locale: Kokoro-82M (Apache-2.0) in ONNX, con i tempi di ogni parola.

I pesi non stanno nel repo (92 MB): al primo uso si scaricano dal registry npm, dove sono pubblicati
così come sono (`kokoro-q8-shards`: il modello quantizzato q8 di onnx-community/Kokoro-82M-v1.0-ONNX in
6 pezzi; `kokoro-local-runtime`: i vettori delle voci). npm è raggiungibile anche dove HuggingFace e
GitHub non lo sono. Ogni tarball è verificato con l'hash sha512 pubblicato dal registry, il modello
ricomposto con lo sha256 dichiarato dal pacchetto.

Al modello aggiungiamo un'uscita "duration" (le durate per fonema che calcola già al suo interno):
così kokoro-onnx restituisce quando inizia e finisce ogni fonema, e da lì ogni parola. Le didascalie
karaoke sono a tempo esatto, senza bisogno di un riconoscitore vocale.

    words, audio = voice.say("Imagine you wake up...", "am_michael*0.6+am_onyx*0.4")
"""

import base64
import hashlib
import io
import json
import os
import re
import tarfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np

SR = 24000
CACHE = Path(os.environ.get("SHORTS_CACHE", Path.home() / ".cache" / "claude-code-shorts"))
KDIR = CACHE / "kokoro"
REGISTRY = "https://registry.npmjs.org"
MODEL_PKG = ("kokoro-q8-shards", "1.0.0")
VOICES_PKG = ("kokoro-local-runtime", "0.1.0")
MODEL_SHA256 = "fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478"
DURATION_NODE = "/encoder/Cast_output_0"   # durate intere per fonema (dopo Round e Clip)
PAUSES = (0.12, 0.04)                      # pausa dopo il punto e dopo la virgola (le pause lunghe le fa "...")


@dataclass
class Word:
    text: str
    start: float   # secondi dall'inizio della battuta
    end: float


# ---------- download e preparazione del modello ----------

def _fetch_tarball(name, version):
    meta = json.load(urllib.request.urlopen(f"{REGISTRY}/{name}/{version}", timeout=60))
    data = urllib.request.urlopen(meta["dist"]["tarball"], timeout=300).read()
    algo, b64 = meta["dist"]["integrity"].split("-", 1)
    if algo != "sha512" or hashlib.sha512(data).digest() != base64.b64decode(b64):
        raise RuntimeError(f"{name}@{version}: hash del tarball non corrisponde")
    return tarfile.open(fileobj=io.BytesIO(data), mode="r:gz")


def ensure_model():
    """Scarica, verifica e prepara modello e voci (una volta sola). Restituisce (modello, voci)."""
    model = KDIR / "kokoro-q8-dur.onnx"
    voices = KDIR / "voices.npz"
    if model.exists() and voices.exists():
        return model, voices
    KDIR.mkdir(parents=True, exist_ok=True)
    import onnx
    from onnx import TensorProto, helper

    tar = _fetch_tarball(*MODEL_PKG)
    parts = sorted((m for m in tar.getmembers() if re.fullmatch(r"package/kokoro-q8\.part\d+\.bin", m.name)),
                   key=lambda m: int(re.search(r"part(\d+)", m.name).group(1)))
    raw = b"".join(tar.extractfile(m).read() for m in parts)
    if hashlib.sha256(raw).hexdigest() != MODEL_SHA256:
        raise RuntimeError("modello Kokoro: sha256 non corrisponde")
    m = onnx.load_from_string(raw)
    m.graph.node.append(helper.make_node("Identity", [DURATION_NODE], ["duration"], name="expose_duration"))
    m.graph.output.append(helper.make_tensor_value_info("duration", TensorProto.INT64, None))
    onnx.save(m, str(model))

    tar = _fetch_tarball(*VOICES_PKG)
    vs = {}
    for mem in tar.getmembers():
        hit = re.fullmatch(r"package/voices/([a-z]{2}_[a-z]+)\.bin", mem.name)
        if hit:
            vs[hit.group(1)] = np.frombuffer(tar.extractfile(mem).read(), dtype=np.float32).reshape(510, 1, 256)
    np.savez(voices, **vs)
    (KDIR / "SOURCE.txt").write_text(
        "Kokoro-82M v1.0 (Apache-2.0, hexgrad), export ONNX q8 di onnx-community, "
        f"da npm {MODEL_PKG[0]}@{MODEL_PKG[1]} e {VOICES_PKG[0]}@{VOICES_PKG[1]}.\n")
    return model, voices


_ENGINE = None


def engine():
    global _ENGINE
    if _ENGINE is None:
        from kokoro_onnx import Kokoro
        model, voices = ensure_model()
        _ENGINE = Kokoro(str(model), str(voices))
    return _ENGINE


def style(spec):
    """'am_michael' oppure una miscela 'am_michael*0.6+am_onyx*0.4' (media pesata dei vettori di stile)."""
    k = engine()
    total, acc = 0.0, None
    for part in spec.split("+"):
        name, _, w = part.partition("*")
        w = float(w) if w else 1.0
        v = k.get_voice_style(name.strip()) * w
        acc = v if acc is None else acc + v
        total += w
    return (acc / total).astype(np.float32)


# ---------- sintesi ----------

def _words(text, timings, n):
    """Tempi delle parole del testo a partire dai tempi dei fonemi (spazi = confini di parola)."""
    groups, cur = [], []
    for t in timings:
        if t.phoneme == " ":
            if cur:
                groups.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        groups.append(cur)
    marks = set(".,!?;:—…\"'()")
    spans = []
    for g in groups:
        voiced = [t for t in g if t.phoneme not in marks] or g
        spans.append((voiced[0].start, voiced[-1].end))
    tokens = text.split()
    if len(spans) == len(tokens):
        return [Word(w, s, e) for w, (s, e) in zip(tokens, spans)]
    # parole e gruppi di fonemi non tornano (numeri, sigle): ripartisco per lunghezza
    t0 = spans[0][0] if spans else 0.0
    t1 = spans[-1][1] if spans else n / SR
    lens = np.array([max(1, len(re.sub(r"\W", "", w))) for w in tokens], float)
    edges = t0 + (t1 - t0) * np.concatenate([[0], np.cumsum(lens) / lens.sum()])
    return [Word(w, float(edges[i]), float(edges[i + 1])) for i, w in enumerate(tokens)]


def say(text, voice, speed=1.0, cache=True, pitch=0.0):
    """(parole con tempi, audio float32 a 24 kHz) per una battuta. Con cache su disco.

    pitch (semitoni): sintetizza più lento e poi accelera, così la durata resta quella giusta e la voce
    sale (serve per una voce di bambina partendo da una voce adulta)."""
    if pitch:
        from scipy.signal import resample_poly
        p = 2 ** (pitch / 12)
        words, audio = say(text, voice, speed / p, cache)
        audio = resample_poly(audio, 1000, int(round(1000 * p))).astype(np.float32)
        return [Word(w.text, w.start / p, w.end / p) for w in words], audio
    key = hashlib.sha1(json.dumps([text, voice, speed, MODEL_SHA256, PAUSES]).encode()).hexdigest()[:20]
    path = CACHE / "lines" / f"{key}.npz"
    if cache and path.exists():
        d = np.load(path, allow_pickle=False)
        words = [Word(str(w), float(s), float(e)) for w, s, e in zip(d["w"], d["s"], d["e"])]
        return words, d["audio"]
    k = engine()
    audio, sr, timings = k.create_timed(text, voice=style(voice), speed=speed, sentence_pause=PAUSES[0],
                                        clause_pause=PAUSES[1])
    assert sr == SR
    audio = audio.astype(np.float32)
    words = _words(text, timings, len(audio))
    if cache:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(path, audio=audio, w=np.array([w.text for w in words]), s=np.array([w.start for w in words]),
                 e=np.array([w.end for w in words]))
    return words, audio


def through_door(audio):
    """Voce dall'altra parte di una porta: niente alti, un po' di corpo sui bassi medi, stanza piccola."""
    from scipy.signal import butter, sosfilt
    x = sosfilt(butter(4, 1400, "low", fs=SR, output="sos"), audio)
    x = x + 0.35 * sosfilt(butter(2, [180, 500], "band", fs=SR, output="sos"), audio)
    ir = np.random.default_rng(1).normal(0, 1, int(0.12 * SR)) * np.exp(-np.arange(int(0.12 * SR)) / (0.03 * SR))
    wet = np.convolve(x, ir / np.sqrt((ir ** 2).sum()))[: len(x)]
    y = x + 0.25 * wet
    return (y / (np.abs(y).max() + 1e-9) * np.abs(audio).max() * 0.9).astype(np.float32)
