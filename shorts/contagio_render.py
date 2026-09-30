"""Render di Contagio in stile minimal: colori piatti, linee sottili, testo sobrio, niente flash.

La timeline mappa il tempo video sul tempo di simulazione (slow-mo sul colpo finale)
e colloca gli eventi (didascalie, eliminazioni) nel video.
"""

import math

import numpy as np
import skia

from . import gfx
from .base import FPS, TOTAL, W, WORLD_TOP, BaseRenderer
from .contagio import ARENA_R, BALL_R, CENTER, ESCAPING, GONE, H
from .gfx import BG, BLACK, INK, draw_text, ease_in_out, ease_out, fade, mix, rgba

PRE, POST, SLOW, CELEB_RATE = 0.55, 0.25, 0.3, 0.7

EVENT_TEXT = {
    "speed": "SPEED UP",
    "gravity_on": "GRAVITY ON",
    "gravity_flip": "GRAVITY FLIPPED",
    "gap": "THE WALL OPENS",
    "duel": "FINAL TWO",
}


class Timeline:
    """Mappa tempo video -> tempo simulazione e colloca gli eventi nel video."""

    def __init__(self, rec, theme):
        self.rec = rec
        self.teams = theme["teams"]
        t_end = rec.t_end
        n = int(TOTAL * FPS)
        s, sims = 0.0, np.zeros(n)
        a0, a1, b0 = t_end - PRE - 0.15, t_end - PRE, t_end + POST
        for f in range(n):
            sims[f] = s
            if s < a0:
                r = 1.0
            elif s < a1:
                r = 1.0 + (SLOW - 1.0) * (s - a0) / 0.15
            elif s < b0:
                r = SLOW
            elif s < b0 + 0.1:
                r = SLOW + (CELEB_RATE - SLOW) * (s - b0) / 0.1
            else:
                r = CELEB_RATE
            s += r / FPS
        self.n_frames = n
        self.sim_t = np.minimum(sims, (len(rec.counts) - 2) * rec.dt)
        self.vt_win = self.vt(t_end)
        self.vt_slow = self.vt(a1)

        # Didascalie degli eventi (mai sovrapposte).
        self.captions = []
        last_end = -1.0
        gravity_seen = False
        for et, kind, _ in rec.events:
            if et > t_end:
                continue
            if kind == "gravity":
                kind = "gravity_flip" if gravity_seen else "gravity_on"
                gravity_seen = True
            v = max(self.vt(et), last_end + 0.1)
            self.captions.append((v, EVENT_TEXT[kind]))
            last_end = v + 2.4

        # Notizie sulle squadre: eliminazioni e "ultima pallina" quando restano poche squadre.
        self.news = []
        for et, team, _, _ in rec.eliminations:
            if et < t_end:
                self.news.append((self.vt(et), team, "is out"))
        counts = rec.counts
        end_step = int(t_end / rec.dt)
        alive = (counts[:end_step] > 0).sum(axis=1)
        for team in range(len(self.teams)):
            c = counts[:end_step, team]
            hits = np.nonzero((c[1:] == 1) & (c[:-1] > 1) & (alive[1:] <= 3))[0]
            if len(hits):
                self.news.append((self.vt((hits[0] + 1) * rec.dt), team, "down to its last ball"))
        self.news.sort()

        # Barra e leader precalcolati per frame (con smoothing).
        n_t = len(self.teams)
        self.bar = np.zeros((n, n_t))
        self.leader = np.zeros(n, int)
        cur = counts[0] / counts[0].sum()
        lead = int(np.argmax(counts[0]))
        for f in range(n):
            c = counts[self.step(f)]
            cur = cur + (c / max(1, c.sum()) - cur) * 0.12
            self.bar[f] = cur
            top = int(np.argmax(c))
            if c[top] > c[lead]:
                lead = top
            self.leader[f] = lead

        conv = np.array(rec.conversions) if rec.conversions else np.zeros((0, 6))
        self.conv_t = conv[:, 0]
        self.conv = conv

    def vt(self, sim_t):
        return int(np.searchsorted(self.sim_t, sim_t)) / FPS

    def step(self, f):
        return min(int(self.sim_t[f] / self.rec.dt), len(self.rec.counts) - 1)


