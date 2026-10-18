"""Stickman in stile "14 Floors Up": corpo a tratti spessi color crema con contorno scuro, testa tonda.

Una posa è un dizionario di angoli in gradi. Arti: 0 = dritto verso il basso, positivo = in avanti
(verso +x quando il personaggio guarda a destra). Busto: 0 = dritto in piedi, positivo = piegato in avanti.
Gomiti e ginocchia sono relativi al segmento sopra. Le pose si mescolano con `blend` e si animano nel tempo.

    fig = Figure(height=520)
    fig.draw(c, x, y_piedi, pose=POSES["stand"], facing=1)
"""

import math
from dataclasses import dataclass, field

import skia

from .gfx import mix, rgba

CREAM = (233, 224, 205)
INK = (44, 36, 32)

POSES = {
    "stand": dict(torso=0, head=0, lsh=6, lel=4, rsh=-6, rel=-4, lhip=4, lkn=0, rhip=-4, rkn=0),
    "stand_tense": dict(torso=-3, head=-4, lsh=14, lel=40, rsh=8, rel=50, lhip=8, lkn=0, rhip=-8, rkn=0),
    "reach_up": dict(torso=-4, head=-12, lsh=8, lel=4, rsh=150, rel=10, lhip=4, lkn=0, rhip=-4, rkn=0),
    "point": dict(torso=0, head=-4, lsh=6, lel=4, rsh=95, rel=0, lhip=4, lkn=0, rhip=-4, rkn=0),
    "hold_phone": dict(torso=8, head=22, lsh=30, lel=95, rsh=24, rel=100, lhip=4, lkn=0, rhip=-4, rkn=0),
    "push": dict(torso=28, head=-18, lsh=80, lel=10, rsh=88, rel=6, lhip=-22, lkn=8, rhip=24, rkn=6),
    "lean_door": dict(torso=14, head=-6, lsh=70, lel=40, rsh=40, rel=60, lhip=6, lkn=4, rhip=-8, rkn=0),
    "sit_floor": dict(torso=-12, head=-6, lsh=40, lel=60, rsh=46, rel=56, lhip=96, lkn=-120, rhip=82, rkn=-112),
    "hug_knees": dict(torso=18, head=10, lsh=70, lel=60, rsh=74, rel=56, lhip=118, lkn=-150, rhip=110, rkn=-146),
    "sit_chair": dict(torso=-2, head=0, lsh=20, lel=50, rsh=26, rel=46, lhip=90, lkn=-90, rhip=86, rkn=-86),
    "lie": dict(torso=-90, head=0, lsh=-10, lel=0, rsh=-6, rel=0, lhip=-90, lkn=0, rhip=-88, rkn=0),
    "sit_up_bed": dict(torso=-8, head=-4, lsh=-20, lel=10, rsh=-30, rel=20, lhip=90, lkn=0, rhip=88, rkn=0),
    "crouch": dict(torso=40, head=-30, lsh=60, lel=30, rsh=70, rel=20, lhip=110, lkn=-120, rhip=70, rkn=-110),
    "crawl": dict(torso=76, head=-62, lsh=-66, lel=0, rsh=-84, rel=0, lhip=6, lkn=-88, rhip=-6, rkn=-84),
    "plead": dict(torso=6, head=-4, lsh=60, lel=70, rsh=50, rel=80, lhip=4, lkn=0, rhip=-4, rkn=0),
    "hold_arm": dict(torso=8, head=8, lsh=20, lel=110, rsh=10, rel=30, lhip=4, lkn=0, rhip=-4, rkn=0),
    "shush": dict(torso=2, head=4, lsh=20, lel=100, rsh=14, rel=150, lhip=4, lkn=0, rhip=-4, rkn=0),
    "text": dict(torso=10, head=26, lsh=34, lel=100, rsh=28, rel=104, lhip=4, lkn=0, rhip=-4, rkn=0),
    "reach_low": dict(torso=55, head=-20, lsh=70, lel=10, rsh=60, rel=20, lhip=-30, lkn=60, rhip=20, rkn=40),
    "kneel": dict(torso=20, head=-6, lsh=50, lel=30, rsh=70, rel=10, lhip=95, lkn=-95, rhip=0, rkn=-90),
    "flashlight": dict(torso=4, head=-4, lsh=10, lel=10, rsh=88, rel=4, lhip=6, lkn=0, rhip=-6, rkn=0),
    "wave": dict(torso=0, head=-6, lsh=6, lel=4, rsh=150, rel=-30, lhip=4, lkn=0, rhip=-4, rkn=0),
    "listen": dict(torso=-4, head=-38, lsh=4, lel=2, rsh=-4, rel=-2, lhip=3, lkn=0, rhip=-3, rkn=0),
    "sit_couch": dict(torso=-6, head=8, lsh=30, lel=96, rsh=26, rel=100, lhip=92, lkn=-88, rhip=86, rkn=-84),
    "sit_shush": dict(torso=-4, head=4, lsh=34, lel=96, rsh=14, rel=150, lhip=92, lkn=-88, rhip=86, rkn=-84),
    "sit_watch": dict(torso=8, head=-2, lsh=40, lel=60, rsh=46, rel=56, lhip=92, lkn=-90, rhip=86, rkn=-86),
    "kneel_reach": dict(torso=38, head=-14, lsh=88, lel=8, rsh=74, rel=14, lhip=95, lkn=-95, rhip=10, rkn=-96),
    "cover": dict(torso=-4, head=-14, lsh=150, lel=10, rsh=162, rel=-6, lhip=6, lkn=0, rhip=-6, rkn=0),
    "knock": dict(torso=4, head=-4, lsh=6, lel=4, rsh=80, rel=70, lhip=4, lkn=0, rhip=-4, rkn=0),
}


