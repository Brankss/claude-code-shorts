"""Format "rules": storie di sopravvivenza in seconda persona, con regole numerate e un dilemma finale.

Ricalca la grammatica dei video tipo "14 Floors Up": voce narrante calma ("Imagine you..."), illustrazioni
piatte con stickman, HUD in alto a sinistra con giorno, ora e luogo, didascalie a blocchi di 1-3 parole con
la parola detta evidenziata, card "RULE #n" con testo condensato enorme, un secondo personaggio che parla
(con il suo cartellino), domanda finale al pubblico e cartello "DAY 2".

La timeline la decide la voce: ogni Beat ha la sua battuta, sintetizzata con Kokoro (vedi voice.py), e
dura quanto la battuta più una pausa. Le scene sono funzioni che disegnano in uno spazio 1080x1920; la
camera (zoom e pan lenti, scossoni) e le transizioni le applica il motore.
"""

import math
import re
from dataclasses import dataclass, field

import numpy as np
import skia

from . import gfx, voice
from . import kinetic as K
from .base import FPS, H, W
from .gfx import rgba

LIME = (206, 242, 64)
ORANGE = (255, 160, 64)
RED = (222, 44, 44)
WHITE = (255, 255, 255)

CAPTION_Y = 1222
HUD_X = 50


def bebas(size):
    return gfx._font("BebasNeue-Regular.woff", size)


def oswald(size):
    return gfx._font("Oswald-Bold.woff", size)


@dataclass
class Beat:
    text: str = ""
    who: str = "narrator"         # "narrator" | "char"
    scene: str = None             # scena (None = come il beat prima)
    cam: dict = None              # {"z": (z0, z1), "c": ((x0, y0), (x1, y1)), "ease": "inout"|"out"|"lin"}
    clock: str = None             # "6:42 AM"; "" nasconde l'HUD; None = invariato
    card: dict = None             # {"kind": "rule"|"title"|"question", ...}
    cut: str = "cut"              # come entra: cut | fade | black | flash
    hold: float = 0.06            # silenzio dopo la battuta (o durata del beat se è muto)
    sfx: tuple = ()               # (("knock", 0.3), ...) secondi dall'inizio del beat
    fx: tuple = ()                # (("shake", 0.2, 14), ("flash", 0.0, (255, 40, 40)))
    params: dict = field(default_factory=dict)
    music: float = None           # tensione 0..1 della musica (None = invariata)
    caption: bool = True          # False: niente didascalia (il testo è già sullo schermo)
    voice: str = None             # voce diversa per questa battuta (es. la "mamma" lontana)
    pitch: float = None           # semitoni per questa battuta (None = quelli della storia)
    last_pitch: float = None      # semitoni per l'ultimo pezzo (dopo l'ultimo "..."): una parola "sbagliata"
    last_delay: float = 0.0       # ritardo in più prima dell'ultimo pezzo
    filt: str = None              # effetto sulla voce: door | far | speaker | glass (None = quello della storia)
    name: str = None              # cartellino: nome di chi parla (None = story.char_name)
    tag: str = None               # cartellino: dove ("THROUGH THE GLASS")
    hud: tuple = None             # righe extra dell'HUD [(testo, colore[, secondi dopo cui si guasta in testo2, testo2])]
                                  # None = invariate, () = nessuna
    mute: tuple = ()              # ((quando, durata), ...): silenzio assoluto di tutto il mix (voce compresa: solo nei vuoti)
    duck: tuple = ()              # ((quando, durata, quanto 0..1), ...): abbassa musica ed effetti, la voce resta
    clock_color: tuple = None     # colore dell'orologio dell'HUD da questo beat (None = invariato)


@dataclass
class Story:
    name: str
    title: str                    # "OPEN 24 HOURS"
    day: str                      # "DAY 1"
    place: str                    # terza riga dell'HUD
    beats: list
    scenes: dict                  # nome -> funzione(c, s, beat, R)
    narrator: str = "am_michael*0.6+am_onyx*0.4"
    speed: float = 1.22
    char_voice: str = "bm_george"
    char_speed: float = 1.0
    char_pitch: float = 0.0       # semitoni (es. +2.5 per una bambina partendo da una voce adulta)
    char_name: str = ""
    char_tag: str = ""            # "THROUGH THE DOOR"
    char_filter: str = None       # "door" | "speaker" | None
    next_day: str = "DAY 2"
    end_time: tuple = ("11:59 PM", "12:00 AM")
    end_label: str = None         # invito sul cartello finale (None = "FOLLOW FOR DAY 2")
    end_glitch: float = 1.4       # secondi dopo cui DAY 1 si guasta in DAY 2
    end_echo: str = None          # battuta del narratore che torna dalla cassa nel cartello finale (None = l'ultima)
    copy: dict = field(default_factory=dict)
    lead: float = 0.12            # silenzio prima della prima parola


