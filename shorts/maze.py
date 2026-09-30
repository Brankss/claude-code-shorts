"""Labirinto: 4 liquidi partono dagli angoli e scorrono nei corridoi; vince il primo che arriva al centro.

Ogni cella ha un tempo di attraversamento casuale; i liquidi si propagano con un Dijkstra
multi-sorgente, quindi chi arriva prima in una cella la occupa e blocca gli altri.
Tutto è deterministico dato il seed.
"""

import heapq
from collections import deque
from dataclasses import dataclass

import numpy as np

N = 21                      # celle per lato
X0, Y0, SIZE = 60.0, 470.0, 960.0
CELL = SIZE / N
BRAID = 0.03               # quota di muri rimossi per creare percorsi alternativi
GOAL = (N // 2, N // 2)
SOURCES = [(0, 0), (0, N - 1), (N - 1, 0), (N - 1, N - 1)]  # (riga, colonna)


@dataclass
class Maze:
    seed: int
    open_e: np.ndarray       # (N, N) passaggio verso est
    open_s: np.ndarray       # (N, N) passaggio verso sud
    w: np.ndarray            # (N, N) tempo di attraversamento
    owner: np.ndarray        # (N, N) squadra che occupa la cella (-1 = nessuna)
    arrival: np.ndarray      # (N, N) quando il liquido entra
    parent: np.ndarray       # (N, N, 2) cella da cui è entrato
    dist: np.ndarray         # (N, N) passi dal centro (ignorando i liquidi)
    t_win: float
    winner: int
    trapped: list            # (tempo, squadra)

    def neighbors(self, r, c):
        if c + 1 < N and self.open_e[r, c]:
            yield r, c + 1
        if c > 0 and self.open_e[r, c - 1]:
            yield r, c - 1
        if r + 1 < N and self.open_s[r, c]:
            yield r + 1, c
        if r > 0 and self.open_s[r - 1, c]:
            yield r - 1, c

    def best(self, team, t):
        """Distanza minima dal centro raggiunta dalla squadra al tempo t."""
        m = (self.owner == team) & (self.arrival <= t)
        return int(self.dist[m].min()) if m.any() else int(self.dist[SOURCES[team]])

    def path(self):
        """Percorso del vincitore dalla sua sorgente al centro."""
        cells = [GOAL]
        while tuple(self.parent[cells[-1]]) != (-1, -1):
            cells.append(tuple(self.parent[cells[-1]]))
        return cells[::-1]


def generate(seed):
    rng = np.random.default_rng(seed)
    open_e = np.zeros((N, N), bool)
    open_s = np.zeros((N, N), bool)
    # Recursive backtracker: corridoi lunghi e sinuosi.
    seen = np.zeros((N, N), bool)
    stack = [(int(rng.integers(N)), int(rng.integers(N)))]
    seen[stack[0]] = True
    while stack:
        r, c = stack[-1]
        nbrs = [(r + dr, c + dc) for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0))
                if 0 <= r + dr < N and 0 <= c + dc < N and not seen[r + dr, c + dc]]
        if not nbrs:
            stack.pop()
            continue
        nr, nc = nbrs[int(rng.integers(len(nbrs)))]
        if nr == r:
            open_e[r, min(c, nc)] = True
        else:
            open_s[min(r, nr), c] = True
        seen[nr, nc] = True
        stack.append((nr, nc))
    # Braid: qualche muro in meno, così esistono più strade.
    open_e[:, :-1] |= rng.random((N, N - 1)) < BRAID
    open_s[:-1, :] |= rng.random((N - 1, N)) < BRAID
    w = rng.uniform(0.55, 1.45, (N, N))

    m = Maze(seed, open_e, open_s, w, np.full((N, N), -1), np.full((N, N), np.inf),
             np.full((N, N, 2), -1), np.zeros((N, N), int), 0.0, -1, [])

    # Distanze dal centro (BFS).
    dist = np.full((N, N), -1)
    dist[GOAL] = 0
    q = deque([GOAL])
    while q:
        cell = q.popleft()
        for nb in m.neighbors(*cell):
            if dist[nb] < 0:
                dist[nb] = dist[cell] + 1
                q.append(nb)
    m.dist = dist

    # Dijkstra multi-sorgente fino a riempire tutto.
    heap = [(0.0, s, team, (-1, -1)) for team, s in enumerate(SOURCES)]
    heapq.heapify(heap)
    while heap:
        t, cell, team, par = heapq.heappop(heap)
        if m.owner[cell] >= 0:
            continue
        m.owner[cell], m.arrival[cell], m.parent[cell] = team, t, par
        for nb in m.neighbors(*cell):
            if m.owner[nb] < 0:
                heapq.heappush(heap, (t + w[cell], nb, team, cell))

    m.winner = int(m.owner[GOAL])
    m.t_win = float(m.arrival[GOAL] + w[GOAL])
    for team in range(len(SOURCES)):
        mask = m.owner == team
        stop = float((m.arrival[mask] + w[mask]).max())
        if stop < m.t_win:
            m.trapped.append((stop, team))
    m.trapped.sort()
    return m


def drama_score(m):
    samples = np.linspace(0, m.t_win, 120)
    leader, changes = None, 0
    lead_at = []
    for t in samples[8:]:
        b = [m.best(k, t) for k in range(len(SOURCES))]
        top = int(np.argmin(b))
        if leader is None:
            leader = top
        elif top != leader and b[top] < b[leader]:
            leader = top
            changes += 1
        lead_at.append(leader)
    final = sorted(m.best(k, m.t_win) for k in range(len(SOURCES)) if k != m.winner)
    runner_up = final[0]
    n_trapped = len(m.trapped)
    score = min(changes, 8) * 2.0
    score += 5.0 if runner_up <= 3 else (2.0 if runner_up <= 6 else 0.0)
    score += {0: 0.0, 1: 3.0, 2: 2.0}.get(n_trapped, -5.0)
    score += 3.0 if lead_at[int(len(lead_at) * 0.6)] != m.winner else 0.0
    return {"score": score, "lead_changes": changes, "runner_up_steps": runner_up,
            "trapped": n_trapped, "winner": m.winner}