class Renderer(BaseRenderer):
    def __init__(self, tl, theme):
        super().__init__(theme["title"], theme["subtitle"])
        self.tl = tl
        self.rec = tl.rec
        self.teams = theme["teams"]
        # Glifi pre-centrati per ogni squadra.
        gf = gfx.glyph(BALL_R * 1.05)
        self.glyphs = []
        for t in self.teams:
            blob = skia.TextBlob.MakeFromString(t.glyph, gf)
            b = blob.bounds()
            self.glyphs.append((blob, -(b.left() + b.right()) / 2, -(b.top() + b.bottom()) / 2))

    def draw(self, c, f, vt):
        tl, rec = self.tl, self.rec
        s = tl.sim_t[f]
        if vt >= tl.vt_win:
            k = ease_in_out((vt - tl.vt_win) / 1.2)
            col = self.teams[rec.winner].color
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
                skia.Point(*CENTER), 820, [rgba(col, 0.10 * k), rgba(col, 0.0)])))

        c.save()
        c.clipRect(skia.Rect(0, WORLD_TOP, W, H))
        self._camera(c, vt)
        self._arena(c, s)
        self._ripples(c, s)
        self._balls(c, s)
        c.restore()

        self._hud(c, f, vt)
        if vt >= tl.vt_win:
            self._winner(c, vt - tl.vt_win)

    # ---------- mondo ----------

    def _camera(self, c, vt):
        """Zoom leggero verso il colpo finale durante lo slow-mo, poi torna indietro."""
        tl = self.tl
        _, hx, hy = self.rec.final_hit
        zin = ease_in_out((vt - (tl.vt_slow - 0.3)) / 1.2)
        zout = ease_in_out((vt - (tl.vt_win + 0.6)) / 1.4)
        k = zin * (1 - zout)
        z = 1.0 + 0.12 * k
        focus = CENTER + (np.array([hx, hy]) - CENTER) * 0.2 * k
        c.translate(*CENTER)
        c.scale(z, z)
        c.translate(-focus[0], -focus[1])

    def _arena(self, c, s):
        rec = self.rec
        gap_c, gap_h = rec.gap[min(int(s / rec.dt), len(rec.gap) - 1)]
        cx, cy = CENTER
        ring = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3,
                          Color=rgba(INK, 0.4), StrokeCap=skia.Paint.kRound_Cap)
        if gap_h > 0.001:
            rect = skia.Rect.MakeLTRB(cx - ARENA_R, cy - ARENA_R, cx + ARENA_R, cy + ARENA_R)
            c.drawArc(rect, math.degrees(gap_c + gap_h), 360 - math.degrees(2 * gap_h), False, ring)
        else:
            c.drawCircle(cx, cy, ARENA_R, ring)

    def _ripples(self, c, s):
        """Un anello sottile che si allarga a ogni conversione."""
        tl = self.tl
        lo = np.searchsorted(tl.conv_t, s - 0.6)
        hi = np.searchsorted(tl.conv_t, s, side="right")
        for k in range(lo, hi):
            t0, x, y, wt = tl.conv[k][:4]
            a = (s - t0) / 0.6
            c.drawCircle(x, y, BALL_R * (1 + 0.9 * ease_out(a)), skia.Paint(
                AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2,
                Color=rgba(self.teams[int(wt)].color, 0.35 * (1 - a))))

    def _balls(self, c, s):
        rec, tl = self.rec, self.tl
        i0 = min(int(s / rec.dt), len(rec.pos) - 2)
        fr = min(1.0, s / rec.dt - i0)
        pos = rec.pos[i0] * (1 - fr) + rec.pos[i0 + 1] * fr
        team = rec.team[i0 + (1 if fr > 0.5 else 0)]
        state = rec.state[i0]

        # Dissolvenza di colore delle palline appena convertite.
        blend = {}
        lo = np.searchsorted(tl.conv_t, s - 0.3)
        hi = np.searchsorted(tl.conv_t, s, side="right")
        for k in range(lo, hi):
            t0, _, _, wt, lt, ball = tl.conv[k]
            blend[int(ball)] = (int(lt), int(wt), ease_in_out((s - t0) / 0.3))

        for b in range(len(pos)):
            if state[b] == GONE:
                continue
            x, y = pos[b]
            alpha = 1.0
            if state[b] == ESCAPING:
                out = math.hypot(x - CENTER[0], y - CENTER[1]) - ARENA_R
                alpha = max(0.0, 1 - out / 300)
                if alpha <= 0:
                    continue
            if b in blend:
                lt, wt, k = blend[b]
                col = mix(self.teams[lt].color, self.teams[wt].color, k)
                c.drawCircle(x, y, BALL_R, skia.Paint(AntiAlias=True, Color=rgba(col, alpha)))
                self._glyph(c, lt, x, y, col, alpha * (1 - k))
                self._glyph(c, wt, x, y, col, alpha * k)
            else:
                t = int(team[b])
                col = self.teams[t].color
                c.drawCircle(x, y, BALL_R, skia.Paint(AntiAlias=True, Color=rgba(col, alpha)))
                self._glyph(c, t, x, y, col, alpha)

    def _glyph(self, c, team, x, y, ball_col, alpha, scale=1.0):
        blob, dx, dy = self.glyphs[team]
        paint = skia.Paint(AntiAlias=True, Color=rgba(mix(ball_col, BLACK, 0.62), alpha))
        if scale == 1.0:
            c.drawTextBlob(blob, x + dx, y + dy, paint)
            return
        c.save()
        c.translate(x, y)
        c.scale(scale, scale)
        c.drawTextBlob(blob, dx, dy, paint)
        c.restore()

    # ---------- HUD ----------

    def _hud(self, c, f, vt):
        tl, rec = self.tl, self.rec
        k = self.header(c, vt)
        if k <= 0:
            return
        counts = rec.counts[tl.step(f)]
        won = vt >= tl.vt_win
        n_t = len(self.teams)

        # Barra sottile a segmenti.
        bx, by, bw, bh, gap = 90.0, 292.0, 900.0, 8.0, 3.0
        rr = skia.RRect.MakeRectXY(skia.Rect(bx, by, bx + bw, by + bh), bh / 2, bh / 2)
        c.save()
        c.clipRRect(rr, True)
        x = bx
        for i in range(n_t):
            w = tl.bar[f][i] * bw
            if w > 0.5:
                c.drawRect(skia.Rect(x, by, x + max(0.0, w - gap), by + bh),
                           skia.Paint(Color=rgba(self.teams[i].color, k)))
            x += w
        c.restore()

        # Riga sotto la barra: leader a sinistra, squadre rimaste a destra.
        y = 346
        lead = rec.winner if won else int(tl.leader[f])
        team = self.teams[lead]
        ft = gfx.text(28)
        label = "Winner  " if won else "Leader  "
        draw_text(c, label, ft, bx, y, color=INK, alpha=0.5 * k, align="left")
        x = bx + ft.measureText(label)
        draw_text(c, team.name, gfx.title(28), x, y, color=team.color, alpha=k, align="left")
        x += gfx.title(28).measureText(team.name)
        draw_text(c, f"  {counts[lead]}", ft, x, y, color=INK, alpha=0.7 * k, align="left")
        left = int((counts > 0).sum())
        draw_text(c, f"{left} of {n_t} left", ft, bx + bw, y, color=INK, alpha=0.5 * k, align="right")

        if won:
            return
        # Didascalie evento.
        for v0, label in tl.captions:
            a = fade(vt - v0, 0.35, 1.6, 0.5)
            if a > 0:
                draw_text(c, label, gfx.text(28), W / 2, 462, color=INK, alpha=0.8 * a, tracking=7)
        # Notizie sulle squadre: si vede solo l'ultima.
        shown = [n for n in tl.news if 0 <= vt - n[0] < 1.9]
        if shown:
            v0, t_i, what = shown[-1]
            a = fade(vt - v0, 0.25, 1.25, 0.4)
            team = self.teams[t_i]
            fn, fw = gfx.title(30), gfx.text(30)
            w = fn.measureText(team.name + " ") + fw.measureText(what)
            x = W / 2 - w / 2
            draw_text(c, team.name + " ", fn, x, 518, color=team.color, alpha=a, align="left")
            draw_text(c, what, fw, x + fn.measureText(team.name + " "), 518, color=INK, alpha=0.7 * a,
                      align="left")

    def _winner(self, c, a):
        team = self.teams[self.rec.winner]
        col = team.color
        c.drawRect(skia.Rect(0, WORLD_TOP, W, H), skia.Paint(Color=rgba(BG, 0.72 * ease_in_out(a / 1.0))))

        def item(delay):
            k = ease_out((a - 0.3 - delay) / 0.8)
            return k, (1 - k) * 14

        k, dy = item(0.0)
        if k > 0:
            c.drawCircle(W / 2, 900 + dy, 66, skia.Paint(AntiAlias=True, Color=rgba(col, k)))
            self._glyph(c, self.rec.winner, W / 2, 900 + dy, col, k, scale=66 / BALL_R)
        k, dy = item(0.15)
        if k > 0:
            f = gfx.fit_font(gfx.title, team.name, 960, 92)
            draw_text(c, team.name, f, W / 2, 1080 + dy, color=col, alpha=k)
            draw_text(c, "wins", gfx.text(40), W / 2, 1140 + dy, color=INK, alpha=0.7 * k)
        k, dy = item(1.4)
        if k > 0:
            draw_text(c, "Comment who plays next", gfx.text(30), W / 2, 1380 + dy, color=INK, alpha=0.55 * k)
