"""Render del Labirinto: muri sottili, liquidi piatti che avanzano cella per cella, percorso del vincitore."""

import numpy as np
import skia

from . import gfx
from .base import FPS, TOTAL, W, BaseRenderer
from .gfx import INK, WHITE, draw_text, ease_in_out, ease_out, fade, mix, rgba
from .maze import CELL, GOAL, N, SIZE, SOURCES, X0, Y0

VT_WIN = 32.0     # il vincitore arriva sempre qui, qualunque sia la durata simulata
WALL = 3.0
INS = WALL / 2 + 1.5


def cell_xy(r, c):
    return X0 + c * CELL, Y0 + r * CELL


class Timeline:
    def __init__(self, m, teams):
        self.m = m
        self.teams = teams
        self.scale = VT_WIN / m.t_win
        n = int(TOTAL * FPS)
        self.n_frames = n

        # Celle occupate prima della vittoria, ordinate per arrivo.
        cells = [(m.arrival[r, c], r, c) for r in range(N) for c in range(N) if m.arrival[r, c] < m.t_win]
        cells.sort()
        self.cells = cells
        self.cell_t = np.array([x[0] for x in cells])

        # Passaggi aperti tra celle dello stesso colore che non sono padre-figlio: si chiudono quando entrambe sono piene.
        joins = []
        fin = m.arrival + m.w
        for r in range(N):
            for c in range(N):
                for (nr, nc), is_open in (((r, c + 1), c + 1 < N and m.open_e[r, c]),
                                          ((r + 1, c), r + 1 < N and m.open_s[r, c])):
                    if not is_open or m.owner[r, c] != m.owner[nr, nc]:
                        continue
                    if tuple(m.parent[nr, nc]) == (r, c) or tuple(m.parent[r, c]) == (nr, nc):
                        continue
                    t = max(fin[r, c], fin[nr, nc])
                    if t < m.t_win:
                        joins.append((t, r, c, nr, nc))
        joins.sort()
        self.joins = joins
        self.join_t = np.array([j[0] for j in joins]) if joins else np.zeros(0)

        # Progresso e leader per frame.
        n_t = len(teams)
        self.best0 = np.array([m.dist[s] for s in SOURCES], float)
        self.progress = np.zeros((n, n_t))
        self.best = np.zeros((n, n_t), int)
        self.leader = np.zeros(n, int)
        cur = np.zeros(n_t)
        lead = 0
        for f in range(n):
            t = self.sim_t(f)
            b = np.array([m.best(k, t) for k in range(n_t)])
            self.best[f] = b
            cur = cur + ((1 - b / self.best0) - cur) * 0.15
            self.progress[f] = cur
            top = int(np.argmin(b))
            if b[top] < b[lead]:
                lead = top
            self.leader[f] = lead

        self.news = [(t * self.scale, team, "is trapped") for t, team in m.trapped]
        # "Final stretch" quando qualcuno è a pochi passi dal centro (se c'è tempo per vederlo).
        close = np.nonzero(self.best.min(axis=1) <= 6)[0]
        if len(close) and close[0] / FPS < VT_WIN - 3:
            self.news.append((close[0] / FPS, None, "FINAL STRETCH"))
        self.news.sort(key=lambda x: x[0])

        self.path = m.path()

    def sim_t(self, f):
        return min(f / FPS, VT_WIN) / self.scale