def blend(a, b, k):
    return {key: a[key] + (b[key] - a[key]) * k for key in a}


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def walk(phase, speed=1.0):
    """Ciclo di camminata (phase in giri)."""
    s = math.sin(phase * 2 * math.pi)
    c = math.cos(phase * 2 * math.pi)
    amp = 24 * speed
    return dict(torso=4 * speed, head=-2, lsh=-s * 18 * speed, lel=8 + max(0, s) * 18, rsh=s * 18 * speed,
                rel=8 + max(0, -s) * 18, lhip=s * amp, lkn=-max(0, -c) * 40 * speed, rhip=-s * amp,
                rkn=-max(0, c) * 40 * speed)


def breathe(pose, t, amount=1.0):
    """Respiro e micro-movimenti: nessuna posa resta perfettamente ferma."""
    p = dict(pose)
    p["torso"] += math.sin(t * 1.7) * 1.2 * amount
    p["head"] += math.sin(t * 1.3 + 1) * 1.5 * amount
    p["lsh"] += math.sin(t * 1.1) * 1.5 * amount
    p["rsh"] += math.sin(t * 1.2 + 2) * 1.5 * amount
    return p


@dataclass
class Figure:
    height: float = 500.0          # dai piedi alla cima della testa, in piedi
    fill: tuple = CREAM
    ink: tuple = INK
    face: str = None               # None (il protagonista non ha faccia), "glasses", "plain", "worried"
    extras: list = field(default_factory=list)   # "mustache", "red_sleeve", "hat", "backpack", "scarf"
    shade: float = 0.0             # 0..1 quanto è in ombra (luce bassa)
    coat: tuple = None             # colore dell'impermeabile col cappuccio (es. giallo), None = niente

    def joints(self, x, y, pose, facing=1):
        """Posizioni (px) di tutte le articolazioni; (x, y) = anca."""
        H = self.height
        th, sh_, ua, fa = 0.24 * H, 0.23 * H, 0.17 * H, 0.16 * H
        tl, r = 0.30 * H, 0.105 * H

        def d(a):
            a = math.radians(a)
            return math.sin(a) * facing, math.cos(a)

        hip = (x, y)
        ta = math.radians(pose["torso"])
        up = (math.sin(ta) * facing, -math.cos(ta))
        neck = (x + up[0] * tl, y + up[1] * tl)
        sho = (x + up[0] * (tl - 0.04 * H), y + up[1] * (tl - 0.04 * H))
        ha = math.radians(pose["torso"] + pose["head"])
        head = (neck[0] + math.sin(ha) * facing * (r + 0.015 * H), neck[1] - math.cos(ha) * (r + 0.015 * H))
        J = {"hip": hip, "neck": neck, "head": head, "sho": sho, "r": r}
        for s in ("l", "r"):
            a1 = pose[s + "sh"] + pose["torso"]
            e = (sho[0] + d(a1)[0] * ua, sho[1] + d(a1)[1] * ua)
            a2 = a1 + pose[s + "el"]
            h = (e[0] + d(a2)[0] * fa, e[1] + d(a2)[1] * fa)
            J[s + "elb"], J[s + "hand"] = e, h
            b1 = pose[s + "hip"]
            k = (hip[0] + d(b1)[0] * th, hip[1] + d(b1)[1] * th)
            b2 = b1 + pose[s + "kn"]
            f = (k[0] + d(b2)[0] * sh_, k[1] + d(b2)[1] * sh_)
            J[s + "knee"], J[s + "foot"] = k, f
        return J

    def hip_for_feet(self, x, y_feet, pose):
        """Anca tale che il piede più basso tocchi y_feet."""
        J = self.joints(0, 0, pose)
        low = max(J["lfoot"][1], J["rfoot"][1], J["lknee"][1], J["rknee"][1])
        return x, y_feet - low - self.height * 0.025

    def draw(self, c, x, y, pose, facing=1, alpha=1.0, feet=True):
        """Disegna con i piedi a y (feet=True) o con l'anca in (x, y)."""
        if feet:
            x, y = self.hip_for_feet(x, y, pose)
        J = self.joints(x, y, pose, facing)
        H = self.height
        w = 0.058 * H
        o = 0.022 * H
        fill = mix(self.fill, (20, 22, 30), self.shade * 0.6)
        far = mix(fill, (0, 0, 0), 0.12)
        ink = self.ink

        def limb(pts, col, width):
            p = skia.Path()
            p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width + 2 * o,
                                     StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                                     Color=rgba(ink, alpha)))
            c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                                     StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                                     Color=rgba(col, alpha)))

        if "backpack" in self.extras:
            bx, by = J["sho"]
            back = -facing
            c.drawRoundRect(skia.Rect(bx + back * 0.06 * H - 0.07 * H, by, bx + back * 0.06 * H + 0.07 * H, by + 0.2 * H),
                            0.03 * H, 0.03 * H, skia.Paint(AntiAlias=True, Color=rgba(mix((90, 70, 50), (0, 0, 0), self.shade), alpha)))
        limb([J["sho"], J["lelb"], J["lhand"]], far, w)
        limb([J["hip"], J["lknee"], J["lfoot"]], far, w)
        limb([J["hip"], J["neck"]], fill, w * 1.05)
        limb([J["hip"], J["rknee"], J["rfoot"]], fill, w)
        limb([J["sho"], J["relb"], J["rhand"]], fill, w)
        if "red_sleeve" in self.extras:
            red = mix((190, 30, 34), (40, 0, 0), self.shade * 0.5)
            for s in ("l", "r") if "both_sleeves" in self.extras else ("r",):
                p = skia.Path()
                p.moveTo(*J[s + "elb"])
                p.lineTo(*J[s + "hand"])
                c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w * 1.25,
                                         StrokeCap=skia.Paint.kRound_Cap, Color=rgba(red, alpha)))
        hx, hy = J["head"]
        r = J["r"]
        if self.coat:
            # impermeabile: trapezio dalle spalle alle ginocchia, maniche, cappuccio attorno alla testa
            coat = mix(self.coat, (20, 22, 30), self.shade * 0.6)
            sx, sy = J["sho"]
            hx0, hy0 = J["hip"]
            low = (J["lknee"][1] + J["rknee"][1]) / 2 * 0.6 + hy0 * 0.4
            body = skia.Path()
            body.moveTo(sx - 0.07 * H, sy - 0.01 * H)
            body.lineTo(sx + 0.07 * H, sy - 0.01 * H)
            body.lineTo(hx0 + 0.13 * H, low)
            body.lineTo(hx0 - 0.13 * H, low)
            body.close()
            c.drawPath(body, skia.Paint(AntiAlias=True, Color=rgba(ink, alpha), Style=skia.Paint.kStroke_Style,
                                        StrokeWidth=2 * o, StrokeJoin=skia.Paint.kRound_Join))
            c.drawPath(body, skia.Paint(AntiAlias=True, Color=rgba(coat, alpha)))
            for s_ in ("l", "r"):
                limb([J["sho"], J[s_ + "elb"]], coat, w * 1.5)
            c.drawCircle(hx, hy, r * 1.32 + o, skia.Paint(AntiAlias=True, Color=rgba(ink, alpha)))
            c.drawCircle(hx, hy, r * 1.32, skia.Paint(AntiAlias=True, Color=rgba(coat, alpha)))
        c.drawCircle(hx, hy, r + o, skia.Paint(AntiAlias=True, Color=rgba(ink, alpha)))
        c.drawCircle(hx, hy, r, skia.Paint(AntiAlias=True, Color=rgba(fill, alpha)))
        if "hat" in self.extras:
            hat = mix((60, 64, 80), (0, 0, 0), self.shade * 0.5)
            c.drawRect(skia.Rect(hx - r * 1.25, hy - r * 0.55, hx + r * 1.25, hy - r * 0.35), skia.Paint(AntiAlias=True, Color=rgba(hat, alpha)))
            c.drawRoundRect(skia.Rect(hx - r * 0.8, hy - r * 1.35, hx + r * 0.8, hy - r * 0.45), r * 0.2, r * 0.2,
                            skia.Paint(AntiAlias=True, Color=rgba(hat, alpha)))
        if self.face:
            self._face(c, hx, hy, r, facing, alpha)
        return J

    def _face(self, c, hx, hy, r, facing, alpha):
        ink = skia.Paint(AntiAlias=True, Color=rgba(self.ink, alpha))
        line = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.09,
                          StrokeCap=skia.Paint.kRound_Cap, Color=rgba(self.ink, alpha))
        ex = r * 0.36
        ey = hy - r * 0.08
        if self.face == "glasses":
            for s in (-1, 1):
                c.drawCircle(hx + s * ex, ey, r * 0.27, line)
                c.drawCircle(hx + s * ex, ey, r * 0.08, ink)
            c.drawLine(hx - ex + r * 0.27, ey, hx + ex - r * 0.27, ey, line)
        else:
            for s in (-1, 1):
                c.drawCircle(hx + s * ex, ey, r * 0.1, ink)
        if self.face in ("worried", "glasses"):
            for s in (-1, 1):
                c.drawLine(hx + s * ex - r * 0.15, ey - r * 0.38 + s * 0.06 * r, hx + s * ex + r * 0.15,
                           ey - r * 0.38 - s * 0.06 * r, line)
        if "mustache" in self.extras:
            m = skia.Path()
            m.moveTo(hx - r * 0.4, hy + r * 0.42)
            m.quadTo(hx, hy + r * 0.18, hx + r * 0.4, hy + r * 0.42)
            m.quadTo(hx, hy + r * 0.32, hx - r * 0.4, hy + r * 0.42)
            c.drawPath(m, ink)
        else:
            p = skia.Path()
            p.moveTo(hx - r * 0.22, hy + r * 0.45)
            p.quadTo(hx, hy + r * (0.32 if self.face == "worried" else 0.55), hx + r * 0.22, hy + r * 0.45)
            c.drawPath(p, line)
