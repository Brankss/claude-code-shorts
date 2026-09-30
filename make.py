"""Genera uno short di un format.

    python make.py --format maze --episode 1 --out out/maze_001.mp4
    python make.py --format contagio --seed 405 --out out/zodiac.mp4
    python make.py --format sync --episode 3 --stills 0.5,20,39 --out out/preview   # solo frame PNG
"""

import argparse

from shorts.formats import FORMATS
from shorts.produce import produce, stills


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", required=True, choices=sorted(FORMATS))
    ap.add_argument("--episode", type=int, default=1)
    ap.add_argument("--seed", type=int, help="salta la ricerca e usa questo seed")
    ap.add_argument("--stills", help="tempi video (s) separati da virgola: salva solo PNG")
    ap.add_argument("--out", default="out/short.mp4")
    args = ap.parse_args()

    fmt = FORMATS[args.format]
    seed = args.seed if args.seed is not None else fmt.pick(args.episode)
    job = fmt.prepare(seed, args.episode)
    print(f"{args.format} #{args.episode}, seed {seed}: {job.meta['winner'] or ''} {job.meta['stats']}")
    if args.stills:
        stills(job, [float(s) for s in args.stills.split(",")], args.out)
    else:
        produce(job, args.out)


if __name__ == "__main__":
    main()
