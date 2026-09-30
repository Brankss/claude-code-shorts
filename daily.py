"""Video del giorno, pensato per girare in automatico una volta al giorno.

    python daily.py                      # video di oggi in out/daily/
    python daily.py --date 2026-10-02    # rigenera un giorno specifico (stesso identico video)

Niente stato da salvare: tutto deriva dalla data.
- I format si alternano a rotazione (CYCLE): Contagio, Labirinto, Sync, Contagio...
- Ogni format ha la sua numerazione di episodi.
- Nei format con vincitore, ogni squadra vince una volta per ciclo, in ordine rimescolato.
"""

import argparse
import datetime as dt

from shorts import publishing
from shorts.formats import CYCLE, FORMATS
from shorts.produce import produce

START = dt.date(2026, 9, 30)


def plan(date):
    day = (date - START).days
    if day < 0:
        raise SystemExit(f"La data deve essere dal {START} in poi")
    return CYCLE[day % len(CYCLE)], day // len(CYCLE) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--out-dir", default="out/daily")
    args = ap.parse_args()

    name, episode = plan(args.date)
    fmt = FORMATS[name]
    seed = fmt.pick(episode)
    job = fmt.prepare(seed, episode)
    job.meta.update(publishing.build(name, episode, args.date))
    print(f"{args.date}: {name} #{episode}, seed {seed}, pubblicazione {job.meta['publish_at']}")
    produce(job, f"{args.out_dir}/{args.date}_{name}.mp4")


if __name__ == "__main__":
    main()
