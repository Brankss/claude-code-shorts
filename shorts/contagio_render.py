"""Render di Contagio: timeline (slow-mo sul colpo finale), arena, HUD, festa."""

import math

import numpy as np
import skia

from . import gfx
from .contagio import ARENA_R, BALL_R, CENTER, ESCAPING, GONE, H, IN_PLAY, W
from .gfx import WHITE, BLACK, draw_text, ease_in_out, ease_out, ease_out_back, mix, rgba

FPS = 60
TOTAL = 40.0
PRE, POST, SLOW, CELEB_RATE = 0.55, 0.25, 0.3, 0.7
LOOP_FADE = 0.45
HOOK_END = 1.25
WORLD_TOP = 404

BANNER_STYLE = {
    "speed": ((255, 214, 10), None),
    "gravity": ((90, 200, 250), None),
    "gap": ((255, 69, 58), None),
    "duel": (WHITE, None),
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
        self.sim_t = sims
        self.n_frames = n
        max_s = (len(rec.counts) - 2) * rec.dt
        self.sim_t = np.minimum(self.sim_t, max_s)

        self.vt_win = self.vt(t_end)
        self.vt_slow = self.vt(a1)

        # Banner: eventi programmati + duello, mai sovrapposti.
        self.banners = []
        last_end = -1.0
        for et, kind, label in rec.events:
            if et > t_end:
                continue
            v = max(self.vt(et), last_end + 0.1)
            extra = None
            if kind == "duel":
                c = rec.counts[min(int(et / rec.dt) + 1, len(rec.counts) - 1)]
                extra = [int(x) for x in np.nonzero(c)[0]]
            self.banners.append((v, kind, label, extra))
            last_end = v + 1.3

        # Toast: eliminazioni + "LAST BALL" quando restano poche squadre.
        self.toasts = []
        for et, team, x, y in rec.eliminations:
            if et < t_end:
                self.toasts.append((self.vt(et), team, "IS OUT!"))
        counts = rec.counts
        end_step = int(t_end / rec.dt)
        alive = (counts[:end_step] > 0).sum(axis=1)
        warned = set()
        for team in range(len(self.teams)):
            c = counts[:end_step, team]
            hits = np.nonzero((c[1:] == 1) & (c[:-1] > 1) & (alive[1:] <= 3))[0]
            for h in hits:
                if team not in warned:
                    warned.add(team)
                    self.toasts.append((self.vt((h + 1) * rec.dt), team, "LAST BALL!"))
        self.toasts.sort()

        # Scossoni.
        self.shakes = [(self.vt(e[0]), 9.0) for e in rec.eliminations if e[0] < t_end]
        self.shakes += [(b[0], 14.0) for b in self.banners]
        self.shakes.append((self.vt_win, 26.0))

        # Barra e leader precalcolati per frame (con smoothing).
        n_t = len(self.teams)
        self.bar = np.zeros((n, n_t))
        self.leader = np.zeros(n, int)
        cur = counts[0] / counts[0].sum()
        lead = int(np.argmax(counts[0]))
        for f in range(n):
            c = counts[self.step(f)]
            tot = max(1, c.sum())
            cur = cur + (c / tot - cur) * 0.2
            self.bar[f] = cur
            top = int(np.argmax(c))
            if c[top] > c[lead]:
                lead = top
            self.leader[f] = lead

        # Conversioni in array per lookup veloce.
        conv = np.array(rec.conversions) if rec.conversions else np.zeros((0, 6))
        self.conv_t = conv[:, 0]
        self.conv = conv
        esc = np.array(rec.escapes) if rec.escapes else np.zeros((0, 5))
        self.esc_t = esc[:, 0]
        self.esc = esc

    def vt(self, sim_t):
        return int(np.searchsorted(self.sim_t, sim_t)) / FPS

    def step(self, f):
        return min(int(self.sim_t[f] / self.rec.dt), len(self.rec.counts) - 1)


class Renderer:
    def __init__(self, tl, theme):
        self.tl = tl
        self.rec = tl.rec
        self.theme = theme
        self.teams = theme["teams"]
        self.buf = np.zeros((H, W, 4), np.uint8)
        self.surface = skia.Surface(self.buf)
        self.bg = self._make_background()
        self.sprites = [self._make_sprite(t) for t in self.teams]
        self.frame0 = None
        rng = np.random.default_rng(self.rec.seed + 7)
        self.confetti = rng.random((170, 7))

    # ---------- asset pre-renderizzati ----------

    def _make_background(self):
        surf = skia.Surface(W, H)
        c = surf.getCanvas()
        p = skia.Paint(Shader=skia.GradientShader.MakeLinear(
            [skia.Point(0, 0), skia.Point(0, H)],
            [rgba((8, 9, 18)), rgba((14, 16, 34)), rgba((8, 9, 18))], [0, 0.55, 1]))
        c.drawRect(skia.Rect(0, 0, W, H), p)
        glow = skia.Paint(Shader=skia.GradientShader.MakeRadial(
            skia.Point(*CENTER), 760, [rgba((60, 70, 170), 0.35), rgba((60, 70, 170), 0.0)]))
        c.drawRect(skia.Rect(0, 0, W, H), glow)
        dot = skia.Paint(AntiAlias=True, Color=rgba(WHITE, 0.045))
        for y in range(20, H, 44):
            for x in range(20, W, 44):
                c.drawCircle(x, y, 1.6, dot)
        return surf.makeImageSnapshot()

    def _make_sprite(self, team):
        s = 3  # super-sampling per restare nitidi durante pop e zoom
        pad = 16
        size = int((BALL_R + pad) * 2 * s)
        surf = skia.Surface(size, size)
        c = surf.getCanvas()
        c.scale(s, s)
        cx = cy = BALL_R + pad
        col = team.color
        glow = skia.Paint(AntiAlias=True, Color=rgba(col, 0.55),
                          MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 7))
        c.drawCircle(cx, cy, BALL_R * 0.95, glow)
        shader = skia.GradientShader.MakeRadial(
            skia.Point(cx - BALL_R * 0.35, cy - BALL_R * 0.45), BALL_R * 1.55,
            [rgba(mix(col, WHITE, 0.45)), rgba(col), rgba(mix(col, BLACK, 0.35))], [0, 0.45, 1])
        c.drawCircle(cx, cy, BALL_R, skia.Paint(AntiAlias=True, Shader=shader))
        c.drawCircle(cx, cy, BALL_R - 1.5, skia.Paint(
            AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.2, Color=rgba(WHITE, 0.35)))
        f = gfx.glyph(BALL_R * 1.2)
        draw_text(c, team.glyph, f, cx + 1.5, cy + 2.5, color=BLACK, alpha=0.35, vcenter=True)
        draw_text(c, team.glyph, f, cx, cy, color=WHITE, vcenter=True)
        return surf.makeImageSnapshot()

    # ---------- frame ----------

    def render(self, f):
        tl, rec = self.tl, self.rec
        c = self.surface.getCanvas()
        vt = f / FPS
        s = tl.sim_t[f]
        c.drawImage(self.bg, 0, 0)

        if vt >= tl.vt_win:
            k = ease_out((vt - tl.vt_win) / 0.6)
            col = self.teams[rec.winner].color
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
                skia.Point(*CENTER), 900, [rgba(col, 0.33 * k), rgba(col, 0.0)])))

        c.save()
        c.clipRect(skia.Rect(0, WORLD_TOP, W, H))
        self._camera(c, vt)
        self._arena(c, f, s)
        self._effects(c, s)
        self._balls(c, f, s)
        c.restore()

        self._hud(c, f, vt)
        self._banners(c, vt)
        self._toasts(c, vt)
        if vt >= tl.vt_win:
            self._winner(c, vt - tl.vt_win)
        self._hook(c, vt)

        if self.frame0 is not None and vt > TOTAL - LOOP_FADE:
            k = ease_in_out((vt - (TOTAL - LOOP_FADE)) / LOOP_FADE)
            c.drawImage(self.frame0, 0, 0, skia.SamplingOptions(), skia.Paint(Alphaf=k))
        if f == 0:
            self.frame0 = skia.Image.fromarray(self.buf.copy())
        return self.buf

    def _camera(self, c, vt):
        tl, rec = self.tl, self.rec
        z, focus = 1.0, CENTER.copy()
        _, hx, hy = rec.final_hit
        if vt >= tl.vt_slow - 0.25:
            zin = ease_in_out((vt - (tl.vt_slow - 0.25)) / 0.9)
            zout = ease_in_out((vt - (tl.vt_win + 0.45)) / 0.9)
            k = zin * (1 - zout)
            z = 1.0 + 0.4 * k
            focus = CENTER + (np.array([hx, hy]) - CENTER) * 0.55 * k
        ox, oy = 0.0, 0.0
        for t0, amp in tl.shakes:
            a = vt - t0
            if 0 <= a < 0.5:
                e = amp * math.exp(-a / 0.11)
                ox += e * math.sin(a * 83 + t0)
                oy += e * math.cos(a * 71 + t0 * 2)
        c.translate(CENTER[0] + ox, CENTER[1] + oy)
        c.scale(z, z)
        c.translate(-focus[0], -focus[1])

    def _arena(self, c, f, s):
        rec = self.rec
        st = min(int(s / rec.dt), len(rec.gap) - 1)
        gap_c, gap_h = rec.gap[st]
        cx, cy = CENTER
        fill = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
            skia.Point(cx, cy), ARENA_R, [rgba((22, 26, 58)), rgba((13, 15, 34))]))
        c.drawCircle(cx, cy, ARENA_R, fill)

        rect = skia.Rect.MakeLTRB(cx - ARENA_R, cy - ARENA_R, cx + ARENA_R, cy + ARENA_R)
        start = math.degrees(gap_c + gap_h)
        sweep = 360 - math.degrees(2 * gap_h)
        glow = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=14,
                          Color=rgba(WHITE, 0.35), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9))
        ring = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=7,
                          Color=rgba(WHITE, 0.95), StrokeCap=skia.Paint.kRound_Cap)
        if gap_h > 0.001:
            c.drawArc(rect, start, sweep, False, glow)
            c.drawArc(rect, start, sweep, False, ring)
            danger = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=9,
                                Color=rgba((255, 69, 58)), StrokeCap=skia.Paint.kRound_Cap)
            dglow = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=22,
                               Color=rgba((255, 69, 58), 0.6),
                               MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
            for a0 in (start, start + sweep - 14):
                c.drawArc(rect, a0, 14, False, dglow)
                c.drawArc(rect, a0, 14, False, danger)
        else:
            c.drawCircle(cx, cy, ARENA_R, glow)
            c.drawCircle(cx, cy, ARENA_R, ring)

    def _effects(self, c, s):
        """Onde d'urto e particelle delle conversioni recenti (in tempo simulazione)."""
        tl = self.tl
        lo = np.searchsorted(tl.conv_t, s - 0.45)
        hi = np.searchsorted(tl.conv_t, s, side="right")
        for k in range(lo, hi):
            t0, x, y, wt, lt, ball = tl.conv[k]
            age = s - t0
            col = self.teams[int(wt)].color
            kk = age / 0.35
            if kk < 1:
                r = BALL_R * (1.0 + 1.6 * ease_out(kk))
                c.drawCircle(x, y, r, skia.Paint(
                    AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=6 * (1 - kk) + 1,
                    Color=rgba(col, 0.9 * (1 - kk))))
            rng = np.random.default_rng(int(t0 * 1000) + int(ball))
            ang = rng.uniform(0, 2 * np.pi, 7)
            spd = rng.uniform(220, 520, 7)
            d = (1 - math.exp(-age * 6)) / 6
            a = max(0.0, 1 - age / 0.45)
            p = skia.Paint(AntiAlias=True, Color=rgba(mix(col, WHITE, 0.3), a))
            for q in range(7):
                c.drawCircle(x + math.cos(ang[q]) * spd[q] * d, y + math.sin(ang[q]) * spd[q] * d,
                             5.0 * a + 1, p)

    def _balls(self, c, f, s):
        rec, tl = self.rec, self.tl
        i0 = min(int(s / rec.dt), len(rec.pos) - 2)
        fr = min(1.0, s / rec.dt - i0)
        pos = rec.pos[i0] * (1 - fr) + rec.pos[i0 + 1] * fr
        team = rec.team[i0 + (1 if fr > 0.5 else 0)]
        state = rec.state[i0]

        # Pop delle palline appena convertite.
        pop = {}
        lo = np.searchsorted(tl.conv_t, s - 0.3)
        hi = np.searchsorted(tl.conv_t, s, side="right")
        for k in range(lo, hi):
            pop[int(tl.conv[k][5])] = s - tl.conv[k][0]

        sampling = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
        half = self.sprites[0].width() / 3 / 2
        for b in range(len(pos)):
            if state[b] == GONE:
                continue
            x, y = pos[b]
            alpha = 1.0
            if state[b] == ESCAPING:
                out = math.hypot(x - CENTER[0], y - CENTER[1]) - ARENA_R
                alpha = max(0.0, 1 - out / 380)
                if alpha <= 0:
                    continue
            sc = 1.0
            if b in pop:
                a = pop[b]
                sc = 1 + 0.45 * math.exp(-a / 0.07) * math.cos(a * 30)
            hs = half * sc
            paint = skia.Paint(Alphaf=alpha)
            c.drawImageRect(self.sprites[int(team[b])], skia.Rect(x - hs, y - hs, x + hs, y + hs),
                            sampling, paint)
            if b in pop and pop[b] < 0.15:
                c.drawCircle(x, y, BALL_R * sc, skia.Paint(
                    AntiAlias=True, Color=rgba(WHITE, 0.85 * (1 - pop[b] / 0.15))))

    # ---------- HUD ----------

    def _hud(self, c, f, vt):
        tl, rec = self.tl, self.rec
        st = tl.step(f)
        counts = rec.counts[st]
        won = vt >= tl.vt_win
        n_t = len(self.teams)

        # Titolo piccolo (dopo l'hook).
        k = ease_in_out((vt - (HOOK_END - 0.35)) / 0.35)
        if k > 0:
            title = " ".join(self.theme["title"])
            draw_text(c, title, gfx.display(78), W / 2, 196, alpha=k,
                      stroke=BLACK, stroke_w=8, stroke_alpha=0.6)
            draw_text(c, self.theme["subtitle"], gfx.label(29), W / 2, 246,
                      color=(255, 214, 10), alpha=k * 0.95)

        # Riga leader.
        y = 318
        lead = rec.winner if won else int(tl.leader[f])
        team = self.teams[lead]
        draw_text(c, "WINNER" if won else "LEADER", gfx.label(24), 64, y + 9, alpha=0.6, align="left")
        lx = 64 + gfx.label(24).measureText("WINNER" if won else "LEADER") + 18
        self._chip(c, lx + 22, y, 22, team)
        draw_text(c, team.name, gfx.display(46), lx + 56, y + 17, color=team.color, align="left")
        nw = gfx.display(46).measureText(team.name)
        draw_text(c, f"×{counts[lead]}", gfx.display(46), lx + 66 + nw, y + 17, align="left")
        left = int((counts > 0).sum())
        draw_text(c, f"{left}/{n_t}", gfx.display(46), W - 64, y + 17, align="right")
        draw_text(c, "SIGNS LEFT", gfx.label(24), W - 64 - gfx.display(46).measureText(f"{left}/{n_t}") - 14,
                  y + 9, alpha=0.6, align="right")

        # Barra impilata.
        bx, by, bw, bh = 60.0, 352.0, 960.0, 44.0
        rr = skia.RRect.MakeRectXY(skia.Rect(bx, by, bx + bw, by + bh), bh / 2, bh / 2)
        c.drawRRect(rr, skia.Paint(AntiAlias=True, Color=rgba((27, 31, 58))))
        c.save()
        c.clipRRect(rr, True)
        x = bx
        fracs = tl.bar[f]
        fg = gfx.glyph(26)
        for i in range(n_t):
            w = fracs[i] * bw
            if w <= 0.3:
                continue
            col = self.teams[i].color
            c.drawRect(skia.Rect(x, by, x + w + 0.5, by + bh), skia.Paint(Color=rgba(col)))
            if w > 38:
                draw_text(c, self.teams[i].glyph, fg, x + w / 2, by + bh / 2, alpha=0.95, vcenter=True)
            x += w
        c.restore()
        c.drawRRect(rr, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2,
                                   Color=rgba(WHITE, 0.25)))

    def _chip(self, c, x, y, r, team, alpha=1.0):
        c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color=rgba(team.color, alpha)))
        draw_text(c, team.glyph, gfx.glyph(r * 1.15), x, y, alpha=alpha, vcenter=True)

    def _banners(self, c, vt):
        for v0, kind, label, extra in self.tl.banners:
            a = vt - v0
            if not 0 <= a < 1.3:
                continue
            color = BANNER_STYLE.get(kind, (WHITE, None))[0]
            if a < 0.3:
                sc = ease_out_back(a / 0.3) * 0.7 + 0.3
                al = min(1.0, a / 0.08)
            elif a > 1.05:
                k = (a - 1.05) / 0.25
                sc, al = 1 + 0.25 * k, 1 - k
            else:
                sc, al = 1.0, 1.0
            cy = CENTER[1]
            c.save()
            c.translate(W / 2, cy)
            c.rotate(-5)
            band_h = 200 if kind != "duel" else 290
            c.drawRect(skia.Rect(-W, -band_h / 2, W, band_h / 2),
                       skia.Paint(Color=rgba(BLACK, 0.55 * al)))
            c.drawRect(skia.Rect(-W, -band_h / 2, W, -band_h / 2 + 6), skia.Paint(Color=rgba(color, al)))
            c.drawRect(skia.Rect(-W, band_h / 2 - 6, W, band_h / 2), skia.Paint(Color=rgba(color, al)))
            c.scale(sc, sc)
            if kind == "duel" and extra and len(extra) == 2:
                draw_text(c, label, gfx.display(110), 0, -48, color=color, alpha=al, vcenter=True,
                          stroke=BLACK, stroke_w=12, stroke_alpha=0.8)
                t1, t2 = self.teams[extra[0]], self.teams[extra[1]]
                f = gfx.display(64)
                vs = "  VS  "
                w1, wv, w2 = f.measureText(t1.name), f.measureText(vs), f.measureText(t2.name)
                x0 = -(w1 + wv + w2 + 96) / 2
                self._chip(c, x0 + 22, 72, 24, t1, al)
                draw_text(c, t1.name, f, x0 + 52, 72, color=t1.color, alpha=al, align="left", vcenter=True)
                draw_text(c, vs, f, x0 + 52 + w1, 72, alpha=al, align="left", vcenter=True)
                x2 = x0 + 52 + w1 + wv
                self._chip(c, x2 + 22, 72, 24, t2, al)
                draw_text(c, t2.name, f, x2 + 52, 72, color=t2.color, alpha=al, align="left", vcenter=True)
            else:
                f = gfx.fit_font(gfx.display, label, 960, 150)
                draw_text(c, label, f, 0, 0, color=color, alpha=al, vcenter=True,
                          stroke=BLACK, stroke_w=14, stroke_alpha=0.8)
            c.restore()

    def _toasts(self, c, vt):
        active = [t for t in self.tl.toasts if 0 <= vt - t[0] < 1.7 and t[0] < self.tl.vt_win]
        active.sort(key=lambda t: -t[0])
        for i, (v0, team_i, text) in enumerate(active[:2]):
            a = vt - v0
            team = self.teams[team_i]
            al = min(1.0, a / 0.12) * (1 - max(0.0, (a - 1.4) / 0.3))
            dy = (1 - ease_out(a / 0.2)) * -30
            y = 452 + i * 78 + dy
            f = gfx.display(40)
            txt = f"{team.name} {text}"
            w = f.measureText(txt) + 100
            rr = skia.RRect.MakeRectXY(skia.Rect(W / 2 - w / 2, y - 32, W / 2 + w / 2, y + 32), 32, 32)
            c.drawRRect(rr, skia.Paint(AntiAlias=True, Color=rgba((18, 20, 40), 0.92 * al)))
            c.drawRRect(rr, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3,
                                       Color=rgba(team.color, al)))
            self._chip(c, W / 2 - w / 2 + 34, y, 22, team, al)
            col = (255, 69, 58) if text == "IS OUT!" else (255, 214, 10)
            draw_text(c, team.name, f, W / 2 - w / 2 + 68, y, color=team.color, alpha=al,
                      align="left", vcenter=True)
            draw_text(c, text, f, W / 2 - w / 2 + 68 + f.measureText(team.name + " "), y,
                      color=col, alpha=al, align="left", vcenter=True)

    def _hook(self, c, vt):
        """Titolo gigante sui primi frame, poi vola nell'header."""
        if vt >= HOOK_END:
            return
        k = ease_in_out((vt - (HOOK_END - 0.35)) / 0.35)
        al = 1 - k
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=rgba(BLACK, 0.45 * al)))
        l1, l2 = self.theme["title"]
        y = CENTER[1] - 60 - (CENTER[1] - 200) * k
        sc = 1 - 0.45 * k
        c.save()
        c.translate(W / 2, y)
        c.scale(sc, sc)
        pulse = 1 + 0.03 * math.sin(vt * 12)
        c.scale(pulse, pulse)
        draw_text(c, l1, gfx.fit_font(gfx.display, l1, 1000, 170), 0, -30, alpha=al,
                  stroke=BLACK, stroke_w=16, stroke_alpha=0.85)
        draw_text(c, l2, gfx.fit_font(gfx.display, l2, 1000, 170), 0, 150, color=(255, 214, 10),
                  alpha=al, stroke=BLACK, stroke_w=16, stroke_alpha=0.85)
        self._pill(c, self.theme["subtitle"], gfx.label(36), 0, 262, (255, 214, 10), BLACK, al)
        c.restore()

    def _winner(self, c, a):
        team = self.teams[self.rec.winner]
        col = team.color
        if a < 0.35:
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=rgba(WHITE, 0.75 * (1 - a / 0.35))))
        if a < 0.25:
            return
        b = a - 0.25
        c.drawRect(skia.Rect(0, WORLD_TOP, W, H), skia.Paint(Color=rgba(BLACK, 0.5 * ease_out(b / 0.5))))
        # Coriandoli.
        g = 900.0
        for q in self.confetti:
            x0, y0, vy, sway, rot, size, ci = q
            yy = -40 - y0 * 500 + (300 + vy * 500) * b + 0.5 * g * 0.15 * b * b
            if yy > H + 40:
                continue
            xx = x0 * W + math.sin(b * (2 + sway * 3) + x0 * 20) * 40
            pc = [col, WHITE, mix(col, WHITE, 0.5), (255, 214, 10)][int(ci * 4)]
            c.save()
            c.translate(xx, yy)
            c.rotate(math.degrees(b * (3 + rot * 8) + x0 * 10))
            sw = 10 + size * 10
            c.drawRect(skia.Rect(-sw / 2, -4 - size * 3, sw / 2, 4 + size * 3), skia.Paint(Color=rgba(pc, 0.95)))
            c.restore()
        if b < 0.1:
            return
        d = b - 0.1
        sc = ease_out_back(d / 0.45)
        cy = 880
        c.save()
        c.translate(W / 2, cy)
        c.scale(sc, sc)
        c.drawCircle(0, 0, 150, skia.Paint(AntiAlias=True, Color=rgba(col, 0.6),
                                           MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30)))
        spr = self.sprites[self.rec.winner]
        hs = spr.width() / 3 / 2 * (140 / BALL_R)
        c.drawImageRect(spr, skia.Rect(-hs, -hs, hs, hs),
                        skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
        c.restore()
        k2 = ease_out_back((d - 0.15) / 0.4)
        if k2 > 0:
            c.save()
            c.translate(W / 2, 1150)
            c.scale(k2, k2)
            f = gfx.fit_font(gfx.display, team.name, 980, 190)
            draw_text(c, team.name, f, 0, 0, color=col, vcenter=True, stroke=BLACK, stroke_w=16, stroke_alpha=0.9)
            draw_text(c, "WINS!", gfx.display(120), 0, 150, vcenter=True, stroke=BLACK, stroke_w=12,
                      stroke_alpha=0.9)
            c.restore()
        k3 = ease_out((d - 1.6) / 0.4)
        if k3 > 0:
            self._pill(c, "COMMENT WHO FIGHTS NEXT", gfx.label(40), W / 2, 1400, (255, 214, 10), BLACK, k3)

    def _pill(self, c, text, font, x, y, bg, fg, alpha):
        w = font.measureText(text) + 56
        rr = skia.RRect.MakeRectXY(skia.Rect(x - w / 2, y - 34, x + w / 2, y + 34), 34, 34)
        c.drawRRect(rr, skia.Paint(AntiAlias=True, Color=rgba(bg, alpha)))
        draw_text(c, text, font, x, y, color=fg, alpha=alpha, vcenter=True)