def at_time(entry, spec):
    """Secondi dall'inizio del beat per un tempo scritto come numero o come "@parola", "@parola:end",
    con un eventuale scarto "+0.2" / "-0.1". La parola è la prima che la contiene."""
    if not isinstance(spec, str):
        return float(spec)
    m = re.match(r"@([^:+\-]+)(:end)?([+\-][\d.]+)?$", spec)
    word, end, extra = m.group(1), m.group(2), m.group(3)
    hit = next((w for w in entry["words"] if word.lower() in w.text.lower()), None)
    t = 0.0 if hit is None else (hit.end if end else hit.start) - entry["t0"]
    return t + (float(extra) if extra else 0.0)


# ---------- timeline ----------

def _tight(audio, words, tail=0.07):
    """Taglia il silenzio in coda alla battuta (Kokoro lascia ~0.4 s di respiro): i tagli restano serrati."""
    loud = np.where(np.abs(audio) > 0.012)[0]
    end = len(audio) if not len(loud) else min(len(audio), loud[-1] + int(tail * voice.SR))
    end = max(end, int((words[-1].end + 0.03) * voice.SR) if words else end)
    out = audio[:end].copy()
    n = min(len(out), int(0.03 * voice.SR))
    if n:
        out[-n:] *= np.linspace(1, 0, n)
    return out


def _takes(text):
    """Spezza la battuta dopo ogni '...': ogni pezzo si sintetizza a parte e la pausa la mettiamo noi."""
    parts = re.split(r"(?<=\.\.\.)\s+", text.strip())
    return [p for p in parts if p]


def _chunks(words, max_words=3, max_chars=17):
    out, cur = [], []
    for w in words:
        cur.append(w)
        n = sum(len(x.text) + 1 for x in cur)
        if len(cur) >= max_words or n >= max_chars or re.search(r"[.,!?:;…]$|\.\.\.$", w.text):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    # niente blocchi di una parola corta da sola alla fine, se si può attaccare al precedente
    if len(out) > 1 and len(out[-1]) == 1 and len(out[-2]) < max_words and len(out[-1][0].text) <= 4 \
            and not re.search(r"[.,!?:;…]$", out[-2][-1].text):
        out[-2] += out.pop()
    return out


def _minutes(s):
    m = re.match(r"(\d+):(\d+)\s*(AM|PM)", s.strip().upper())
    h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3)
    return (h % 12 + (12 if ap == "PM" else 0)) * 60 + mi


def _fmt_clock(minutes):
    minutes = int(round(minutes)) % (24 * 60)
    h, mi = divmod(minutes, 60)
    ap = "AM" if h < 12 else "PM"
    return f"{(h % 12) or 12}:{mi:02d}", ap


