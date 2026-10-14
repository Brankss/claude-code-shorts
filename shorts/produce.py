"""Dal Job al file finale: audio, encoding H.264, metadati."""

import json
import multiprocessing as mp
import subprocess
import time
from pathlib import Path

import imageio_ffmpeg
import skia

from . import audio, publishing
from .base import FPS, H, W


def _ffmpeg_in():
    return ["-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]


_JOB = None


def _worker_init():
    _JOB.render(0)  # ogni processo cattura il primo frame per la dissolvenza del loop


def _worker_render(f):
    return _JOB.render(f).tobytes()


def frames(job):
    """Frame in ordine come bytes RGBA. Con job.workers > 1 li renderizzano più processi in parallelo
    (fork: ereditano il job già preparato), a blocchi così la memoria resta limitata."""
    global _JOB
    workers = getattr(job, "workers", 1)
    if workers <= 1:
        for f in range(job.n_frames):
            yield job.render(f).tobytes()
        return
    _JOB = job
    batch = workers * 6
    with mp.get_context("fork").Pool(workers, initializer=_worker_init) as pool:
        for b0 in range(0, job.n_frames, batch):
            yield from pool.imap(_worker_render, range(b0, min(job.n_frames, b0 + batch)))


def encode(job, wav, out):
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    # Tetto al bitrate: 5M per i video corti, più basso per quelli lunghi (What If) così restano sotto i 30 MB.
    mbps = min(5.0, 28 * 8 / (job.n_frames / FPS) - 0.25)
    vf = ["-vf", job.vf] if getattr(job, "vf", None) else []
    cmd = [ff, "-y", "-loglevel", "error", *_ffmpeg_in(), "-i", str(wav), *vf,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", f"{mbps:.1f}M", "-bufsize", f"{2 * mbps:.1f}M",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t = time.time()
    for f, data in enumerate(frames(job)):
        proc.stdin.write(data)
        if f % 600 == 0:
            print(f"  frame {f}/{job.n_frames} ({time.time() - t:.0f}s)")
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg ha fallito")


def produce(job, out):
    """Scrive out (.mp4), più .json (metadati) e .txt (scheda di pubblicazione da copiare)."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    wav = out.with_suffix(".wav")
    audio.write_wav(wav, job.audio())
    encode(job, wav, out)
    wav.unlink()
    out.with_suffix(".json").write_text(json.dumps(job.meta, indent=2, ensure_ascii=False, default=str))
    out.with_suffix(".txt").write_text(publishing.sheet(job.meta))
    print(f"fatto: {out}")


def stills(job, times, out_dir):
    """Solo frame PNG, con la stessa post-produzione (job.vf) del video."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    job.render(0)  # serve per il loop finale
    vf = getattr(job, "vf", None)
    for s in times:
        f = min(int(s * FPS), job.n_frames - 1)
        path = out_dir / f"frame_{s:06.2f}.png"
        if not vf:
            skia.Image.fromarray(job.render(f).copy()).save(str(path), skia.kPNG)
            continue
        cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", *_ffmpeg_in(), "-vf", vf,
               "-frames:v", "1", str(path)]
        subprocess.run(cmd, input=job.render(f).tobytes(), check=True)


def small_copy(src, dst, max_mb=9.5):
    """Copia leggera per chat come Discord (limite 10 MB sui server senza boost).

    Se il video sta già sotto il limite lo copia così com'è; altrimenti lo ricomprime
    in 1080p con un tetto di bitrate (le grafiche piatte reggono benissimo).
    """
    import shutil
    src, dst = Path(src), Path(dst)
    if src.stat().st_size <= max_mb * 1024 * 1024:
        shutil.copyfile(src, dst)
        return dst
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-i", str(src),
           "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "1.7M", "-bufsize", "3.4M",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst)]
    if subprocess.run(cmd).returncode != 0:
        raise SystemExit("ffmpeg ha fallito (copia leggera)")
    return dst
