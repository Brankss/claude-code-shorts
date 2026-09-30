"""Genera uno short di Contagio.

    python make_contagio.py --theme zodiac --seeds 1000 --out out/zodiac_001.mp4
    python make_contagio.py --seed 149 --stills 0.5,9,26,34 --out out/preview   # solo frame PNG
"""

import argparse
import json
import subprocess
import time
from pathlib import Path

import imageio_ffmpeg
import skia

from shorts import audio, contagio, contagio_audio
from shorts.contagio_render import FPS, TOTAL, Renderer, Timeline
from shorts.themes import THEMES


def pick_seed(n_teams, start, count):
    t = time.time()
    res = contagio.search(n_teams, range(start, start + count))
    ranked = sorted(((d["score"], s, d) for s, (_, d) in res if d), key=lambda x: -x[0])
    print(f"{count} partite simulate in {time.time() - t:.0f}s, {len(ranked)} nella finestra di durata")
    for score, s, d in ranked[:5]:
        print(f"  seed {s}: {d}")
    if not ranked:
        raise SystemExit("Nessuna partita nella finestra: aumenta --seeds")
    return ranked[0][1]


def encode(renderer, tl, wav, out):
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "1080x1920", "-r", str(FPS), "-i", "-",
           "-i", str(wav),
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "5M", "-bufsize", "10M", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t = time.time()
    for f in range(tl.n_frames):
        proc.stdin.write(renderer.render(f).tobytes())
        if f % 300 == 0:
            print(f"  frame {f}/{tl.n_frames} ({time.time() - t:.0f}s)")
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg ha fallito")


def produce(theme_name, seed, out, episode=None):
    """Renderizza il video di un seed e scrive accanto .json (metadati) e .txt (titolo e descrizione)."""
    theme = THEMES[theme_name]
    rec = contagio.simulate(seed, len(theme["teams"]))
    stats = contagio.drama_score(rec)
    if stats is None:
        raise SystemExit(f"Il seed {seed} finisce fuori finestra (t_end={rec.t_end})")
    tl = Timeline(rec, theme)
    renderer = Renderer(tl, theme)
    winner = theme["teams"][rec.winner]
    print(f"seed {seed}: vince {winner.name} a {rec.t_end:.2f}s (video {tl.vt_win:.2f}s) {stats}")

    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    wav = out.with_suffix(".wav")
    audio.write_wav(wav, contagio_audio.build(tl))
    encode(renderer, tl, wav, out)
    wav.unlink()

    title = " ".join(theme["title"]).title()
    if episode:
        title += f" #{episode}"
    meta = {
        "seed": seed, "theme": theme_name, "winner": winner.name, "episode": episode,
        "duration": TOTAL, "stats": stats,
        "title": f"{title} \U0001F631 #shorts",
        "description": f"{theme['subtitle'].capitalize()}! Physics simulation, every hit converts.\n"
                       + " ".join(theme["hashtags"]),
    }
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    out.with_suffix(".txt").write_text(f"{meta['title']}\n\n{meta['description']}\n")
    print(f"fatto: {out}")
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", default="zodiac", choices=sorted(THEMES))
    ap.add_argument("--seed", type=int)
    ap.add_argument("--seeds", type=int, default=1000)
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--stills", help="tempi video (s) separati da virgola: salva solo PNG")
    ap.add_argument("--out", default="out/contagio.mp4")
    args = ap.parse_args()

    theme = THEMES[args.theme]
    n_teams = len(theme["teams"])
    seed = args.seed if args.seed is not None else pick_seed(n_teams, args.seed_start, args.seeds)

    if not args.stills:
        produce(args.theme, seed, args.out)
        return

    rec = contagio.simulate(seed, n_teams)
    tl = Timeline(rec, theme)
    renderer = Renderer(tl, theme)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for s in args.stills.split(","):
        f = min(int(float(s) * FPS), tl.n_frames - 1)
        buf = renderer.render(f)
        skia.Image.fromarray(buf.copy()).save(str(out / f"frame_{float(s):06.2f}.png"), skia.kPNG)


if __name__ == "__main__":
    main()