class Timeline:
    def __init__(self, story):
        self.story = story
        self.beats = []       # dict: beat, t0, t1, takes [(t, audio, who)], words [(Word assoluta, who)]
        self.captions = []    # dict: t0, t1, words [(text, t_start)], who
        self.shots = []       # inquadrature: beat consecutivi senza scena/camera nuova restano nella stessa
        t = story.lead
        scene = None
        clock = ""
        hud = ()
        clock_color = WHITE
        for b in story.beats:
            if b.scene is not None or b.cam is not None or not self.shots:
                self.shots.append({"t0": t, "cam": b.cam or {}, "scene": b.scene or scene})
            scene = b.scene or scene
            clock = clock if b.clock is None else b.clock
            hud = hud if b.hud is None else b.hud
            clock_color = clock_color if b.clock_color is None else tuple(b.clock_color)
            entry = {"beat": b, "t0": t, "scene": scene, "clock": clock, "takes": [], "words": [],
                     "shot": len(self.shots) - 1, "hud": hud, "clock_color": clock_color}
            v, sp = (story.narrator, story.speed) if b.who == "narrator" else (story.char_voice, story.char_speed)
            v = b.voice or v
            pitch = b.pitch if b.pitch is not None else (story.char_pitch if b.who == "char" else 0.0)
            filt = b.filt if b.filt is not None else (story.char_filter if b.who == "char" else None)
            takes = _takes(b.text)
            for ti, take in enumerate(takes):
                last = ti == len(takes) - 1 and len(takes) > 1
                if last and b.last_delay:
                    t += b.last_delay
                words, audio = voice.say(take, v, sp, pitch=b.last_pitch if last and b.last_pitch is not None else pitch)
                audio = _tight(audio, words)
                entry["takes"].append((t, audio, b.who, filt))
                entry["words"] += [voice.Word(w.text, t + w.start, t + w.end) for w in words]
                t += len(audio) / voice.SR + (0.24 if take.endswith("...") else 0.05)
            t += b.hold
            entry["t1"] = t
            self.shots[-1]["t1"] = t
            self.beats.append(entry)
            if b.caption:
                for ch in _chunks(entry["words"]):
                    self.captions.append({"t0": ch[0].start - 0.04, "words": [(w.text, w.start) for w in ch],
                                          "who": b.who, "end": ch[-1].end, "beat_t1": t,
                                          "name": b.name, "tag": b.tag})
        for i, cap in enumerate(self.captions):
            nxt = self.captions[i + 1]["t0"] if i + 1 < len(self.captions) else math.inf
            cap["t1"] = min(nxt, cap["end"] + 0.45, cap["beat_t1"] + 0.05)
        self.duration = t + 0.05
        self.t0s = np.array([e["t0"] for e in self.beats])

    def at(self, t):
        i = max(0, int(np.searchsorted(self.t0s, t, side="right")) - 1)
        return i, self.beats[i]


# ---------- renderer ----------