class Renderer(BaseRenderer):
    def __init__(self, tl, title_lines, subtitle):
        super().__init__(title_lines, subtitle)
        self.tl = tl
        self.m = tl.m
        self.teams = tl.teams
        # Muri come un unico path.
        p = skia.Path()
        for r in range(N):
            for c in range(N):
                x, y = cell_xy(r, c)
                if c + 1 < N and not self.m.open_e[r, c]:
                    p.moveTo(x + CELL, y)
                    p.lineTo(x + CELL, y + CELL)
                if r + 1 < N and not self.m.open_s[r, c]:
                    p.moveTo(x, y + CELL)
                    p.lineTo(x + CELL, y + CELL)
        p.addRect(skia.Rect(X0, Y0, X0 + SIZE, Y0 + SIZE))
        self.walls = p

    def draw(self, c, f, vt):
        tl, m = self.tl, self.m
        t = tl.sim_t(f)
        won = vt >= VT_WIN
        a_win = vt - VT_WIN

        dim = 1.0 - 0.55 * ease_in_out(a_win / 0.8) if won else 1.0
        self._liquid(c, t, dim)
        c.drawPath(self.walls, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=WALL,
                                          Color=rgba(INK, 0.28), StrokeCap=skia.Paint.kRound_Cap))

        # Sorgenti e traguardo.
        for team, (r, cc) in enumerate(SOURCES):
            x, y = cell_xy(r, cc)
            if m.arrival[r, cc] >= t:
                c.drawCircle(x + CELL / 2, y + CELL / 2, CELL * 0.22,
                             skia.Paint(AntiAlias=True, Color=rgba(self.teams[team].color)))
        gx, gy = cell_xy(*GOAL)
        gcol = self.teams[m.winner].color if won else INK
        c.drawCircle(gx + CELL / 2, gy + CELL / 2, CELL * 0.3, skia.Paint(
            AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.5, Color=rgba(gcol, 0.8)))

        if won:
            self._path(c, a_win)
        self._hud(c, f, vt)

    def _liquid(self, c, t, dim):
        tl, m = self.tl, self.m
        hi = int(np.searchsorted(tl.cell_t, t, side="right"))
        span = CELL - 2 * INS
        winner = m.winner
        for a, r, cc in tl.cells[:hi]:
            k = min(1.0, (t - a) / m.w[r, cc])
            team = int(m.owner[r, cc])
            col = self.teams[team].color
            if k < 1:
                col = mix(col, WHITE, 0.3)
            alpha = 0.9 * (dim if team != winner else max(dim, 0.75))
            paint = skia.Paint(AntiAlias=True, Color=rgba(col, alpha))
            x, y = cell_xy(r, cc)
            pr, pc = m.parent[r, cc]
            if pr < 0:
                h = span * (0.3 + 0.7 * k) / 2
                cx, cy = x + CELL / 2, y + CELL / 2
                c.drawRect(skia.Rect(cx - h, cy - h, cx + h, cy + h), paint)
                continue
            dr, dc = r - pr, cc - pc
            L = span * k
            if dc == 1:
                c.drawRect(skia.Rect(x - INS, y + INS, x + INS + L, y + CELL - INS), paint)
            elif dc == -1:
                c.drawRect(skia.Rect(x + CELL - INS - L, y + INS, x + CELL + INS, y + CELL - INS), paint)
            elif dr == 1:
                c.drawRect(skia.Rect(x + INS, y - INS, x + CELL - INS, y + INS + L), paint)
            else:
                c.drawRect(skia.Rect(x + INS, y + CELL - INS - L, x + CELL - INS, y + CELL + INS), paint)
        # Chiude i passaggi tra celle dello stesso colore già piene.
        hj = int(np.searchsorted(tl.join_t, t, side="right"))
        for _, r, cc, nr, nc in tl.joins[:hj]:
            team = int(m.owner[r, cc])
            alpha = 0.9 * (dim if team != winner else max(dim, 0.75))
            paint = skia.Paint(Color=rgba(self.teams[team].color, alpha))
            x, y = cell_xy(r, cc)
            if nc == cc + 1:
                c.drawRect(skia.Rect(x + CELL - INS, y + INS, x + CELL + INS, y + CELL - INS), paint)
            else:
                c.drawRect(skia.Rect(x + INS, y + CELL - INS, x + CELL - INS, y + CELL + INS), paint)

    def _path(self, c, a):
        """Il percorso del vincitore si disegna dalla sorgente al centro."""
        k = ease_in_out((a - 0.3) / 1.8)
        if k <= 0:
            return
        pts = [(cell_xy(r, cc)[0] + CELL / 2, cell_xy(r, cc)[1] + CELL / 2) for r, cc in self.tl.path]
        n = (len(pts) - 1) * k
        i = int(n)
        p = skia.Path()
        p.moveTo(*pts[0])
        for q in range(1, i + 1):
            p.lineTo(*pts[q])
        if i < len(pts) - 1:
            fr = n - i
            p.lineTo(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * fr, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * fr)
        col = mix(self.teams[self.m.winner].color, WHITE, 0.35)
        c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=7,
                                 Color=rgba(col), StrokeCap=skia.Paint.kRound_Cap,
                                 StrokeJoin=skia.Paint.kRound_Join))

    def _hud(self, c, f, vt):
        tl = self.tl
        k = self.header(c, vt)
        if k <= 0:
            return
        won = vt >= VT_WIN
        n_t = len(self.teams)

        # Quattro barrette di progresso verso il centro.
        bx, by, bw, bh, gap = 90.0, 292.0, 900.0, 8.0, 24.0
        seg = (bw - gap * (n_t - 1)) / n_t
        for i in range(n_t):
            x = bx + i * (seg + gap)
            track = skia.RRect.MakeRectXY(skia.Rect(x, by, x + seg, by + bh), bh / 2, bh / 2)
            c.drawRRect(track, skia.Paint(AntiAlias=True, Color=rgba(INK, 0.1 * k)))
            p = 1.0 if (won and i == self.m.winner) else float(np.clip(tl.progress[f][i], 0, 1))
            if p > 0.01:
                c.save()
                c.clipRRect(track, True)
                c.drawRect(skia.Rect(x, by, x + seg * p, by + bh), skia.Paint(Color=rgba(self.teams[i].color, k)))
                c.restore()

        y = 346
        ft, fn = gfx.text(28), gfx.title(28)
        lead = self.m.winner if won else int(tl.leader[f])
        team = self.teams[lead]
        label = "Winner  " if won else "Closest  "
        draw_text(c, label, ft, bx, y, color=INK, alpha=0.5 * k, align="left")
        x = bx + ft.measureText(label)
        draw_text(c, team.name, fn, x, y, color=team.color, alpha=k, align="left")
        if not won:
            x += fn.measureText(team.name)
            steps = int(tl.best[f][lead])
            draw_text(c, f"  {steps} steps away", ft, x, y, color=INK, alpha=0.7 * k, align="left")
        trapped = sum(1 for tt, _ in self.m.trapped if tt * tl.scale <= vt)
        draw_text(c, f"{n_t - trapped} of {n_t} flowing", ft, bx + bw, y, color=INK, alpha=0.5 * k, align="right")

        if won:
            a = vt - VT_WIN
            kk = ease_out((a - 0.8) / 0.8)
            if kk > 0:
                w = self.teams[self.m.winner]
                fw = gfx.title(46)
                s1, s2 = w.name + " ", "wins"
                tw = fw.measureText(s1) + gfx.text(46).measureText(s2)
                draw_text(c, s1, fw, W / 2 - tw / 2, 432, color=w.color, alpha=kk, align="left")
                draw_text(c, s2, gfx.text(46), W / 2 - tw / 2 + fw.measureText(s1), 432, color=INK,
                          alpha=0.75 * kk, align="left")
            k3 = ease_out((a - 2.2) / 0.8)
            if k3 > 0:
                draw_text(c, "Comment your color for the next one", gfx.text(30), W / 2, 1490,
                          color=INK, alpha=0.55 * k3)
            return

        shown = [n for n in tl.news if 0 <= vt - n[0] < 2.2]
        if shown:
            v0, t_i, what = shown[-1]
            a = fade(vt - v0, 0.3, 1.5, 0.4)
            if t_i is None:
                draw_text(c, what, gfx.text(28), W / 2, 432, color=INK, alpha=0.8 * a, tracking=7)
            else:
                team = self.teams[t_i]
                fn2, fw2 = gfx.title(30), gfx.text(30)
                w = fn2.measureText(team.name + " ") + fw2.measureText(what)
                x = W / 2 - w / 2
                draw_text(c, team.name + " ", fn2, x, 432, color=team.color, alpha=a, align="left")
                draw_text(c, what, fw2, x + fn2.measureText(team.name + " "), 432, color=INK, alpha=0.7 * a,
                          align="left")
