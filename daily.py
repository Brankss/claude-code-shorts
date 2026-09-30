"""Video del giorno, pensato per girare in automatico una volta al giorno.

    python daily.py                      # video di oggi in out/daily/
    python daily.py --date 2026-10-02    # rigenera un giorno specifico (stesso identico video)

Niente stato da salvare: tutto deriva dalla data.
- Il numero di episodio parte da START.
- Ogni 12 giorni vince una volta ogni segno, in un ordine rimescolato per ciclo
  (così nessuno si accorge dello schema e nessun segno vince sempre).
- Ogni giorno usa un blocco di seed diverso; tra quelli dove vince il segno del
  giorno si prende la partita con il drama score più alto.
"""

import argparse
import datetime as dt

import numpy as np

from make_contagio import produce
from shorts import contagio
from shorts.themes import THEMES

START = dt.date(2026, 9, 30)
SEEDS_PER_BATCH = 1000
MAX_BATCHES = 3


def pick(theme_name, episode):
    n_teams = len(THEMES[theme_name]["teams"])
    cycle, idx = divmod(episode - 1, n_teams)
    target = int(np.random.default_rng(cycle).permutation(n_teams)[idx])
    base = episode * 100_000
    best_any = None
    for b in range(MAX_BATCHES):
        seeds = range(base + b * SEEDS_PER_BATCH, base + (b + 1) * SEEDS_PER_BATCH)
        scored = [(d["score"], s, d) for s, (_, d) in contagio.search(n_teams, seeds) if d]
        scored.sort(key=lambda x: -x[0])
        if scored and (best_any is None or scored[0][0] > best_any[0]):
            best_any = scored[0]
        mine = [x for x in scored if x[2]["winner"] == target]
        if mine:
            return mine[0][1]
    if best_any is None:
        raise SystemExit("Nessuna partita valida trovata")
    return best_any[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--theme", default="zodiac", choices=sorted(THEMES))
    ap.add_argument("--out-dir", default="out/daily")
    args = ap.parse_args()

    episode = (args.date - START).days + 1
    if episode < 1:
        raise SystemExit(f"La data deve essere dal {START} in poi")
    seed = pick(args.theme, episode)
    produce(args.theme, seed, f"{args.out_dir}/{args.date}_{args.theme}.mp4", episode=episode)


if __name__ == "__main__":
    main()