class Renderer:
    def __init__(self, story):
        self.story = story
        self.tl = Timeline(story)
        self.n_frames = int(math.ceil(self.tl.duration * FPS))
        self.surface = skia.Surface(W, H)

    # --- camera e scena ---

    def _cam(self, shot, s):
        cam = shot["cam"]
        dur = max(0.01, shot["t1"] - shot["t0"])
        k = min(1.0, s / dur)
        e = {"inout": gfx.ease_in_out, "out": gfx.ease_out, "lin": lambda x: x}[cam.get("ease", "inout")](k)
        z0, z1 = cam.get("z", (1.0, 1.06))
        (x0, y0), (x1, y1) = cam.get("c", ((540, 960), (540, 960)))
        r0, r1 = cam.get("r", (0.0, 0.0))
        self.cam_rot = r0 + (r1 - r0) * e
        return z0 + (z1 - z0) * e, x0 + (x1 - x0) * e, y0 + (y1 - y0) * e

    def _scene(self, c, idx, t):
        entry = self.tl.beats[idx]
        shot = self.tl.shots[entry["shot"]]
        s = t - shot["t0"]
        self.t, self.bs, self.shot, self.entry = t, t - entry["t0"], shot, entry
        self.ss = s
        z, cx, cy = self._cam(shot, s)
        # camera a mano: una deriva lentissima, così nessuna inquadratura è mai ferma
        sway = shot["cam"].get("sway", 1.0)
        dx = sway * (4 * math.sin(t * 0.61) + 2 * math.sin(t * 1.37))
        dy = sway * (3 * math.sin(t * 0.47 + 1) + 1.5 * math.sin(t * 1.11))
        for f in entry["beat"].fx:
            if f[0] == "shake":
                ddx, ddy = K.shake(self.bs - f[1], amount=f[2])
                dx, dy = dx + ddx, dy + ddy
            elif f[0] == "punch":
                z *= K.punch(self.bs - f[1], amount=f[2] if len(f) > 2 else 0.08, decay=5.0)
        c.save()
        c.translate(W / 2 + dx, H / 2 + dy)
        c.scale(z, z)
        if self.cam_rot:
            c.rotate(self.cam_rot)
        c.translate(-cx, -cy)
        fn = self.story.scenes.get(entry["scene"])
        if fn is None:
            getattr(self, entry["scene"])(c, s, entry["beat"])   # scene del motore (endcard)
        else:
            fn(c, s, entry["beat"], self)
        c.restore()

    def render(self, f):
        t = f / FPS
        c = self.surface.getCanvas()
        c.clear(skia.Color(8, 8, 10))
        idx, entry = self.tl.at(t)
        b = entry["beat"]
        s = t - entry["t0"]
        self._scene(c, idx, t)
        # transizioni in entrata
        if idx > 0 and b.cut == "fade" and s < 0.4:
            prev = self.tl.beats[idx - 1]
            c.saveLayerAlpha(None, int(255 * (1 - gfx.ease_in_out(s / 0.4))))
            self._scene(c, idx - 1, min(t, prev["t1"] - 1e-3))
            c.restore()
        if b.cut == "black" and s < 0.5:
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=rgba((0, 0, 0), 1 - gfx.ease_out(s / 0.5))))
        if b.cut == "flash":
            K.flash(c, s, strength=0.8)
        for name, at, col in (fx for fx in b.fx if fx[0] == "flash"):
            K.flash(c, s - at, color=col, strength=0.55, decay=5.0)
        self._hud(c, idx, t)
        self._card(c, idx, t)
        _, card = self._active_card(idx)
        if not (card and card.get("kind") == "black_reveal") and entry["scene"] != "endcard":
            self._captions(c, t)            # sul nero le parole sono già la card; sul cartello finale niente
        img = self.surface.makeImageSnapshot()
        return img.toarray(colorType=skia.kRGBA_8888_ColorType)

    def when(self, j, spec):
        """Tempo assoluto di spec (numero dall'inizio del beat j, oppure "@parola[:end][+x]" cercata
        dal beat j in avanti: una card può restare a schermo mentre la voce va avanti)."""
        if not isinstance(spec, str):
            return self.tl.beats[j]["t0"] + float(spec)
        word = re.match(r"@([^:+\-]+)", spec).group(1).lower()
        for e in self.tl.beats[j:]:
            if any(word in w.text.lower() for w in e["words"]):
                return e["t0"] + at_time(e, spec)
        return self.tl.beats[j]["t0"]

    def word(self, needle, entry=None, end=False):
        """Secondi dall'inizio del beat in cui viene detta la prima parola che contiene needle (None se non c'è)."""
        entry = entry or self.entry
        for w in entry["words"]:
            if needle.lower() in w.text.lower():
                return (w.end if end else w.start) - entry["t0"]
        return None

    # --- HUD: giorno, ora, luogo ---

    def _hud(self, c, idx, t):
        entry = self.tl.beats[idx]
        if not entry["clock"]:
            return
        j, card = self._active_card(idx)
        if card and card["kind"] == "title" and not card.get("hud") and t - self.tl.beats[j]["t0"] < card.get("dur", 2.2):
            return   # il titolo della serie occupa la parte alta, come nel riferimento
        s = t - entry["t0"]
        a = min(1.0, s / 0.25) if idx == 0 or not self.tl.beats[idx - 1]["clock"] else 1.0
        cur = _minutes(entry["clock"])
        prev = self.tl.beats[idx - 1]["clock"] if idx > 0 else ""
        if prev and prev != entry["clock"] and s < 0.7:
            p = _minutes(prev)
            if cur < p:
                cur += 24 * 60
            cur = p + (cur - p) * gfx.ease_out(s / 0.7)
        hhmm, ap = _fmt_clock(cur)
        x, y = HUD_X, 292
        c.drawCircle(x + 6, y - 8, 6, skia.Paint(AntiAlias=True, Color=rgba(RED, a)))
        gfx.draw_text(c, self.story.day, K.bold(24), x + 20, y, color=(235, 90, 80), alpha=a, align="left", tracking=2)
        big = gfx.mono(72, "SemiBold")
        gfx.draw_text(c, hhmm, big, x, y + 74, color=entry["clock_color"], alpha=a, align="left")
        gfx.draw_text(c, ap, K.bold(24), x + big.measureText(hhmm) + 10, y + 74, color=(220, 220, 225), alpha=a,
                      align="left")
        c.drawLine(x, y + 96, x + 250, y + 96, skia.Paint(AntiAlias=True, StrokeWidth=2, Color=rgba((255, 255, 255), 0.35 * a)))
        gfx.draw_text(c, self.story.place, gfx.mono(22, "Medium"), x, y + 128, color=(170, 172, 180), alpha=a,
                      align="left", tracking=3)
        yy = y + 162
        for line in entry["hud"]:
            txt, col = line[0], line[1]
            if len(line) > 3:
                at = line[2] if not isinstance(line[2], str) else (self.word(line[2][1:], entry) or 0.0)
                back = line[5] if len(line) > 5 else None
                if s >= at and (back is None or s < at + back):
                    g = s - at
                    if g < 0.3 and int(g * 30) % 2 == 0:
                        gfx.draw_text(c, txt, gfx.mono(22, "Medium"), x + 6 * math.sin(g * 90), yy, color=(255, 60, 60),
                                      alpha=a, align="left", tracking=3)
                        yy += 32
                        continue
                    txt, col = line[3], line[4] if len(line) > 4 else (255, 80, 70)
            gfx.draw_text(c, txt, gfx.mono(22, "Medium"), x, yy, color=col, alpha=a, align="left", tracking=3)
            yy += 32

    # --- card: regole, titolo, domanda finale ---

    def _active_card(self, idx):
        """La card dell'ultimo beat che ne ha una, finché un beat non la toglie (card={'kind': None})."""
        for j in range(idx, -1, -1):
            card = self.tl.beats[j]["beat"].card
            if card is not None:
                return (j, card) if card.get("kind") else (None, None)
        return None, None

    def _card(self, c, idx, t):
        j, card = self._active_card(idx)
        if card is None:
            return
        entry = self.tl.beats[j]
        s = t - entry["t0"] - card.get("at", 0.0)
        if s < 0:
            return
        kind = card["kind"]
        if kind == "rule":
            self._rule(c, card, s, t)
        elif kind == "title":
            dur = card.get("dur", 2.2)
            a = min(1.0, s / 0.25) * (1 - gfx.ease_in_out((s - dur + 0.4) / 0.4))
            if a <= 0:
                return
            ty = card.get("y", 470)
            if not card.get("hud"):
                gfx.draw_text(c, self.story.day, K.bold(30), W / 2, ty - 140, color=(235, 90, 80), alpha=a * 0.9, tracking=8)
            f = bebas(card.get("size", 196))
            sc = 1.08 - 0.08 * gfx.ease_out(s / 0.25)
            c.save()
            c.translate(W / 2 + (2 * math.sin(s * 90) if s < 0.3 else 0), ty)
            c.scale(sc, sc)
            glow = skia.Paint(AntiAlias=True, Color=rgba((255, 120, 70), 0.55 * a),
                              MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 26))
            w = f.measureText(self.story.title)
            c.drawString(self.story.title, -w / 2, 0, f, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                                                     StrokeWidth=8, Color=rgba((0, 0, 0), 0.7 * a)))
            c.drawString(self.story.title, -w / 2, 0, f, glow)
            c.drawString(self.story.title, -w / 2, 0, f, skia.Paint(AntiAlias=True, Color=rgba(WHITE, a)))
            c.restore()
        elif kind == "banner":
            k = gfx.ease_out(s / 0.3)
            y = 470 - 140 * (1 - k)
            r = skia.RRect.MakeRectXY(skia.Rect(60, y, W - 60, y + 150), 34, 34)
            c.drawRRect(r, skia.Paint(AntiAlias=True, Color=rgba((120, 22, 26), 0.95 * k)))
            c.drawRRect(r, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3,
                                      Color=rgba((255, 120, 100), 0.8 * k)))
            gfx.draw_text(c, card.get("title", "ALERT"), K.heavy(30), 100, y + 52, color=(255, 150, 130), alpha=k,
                          align="left", tracking=2)
            f = gfx.fit_font(K.heavy, card["text"], W - 200, 50)
            gfx.draw_text(c, card["text"], f, 100, y + 112, color=WHITE, alpha=k, align="left")
        elif kind == "black_reveal":
            self._black_reveal(c, card, j, t)
        elif kind == "ledger":
            self._ledger(c, card, j, t, s)
        elif kind == "question":
            k = gfx.ease_out(s / 0.3)
            f = bebas(150)
            text = card["text"]
            sc = 0.9 + 0.1 * K.back_out(s / 0.35)
            c.save()
            c.translate(W / 2, 640)
            c.scale(sc, sc)
            w = f.measureText(text)
            if w > 980:
                c.scale(980 / w, 980 / w)
            c.drawString(text, -w / 2 + 4, 6, f, skia.Paint(AntiAlias=True, Color=rgba((0, 0, 0), 0.6 * k),
                                                             MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10)))
            c.drawString(text, -w / 2, 0, f, skia.Paint(AntiAlias=True, Color=rgba(WHITE, k)))
            c.restore()
            if card.get("sub"):
                ks = gfx.ease_out((s - card.get("sub_at", 0.8)) / 0.3)
                gfx.draw_text(c, card["sub"], K.bold(36), W / 2, 730, color=(235, 235, 235), alpha=ks, tracking=3)

    def _black_reveal(self, c, card, j, t):
        """Twist su nero in due righe: la prima bianca entra con la voce, la seconda rossa e più grande
        compare di colpo, nello stesso fotogramma del colpo (vedi rules_audio.build)."""
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=rgba((2, 1, 4))))
        t1 = self.when(j, card.get("l1_at", 0.0))
        t2 = self.when(j, card.get("l2_at", 1.0))
        for text, t0, size, col, y in ((card["l1"], t1, 120, WHITE, 860), (card["l2"], t2, 210, (230, 40, 36), 1080)):
            g = t - t0
            if g < 0:
                continue
            f = bebas(size)
            w = f.measureText(text)
            sc = min(1.0, 980 / w) * (1.0 if col == WHITE else 1.0 + 0.1 * max(0.0, 1 - g / 0.12))
            c.save()
            c.translate(W / 2 + (6 * math.sin(g * 120) if col != WHITE and g < 0.15 else 0), y)
            c.scale(sc, sc)
            if col != WHITE:
                c.drawString(text, -w / 2, 0, f, skia.Paint(AntiAlias=True, Color=rgba(col, 0.45),
                                                             MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30)))
            c.drawString(text, -w / 2, 0, f, skia.Paint(AntiAlias=True, Color=rgba(col)))
            c.restore()

    def _ledger(self, c, card, j, t, s):
        """Registro di casa: card scura al centro, righe che contano e si fermano sulla parola detta."""
        rows = card["rows"]
        k = K.back_out(s / 0.28) if s < 0.28 else 1.0
        a = min(1.0, s / 0.15)
        x0, x1 = 90, W - 90
        top = card.get("y", 600)
        bottom = top + 124 + 120 * len(rows)
        c.save()
        c.translate(W / 2, (top + bottom) / 2)
        c.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k)
        c.translate(-W / 2, -(top + bottom) / 2)
        r = skia.RRect.MakeRectXY(skia.Rect(x0, top, x1, bottom), 28, 28)
        c.drawRRect(r, skia.Paint(AntiAlias=True, Color=rgba((0, 0, 0), 0.5 * a),
                                  MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 24)))
        c.drawRRect(r, skia.Paint(AntiAlias=True, Color=rgba((14, 14, 18), 0.94 * a)))
        c.drawRRect(r, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2,
                                  Color=rgba((255, 255, 255), 0.18 * a)))
        c.drawCircle(x0 + 46, top + 62, 7, skia.Paint(AntiAlias=True, Color=rgba(RED, a)))
        gfx.draw_text(c, card.get("title", "HOUSE LOG"), gfx.mono(36, "SemiBold"), x0 + 66, top + 75,
                      color=(240, 240, 244), alpha=a, align="left", tracking=3)
        c.drawLine(x0 + 40, top + 100, x1 - 40, top + 100,
                   skia.Paint(AntiAlias=True, StrokeWidth=2, Color=rgba((255, 255, 255), 0.22 * a)))
        for i, row in enumerate(rows):
            y = top + 176 + 120 * i
            ra = a * min(1.0, max(0.0, (s - 0.12 - 0.08 * i) / 0.2))
            if ra <= 0:
                continue
            col = tuple(row.get("color", (235, 235, 240)))
            gfx.draw_text(c, row["label"], gfx.mono(31, "Medium"), x0 + 46, y, color=(180, 182, 192), alpha=ra,
                          align="left", tracking=2)
            frac = None
            if "to" in row:
                stop = self.when(j, row.get("at", 0.0))
                dur = row.get("dur", 0.8)
                p = gfx.ease_out(min(1.0, max(0.0, (t - (stop - dur)) / dur)))
                v = row.get("from", 0) + (row["to"] - row.get("from", 0)) * p
                text = row.get("fmt", "{}").format(int(round(v)))
                if row.get("max"):
                    frac = v / row["max"]
            else:
                text = str(row.get("value", ""))
                if row.get("max") and isinstance(row.get("fill"), (int, float)):
                    frac = row["fill"] / row["max"]
            if row.get("approx"):
                text = "≈ " + text
            gfx.draw_text(c, text, gfx.mono(50, "SemiBold"), x1 - 46, y + 6, color=col, alpha=ra, align="right")
            if row.get("bar") and frac is not None:
                by = y + 30
                c.drawRoundRect(skia.Rect(x0 + 46, by, x1 - 46, by + 8), 4, 4,
                                skia.Paint(AntiAlias=True, Color=rgba((255, 255, 255), 0.12 * ra)))
                c.drawRoundRect(skia.Rect(x0 + 46, by, x0 + 46 + (x1 - x0 - 92) * max(0.0, min(1.0, frac)), by + 8), 4, 4,
                                skia.Paint(AntiAlias=True, Color=rgba(col, ra)))
        c.restore()

    def _rule(self, c, card, s, t):
        """RULE #n in rosso, poi il testo enorme con sottolineatura; dopo un po' si rimpicciolisce e resta."""
        n, text, sub = card["n"], card["text"], card.get("sub")
        tag_k = K.back_out(s / 0.3) if s < 0.3 else 1.0
        shrink = gfx.ease_in_out((s - card.get("shrink", 2.4)) / 0.5)
        # cartellino
        tag = f"RULE #{n}"
        tf = K.heavy(40)
        tw = tf.measureText(tag)
        ty = 440 - 30 * shrink
        c.save()
        c.translate(W / 2, ty)
        c.rotate(-2.0)
        c.scale(tag_k * (1 - 0.15 * shrink), tag_k * (1 - 0.15 * shrink))
        c.drawRect(skia.Rect(-tw / 2 - 18, -40, tw / 2 + 18, 14), skia.Paint(AntiAlias=True, Color=rgba(RED)))
        c.drawString(tag, -tw / 2, 0, tf, skia.Paint(AntiAlias=True, Color=rgba(WHITE)))
        c.restore()
        # testo grande (eventualmente censurato prima di essere rivelato)
        reveal = card.get("reveal")
        k = gfx.ease_out((s - 0.18) / 0.3)
        if k <= 0:
            return
        size = 168 * (1 - 0.42 * shrink)
        f = bebas(size)
        w = f.measureText(text)
        fit = min(1.0, 1000 / w)
        y = 600 - 90 * shrink
        c.save()
        c.translate(W / 2, y)
        c.scale(fit * (0.92 + 0.08 * k), fit * (0.92 + 0.08 * k))
        if reveal is not None and s < reveal:
            # barre grigie al posto delle parole: la regola che "conosci già"
            x = -w / 2
            for word in text.split():
                ww = f.measureText(word)
                c.drawRect(skia.Rect(x, -size * 0.72, x + ww, 0), skia.Paint(AntiAlias=True, Color=rgba((150, 150, 156), 0.95 * k)))
                x += ww + f.measureText(" ")
        else:
            rk = 1.0 if reveal is None else gfx.ease_out((s - reveal) / 0.25)
            c.drawString(text, -w / 2 + 5, 7, f, skia.Paint(AntiAlias=True, Color=rgba((0, 0, 0), 0.55 * k),
                                                             MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10)))
            c.drawString(text, -w / 2, 0, f, skia.Paint(AntiAlias=True, Color=rgba(WHITE, k * rk)))
            if sub:
                sf = bebas(size * 0.62)
                sw = sf.measureText(sub)
                c.drawString(sub, -sw / 2, size * 0.62, sf, skia.Paint(AntiAlias=True, Color=rgba(RED, k * rk)))
        if not sub:
            uk = gfx.ease_out((s - 0.35) / 0.4)
            c.drawRect(skia.Rect(-w / 2, size * 0.1, -w / 2 + w * uk, size * 0.1 + 9),
                       skia.Paint(AntiAlias=True, Color=rgba(RED, k)))
        c.restore()

    # --- didascalie ---

    def _captions(self, c, t):
        for cap in self.tl.captions:
            if not (cap["t0"] <= t < cap["t1"]):
                continue
            age = t - cap["t0"]
            who = cap["who"]
            hot = LIME if who == "narrator" else ORANGE
            words = [w for w, _ in cap["words"]]
            cur = 0
            for i, (_, ws) in enumerate(cap["words"]):
                if t >= ws - 0.02:
                    cur = i
            font = K.heavy(68)
            space = font.measureText(" ")
            widths = [font.measureText(w.upper()) for w in words]
            total = sum(widths) + space * (len(words) - 1)
            scale = min(1.0, 960 / total)
            pop = 0.86 + 0.14 * K.back_out(age / 0.16)
            c.save()
            c.translate(W / 2, CAPTION_Y)
            c.scale(pop * scale, pop * scale)
            x = -total / 2
            stroke = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=13,
                                StrokeJoin=skia.Paint.kRound_Join, Color=rgba((0, 0, 0), 0.95))
            shadow = skia.Paint(AntiAlias=True, Color=rgba((0, 0, 0), 0.6),
                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 12))
            for i, w in enumerate(words):
                u = w.upper()
                c.drawString(u, x + 3, 7, font, shadow)
                c.drawString(u, x, 0, font, stroke)
                col = hot if i == cur else WHITE
                c.drawString(u, x, 0, font, skia.Paint(AntiAlias=True, Color=rgba(col)))
                x += widths[i] + space
            c.restore()
            if who == "char" and self.story.char_name:
                self._pill(c, CAPTION_Y - 88, min(1.0, age / 0.15))
            break

    # --- cartello finale ---

    def endcard(self, c, s, beat):
        """Titolo della serie, DAY 1 che si guasta in DAY 2 rosso, "FOLLOW FOR DAY 2"."""
        st = self.story
        glitch_at = st.end_glitch
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=rgba((6, 6, 8))))
        a = min(1.0, s / 0.4)
        f = bebas(120)
        tw = f.measureText(st.title)
        glow = skia.Paint(AntiAlias=True, Color=rgba((255, 255, 255), 0.35 * a),
                          MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
        c.drawString(st.title, W / 2 - tw / 2, 600, f, glow)
        c.drawString(st.title, W / 2 - tw / 2, 600, f, skia.Paint(AntiAlias=True, Color=rgba((240, 240, 240), a)))
        g = s - glitch_at
        after = g >= 0.25
        day = st.next_day if after else st.day
        clock = st.end_time[1] if after else st.end_time[0]
        col = (255, 70, 50) if after else (245, 245, 245)
        big = bebas(300)
        dw = big.measureText(day)
        rng = np.random.default_rng(int(s * 30))
        glitching = 0 <= g < 0.45
        if after:
            c.drawString(day, W / 2 - dw / 2, 900, big, skia.Paint(AntiAlias=True, Color=rgba((255, 60, 40), 0.6),
                                                                    MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30)))
        if glitching:
            for dx, cc in ((-12, (255, 0, 60)), (12, (0, 220, 255))):
                c.drawString(day, W / 2 - dw / 2 + dx * rng.uniform(0.5, 1.5), 900, big,
                             skia.Paint(AntiAlias=True, Color=rgba(cc, 0.6), BlendMode=skia.BlendMode.kPlus))
            for _ in range(6):
                y0 = rng.uniform(650, 920)
                c.save()
                c.clipRect(skia.Rect(0, y0, W, y0 + rng.uniform(10, 50)))
                c.drawString(day, W / 2 - dw / 2 + rng.uniform(-60, 60), 900, big, skia.Paint(AntiAlias=True, Color=rgba(col)))
                c.restore()
        else:
            c.drawString(day, W / 2 - dw / 2, 900, big, skia.Paint(AntiAlias=True, Color=rgba(col, a)))
        gfx.draw_text(c, clock, gfx.mono(46, "Medium"), W / 2, 990, color=(225, 225, 230), alpha=a, tracking=4)
        k = gfx.ease_out((s - 0.6) / 0.4)
        if k > 0:
            label = st.end_label or f"FOLLOW FOR {st.next_day}"
            pf = K.bold(34)
            pw = pf.measureText(label)
            r = skia.RRect.MakeRectXY(skia.Rect(W / 2 - pw / 2 - 40, 1080, W / 2 + pw / 2 + 40, 1160), 40, 40)
            c.drawRRect(r, skia.Paint(AntiAlias=True, Color=rgba((20, 18, 18), 0.9 * k)))
            c.drawRRect(r, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3,
                                      Color=rgba((255, 110, 80), k)))
            gfx.draw_text(c, label, pf, W / 2, 1133, color=(245, 240, 235), alpha=k, tracking=2)

    def _pill(self, c, y, a):
        name = self.story.char_name.upper()
        tag = self.story.char_tag.upper()
        f = K.bold(22)
        sep = "  ·  "
        w = f.measureText(name) + (f.measureText(sep + tag) if tag else 0)
        r = skia.RRect.MakeRectXY(skia.Rect(W / 2 - w / 2 - 24, y - 30, W / 2 + w / 2 + 24, y + 12), 21, 21)
        c.drawRRect(r, skia.Paint(AntiAlias=True, Color=rgba((18, 16, 16), 0.88 * a)))
        c.drawRRect(r, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.5, Color=rgba(ORANGE, a)))
        x = W / 2 - w / 2
        gfx.draw_text(c, name, f, x, y, color=ORANGE, alpha=a, align="left")
        if tag:
            gfx.draw_text(c, sep + tag, f, x + f.measureText(name), y, color=(235, 230, 225), alpha=a, align="left")
