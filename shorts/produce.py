"""Dal Job al file finale: audio, encoding H.264, metadati."""

import json
import subprocess
import time
from pathlib import Path

import imageio_ffmpeg
import skia

from . import audio, publishing
from .base import FPS, H, W


def encode(job, wav, out):
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(wav),
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "5M", "-bufsize", "10M",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t = time.time()
    for f in range(job.n_frames):
        proc.stdin.write(job.render(f).tobytes())
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
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    job.render(0)  # serve per il loop finale
    for s in times:
        f = min(int(s * FPS), job.n_frames - 1)
        skia.Image.fromarray(job.render(f).copy()).save(str(out_dir / f"frame_{s:06.2f}.png"), skia.kPNG)
