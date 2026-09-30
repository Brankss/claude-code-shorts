"""Registro dei format. Ognuno sa scegliere il seed di un episodio e preparare il lavoro di render."""

from dataclasses import dataclass
from typing import Callable

import numpy as np

from . import contagio, maze, sync
from .themes import COLORS4, THEMES


@dataclass
class Job:
    n_frames: int
    render: Callable      # frame -> buffer RGBA
    audio: Callable       # () -> array stereo
    meta: dict


def rotating(episode, n):
    """Ogni n episodi ogni squadra vince una volta, in un ordine rimescolato per ciclo."""
    cycle, idx = divmod(episode - 1, n)
    return int(np.random.default_rng(cycle).permutation(n)[idx])


def _meta(name, seed, episode, title, subtitle, hashtags, winner=None, stats=None):
    t = title + (f" #{episode}" if episode else "")
    return {
        "format": name, "seed": seed, "episode": episode, "winner": winner, "stats": stats,
        "title": f"{t} #shorts",
        "description": f"{subtitle}.\n" + " ".join(hashtags),
    }


class Contagio:
    name = "contagio"
    theme = "zodiac"

    def pick(self, episode, batches=3):
        teams = THEMES[self.theme]["teams"]
        target = rotating(episode, len(teams))
        best_any = None
        for b in range(batches):
            seeds = range(episode * 100_000 + b * 1000, episode * 100_000 + (b + 1) * 1000)
            scored = sorted(((d["score"], s, d) for s, (_, d) in contagio.search(len(teams), seeds) if d),
                            key=lambda x: -x[0])
            if scored and (best_any is None or scored[0][0] > best_any[0]):
                best_any = scored[0]
            mine = [x for x in scored if x[2]["winner"] == target]
            if mine:
                return mine[0][1]
        if best_any is None:
            raise SystemExit("Nessuna partita valida trovata")
        return best_any[1]

    def prepare(self, seed, episode=None):
        from . import contagio_audio
        from .contagio_render import Renderer, Timeline
        theme = THEMES[self.theme]
        rec = contagio.simulate(seed, len(theme["teams"]))
        stats = contagio.drama_score(rec)
        if stats is None:
            raise SystemExit(f"Il seed {seed} finisce fuori finestra (t_end={rec.t_end})")
        tl = Timeline(rec, theme)
        r = Renderer(tl, theme)
        winner = theme["teams"][rec.winner].name
        return Job(r.n_frames, r.render, lambda: contagio_audio.build(tl),
                   _meta(self.name, seed, episode, "Which Zodiac Sign Wins?", theme["subtitle"],
                         theme["hashtags"], winner, stats))


class Maze:
    name = "maze"
    title_lines = ["Which color reaches", "the center first?"]
    subtitle = "Pick one before it starts"
    hashtags = ["#maze", "#satisfying", "#simulation", "#relaxing", "#shorts"]

    def pick(self, episode):
        target = rotating(episode, len(COLORS4))
        scored = []
        for s in range(episode * 100_000, episode * 100_000 + 1500):
            m = maze.generate(s)
            d = maze.drama_score(m)
            if d["winner"] == target:
                scored.append((d["score"], s))
        return max(scored)[1]

    def prepare(self, seed, episode=None):
        from . import maze_audio
        from .maze_render import Renderer, Timeline
        m = maze.generate(seed)
        tl = Timeline(m, COLORS4)
        r = Renderer(tl, self.title_lines, self.subtitle)
        return Job(r.n_frames, r.render, lambda: maze_audio.build(tl),
                   _meta(self.name, seed, episode, "Which Color Reaches The Center First?", self.subtitle,
                         self.hashtags, COLORS4[m.winner].name, maze.drama_score(m)))


class Sync:
    name = "sync"
    title_lines = ["Wait for them", "to sync again"]
    subtitle = "Every hit plays a note"
    hashtags = ["#satisfying", "#polyrhythm", "#relaxing", "#asmr", "#shorts"]

    def pick(self, episode):
        return episode

    def prepare(self, seed, episode=None):
        p = sync.params(seed)
        r = sync.Renderer(p, self.title_lines, self.subtitle)
        return Job(r.n_frames, r.render, lambda: sync.build_audio(p),
                   _meta(self.name, seed, episode, "Wait For Them To Sync Again", self.subtitle,
                         self.hashtags, stats=p.__dict__))


FORMATS = {f.name: f for f in (Contagio(), Maze(), Sync())}
CYCLE = ["contagio", "maze", "sync"]
