"""Storie del format "rules". Ogni storia è una funzione che restituisce una rules.Story."""

from . import dont_answer as DA
from .rules import Beat, Story

GREEN = (60, 190, 90)
VIS = (190, 196, 205)
DIM = (150, 152, 160)
REDV = (255, 120, 110)
RED_CLOCK = (255, 70, 60)


def vis(ft, extra=()):
    return ((f"VISIBILITY {ft} FT", VIS if ft else REDV),) + tuple(extra)


def dont_answer():
    """DON'T ANSWER, Day 1: una nebbia che copia le voci. L'allerta dice di non rispondere a nessuna voce,
    nemmeno a una che conosci. A mezzanotte la bambina della casa accanto è là fuori, con il telefono della mamma
    e la password di famiglia che nessuno ha mai detto ad alta voce. E qualcosa dietro di lei.

    v2 (75 s): catena causale tra le regole, registro della casa, scelta della torcia, twist su nero,
    l'outro che torna dalla cassa come ultimo suono. Vedi docs/PLAYBOOK.md."""
    pw = [("password?", True, -9), ("blue kite. never out loud.", False, -9)]
    evening = pw + [("voices stopped.", False, -9), ("walking home. stay quiet.", False, -9)]
    mom_del = ("MOM · DELIVERED 8:06 PM", DIM)
    mom_read = ("MOM · READ 11:51 PM", REDV)
    beats = [
        # ---------- hook: "voice" e "fog" entro 3 s, la contraddizione nella frase ----------
        Beat("Imagine you hear your mom's voice in the fog... while she's texting you. From work.",
             scene="bedroom", clock="6:41 AM", hud=vis(300), music=0.35,
             cam={"z": (1.0, 1.14), "c": ((560, 960), (720, 880))},
             sfx=(("fog", 0.0, 0.5), ("say:af_heart:Sweetie?", "@fog:end+0.05", 0.45, 0.6), ("buzz", "@texting", 0.45))),
        # titolo: colpo 1 di 5 (hai capito che fuori non è lei)
        Beat("", card={"kind": "title", "dur": 0.55, "hud": True, "y": 820, "size": 210}, hold=0.55,
             sfx=(("say:af_heart:Come outside...", 0.05, 0.25, 0.8),)),
        Beat("If you hear me outside... that's not me.", scene="phone", card={"kind": None},
             cam={"z": (1.0, 1.32), "c": ((540, 900), (540, 960))},
             params={"ui": "lock", "time": "6:41", "notifs": [
                 ("Mom", "Mom", "at work. people hear family outside", GREEN, -9),
                 ("Mom", "Mom", "if you hear me outside... that's not me.", GREEN, 0.05)]},
             sfx=(("buzz", 0.0, 0.4), ("text", 0.0, 0.4)), music=0.4),
        # l'allerta: niente HUD sopra il telefono zoomato
        Beat("Every phone screams: don't answer any voice...", scene="phone", clock="",
             cam={"z": (1.0, 1.12), "c": ((540, 880), (540, 960))},
             params={"ui": "alert", "hot": "answer", "line_at": [0.2, 0.45, 0.45, 0.8]},
             sfx=(("alert", 0.0, 0.42), ("alert", 0.25, 0.14, -0.7), ("alert", 0.5, 0.1, 0.7)), music=0.6),
        Beat("Even one you know.", cam={"z": (1.85, 2.0), "c": ((540, 1000), (540, 1010))},
             params={"ui": "alert", "dim_but": (3,)}, scene="phone"),
        # ---------- l'errore del terzo ----------
        Beat("But across the street, a man follows his wife's voice...", scene="street_top", clock="6:41 AM",
             hud=vis(200), cam={"z": (1.1, 1.3), "c": ((820, 990), (330, 820)), "r": (0.0, 3.0)},
             params={"walk_dur": 2.9},
             sfx=(("say:af_bella:Honey?", "@wife", 0.3, -0.8), ("steps", 0.1, 0.3))),
        # Ellie (gialla, piccola) esce di casa: easter egg per chi mette in pausa
        Beat("She's on the porch. Behind him.", scene="window_view", hold=0.06,
             cam={"z": (1.05, 1.15), "c": ((560, 1040), (600, 1060))},
             params={"mood": "dawn", "vis": 0.75, "what": "street", "man": "up", "walk_at": -0.4, "wife": True,
                     "hook": True, "ellie_out_at": 0.8, "you": True},
             sfx=(("whoosh_down", "@him", 0.25),), music=0.5),
        # ---------- tu guardavi: la #1 arriva come risposta (colpo 2) ----------
        Beat("If you can see out... it can see in.", scene="living", hud=vis(180),
             cam={"z": (1.55, 1.75), "c": ((880, 780), (875, 780))},
             params={"act": "strip", "led": 1.0},
             sfx=(("whoosh", 0.05, 0.2), ("whoosh_down", "@in:end-0.3", 0.3)), music=0.55),
        Beat("Rule number one: cover every window.", clock="9:00 AM", hud=vis(150),
             cam={"z": (1.0, 1.08), "c": ((760, 1000), (780, 980))},
             card={"kind": "rule", "n": 1, "text": "COVER EVERY WINDOW", "at": 0.25},
             params={"act": "cover", "led": 1.0}, sfx=(("tape", 1.0, 0.5), ("tape", 1.7, 0.4)), music=0.45),
        # ---------- non vede più dentro, quindi parla: dalla TV, con la voce della mamma ----------
        Beat("So it talks through your TV.", card={"kind": None}, clock="10:30 AM", hud=vis(120),
             cam={"z": (1.0, 1.15), "c": ((760, 1000), (1180, 1040))},
             params={"act": "listen", "tv": 1.0, "led": 1.0},
             sfx=(("static", 0.0, 0.25), ("say:af_heart:Sweetie... open the window...", "@TV:end", 0.3, 0.35))),
        Beat("Rule number two: unplug every speaker.",
             cam={"z": (1.15, 1.25), "c": ((1250, 1100), (1260, 1080))},
             card={"kind": "rule", "n": 2, "text": "UNPLUG EVERY SPEAKER", "at": 0.2, "boom": False},
             params={"act": "unplug", "tv": 1.0, "led": 1.0, "unplug_tv": "unplug", "unplug_spk": "speaker"},
             sfx=(("unplug", "@unplug:end", 0.6), ("unplug", "@speaker:end", 0.6), ("power_off", "@speaker:end+0.1", 0.3))),
        # ---------- chi non l'ha fatto: la casa di Ellie parla, e non c'è nessuno ----------
        Beat("Next door, Ellie's house is still talking. Nobody's home.", scene="window_view", clock="12:02 PM",
             hud=vis(100), card={"kind": None}, cam={"z": (1.0, 1.14), "c": ((540, 940), (560, 900))},
             params={"mood": "day", "vis": 0.6, "what": "ellie", "gap": 420, "tap_word": "home", "close_at": "@home"},
             sfx=(("say:af_heart:Mommy? Daddy?", 0.2, 0.18, 0.3), ("say:bm_george:We're home!", 0.9, 0.16, 0.4),
                  ("tap_soft", "@home", 0.4, 0.4)), music=0.55),
        # ---------- la voce della mamma non prova più niente: #3 ----------
        Beat("So, rule number three: a family password.", scene="living", clock="3:30 PM", hud=vis(60),
             cam={"z": (1.0, 1.1), "c": ((460, 1000), (420, 980))},
             card={"kind": "rule", "n": 3, "text": "FAMILY PASSWORD", "at": 0.35, "boom": False},
             params={"act": "sit", "led": 0.0, "unplugged": True}),
        Beat("Text it. Never say it.", scene="phone", card={"kind": None}, hold=0.06,
             cam={"z": (1.0, 1.45), "c": ((540, 900), (470, 720))},
             params={"ui": "chat", "msgs": [("password?", True, 0.0), ("blue kite. never out loud.", False, 0.45)],
                     "typing": 0.1, "typing_until": 0.45, "highlight": "blue kite.", "status": "online"},
             sfx=(("text", 0.0, 0.3), ("text", 0.45, 0.45)), duck=(("@Never", 1.0, 0.85),)),
        # ---------- tramonto: le voci tacciono (il mix con loro) MA il vicino è tornato ----------
        Beat("At sunset, the voices stop... and the neighbor is back.", scene="window_view",
             clock="7:52 PM", hud=vis(50), cut="black", hold=0.06,
             cam={"z": (1.0, 1.2), "c": ((540, 1000), (470, 1150))},
             params={"mood": "sunset", "vis": 0.55, "what": "street", "man": "bent", "porch": False, "hook": False,
                     "gap": 460, "gap_x": 470, "clock": True, "close_at": 2.9},
             sfx=(("say:af_bella:Hello?", 0.05, 0.22, -0.6), ("say:bm_george:Over here...", 0.4, 0.2, 0.6),
                  ("heartbeat", "@back", 0.35)),
             duck=(("@stop", 1.1, 0.95),), music=0.55),
        Beat("So mom heads home... and stops texting.", scene="phone", clock="8:06 PM",
             hud=vis(20), cam={"z": (1.0, 1.1), "c": ((540, 900), (540, 860))},
             params={"ui": "chat", "msgs": evening + [("ok. text me every 5 min", True, 2.3)],
                     "receipt": ("Delivered", 99, ""), "typing": 0.15, "typing_until": 1.6},
             sfx=(("text", 2.3, 0.3),), music=0.5),
        # la corrente muore: colpo 3, respiro dopo
        Beat("But then the power dies.", scene="house_ext", clock="10:40 PM",
             hud=(("VISIBILITY 20 FT", VIS, 0.25, "VISIBILITY 0 FT", REDV), mom_del),
             cam={"z": (1.0, 1.06)}, hold=0.5,
             params={"mood": "night", "up_lamp": False, "blanket_line": 1.0, "pin": "YOU · 41 LINDEN ST",
                     "pin_at": (460, 990), "lamps_die_at": 0.0, "line_off_at": 0.9, "to_black": 1.4,
                     "coat": False},
             sfx=(("click", 0.12, 0.3), ("click", 0.44, 0.3), ("click", 0.76, 0.35), ("click", 1.08, 0.4),
                  ("power_down", 0.9, 0.6), ("boom", "@dies", 0.45)), music=0.65),
        # ---------- il registro al buio: 2 righe dette, 2 per chi mette in pausa ----------
        Beat("So you check: nine windows. Four speakers.", scene="living", clock="10:41 PM",
             hud=vis(0, (mom_del,)), hold=0.25, cam={"z": (1.0, 1.06), "c": ((600, 1060), (640, 1020))},
             card={"kind": "ledger", "title": "HOUSE LOG · DAY 1", "y": 530, "rows": [
                 {"label": "WINDOWS COVERED", "from": 0, "to": 9, "fmt": "{}/9", "at": "@nine", "dur": 0.6,
                  "color": [80, 200, 120], "bar": True, "max": 9},
                 {"label": "SPEAKERS UNPLUGGED", "from": 0, "to": 4, "fmt": "{}/4", "at": "@four", "dur": 0.7,
                  "color": [235, 235, 240], "bar": True, "max": 4},
                 {"label": "PHONE · ON SILENT", "value": "100%", "color": [120, 170, 255]},
                 {"label": "WORDS SAID OUT LOUD", "value": "0", "color": [255, 90, 80]}]},
             params={"act": "dark_phone", "dark": 0.85, "unplugged": True, "led": 0.0}, music=0.5),
        # ---------- il minuto: orologio rosso, detto in lettere (Kokoro) ----------
        # la ricevuta cambia davanti a te, in rosso, sotto l'orologio rosso: qualcuno ha aperto la chat
        Beat("Eleven fifty-seven.", clock="11:57 PM", clock_color=RED_CLOCK,
             hud=vis(0, (("MOM · DELIVERED 8:06 PM", DIM, "@fifty", "MOM · READ 11:51 PM", REDV),)), cam={"z": (1.0, 1.12), "c": ((600, 1100), (700, 1000))},
             params={"act": "dark_phone", "dark": 0.93, "unplugged": True, "led": 0.0}, music=0.7),
        Beat("It's Ellie from next door... I can't find you.", who="char", card={"kind": None},
             cam={"z": (1.5, 1.65), "c": ((800, 780), (790, 770))},
             params={"act": "ellie", "dark": 0.9, "unplugged": True, "ring_fabric": True, "ring_dx": 120}),
        # la scelta consapevole: una luce non è una voce (ma piega la #1)
        Beat("A light isn't a voice... would you?", scene="flashlight",
             cam={"z": (1.0, 1.08), "c": ((540, 960), (540, 940))}, music=0.75),
        Beat("Just an inch. Flashlight on.", scene="front_walk", clock="11:58 PM",
             hud=(("VISIBILITY 0 FT", REDV, "@on", "VISIBILITY 8 FT", VIS), mom_read),
             cam={"z": (1.0, 1.15), "c": ((540, 1000), (550, 1080))}, params={"ellie": "lost", "strike": True},
             sfx=(("drag", 0.0, 0.25), ("click", "@on", 0.6))),
        # il telefono della mamma in mano a lei, mentre dice la password
        Beat("Your mom sent me. The password is... blue kite.", who="char", scene="ellie_phone", last_pitch=0.8,
             last_delay=0.1, cam={"z": (1.0, 1.15), "c": ((540, 960), (540, 900))},
             sfx=(("heartbeat", 0.0, 0.45),),
             hud=(("VISIBILITY 8 FT", VIS, "@blue", "VISIBILITY -- FT", REDV, 0.6), mom_read), music=0.85),
        # ---------- il suono prima della parola: due colpi ai vetri, poi il nome ----------
        Beat("", scene="window_tap", clock="11:59 PM", hold=0.62, cam={"z": (1.0, 1.06)}, music=0.95,
             fx=(("shake", 0.12, 10), ("flash", 0.12, (255, 255, 255)), ("shake", 0.42, 16),
                 ("flash", 0.42, (255, 255, 255))),
             sfx=(("tap", 0.12, 0.7, -0.8), ("tap_hard", 0.42, 0.8, 0.4))),
        Beat("It saw your light.", params={"small": True}, cam={"z": (1.04, 1.1)}),
        Beat("No third tap... It's behind her.", scene="front_walk",
             cam={"z": (1.0, 1.1), "c": ((540, 1000), (560, 950))},
             params={"ellie": "near", "shape": 1, "shape_at": "@tap:end"},
             sfx=(("scrape", "@behind-0.6", 0.3), ("heartbeat", "@behind", 0.6))),
        # ---------- il rito della #4 (colpo 4 sulla rivelazione) ----------
        Beat("Rule number four...", scene="phone", cut="flash", clock="",
             cam={"z": (1.9, 2.0), "c": ((540, 940), (540, 950))}, params={"ui": "alert", "glitch": True, "dim_but": (1, 2)},
             sfx=(("alert", 0.0, 0.22), ("glitch", 0.35, 0.35)), music=0.9),
        Beat("You already know rule number four.", scene="front_walk", clock="11:59 PM",
             cam={"z": (1.0, 1.08), "c": ((540, 1080), (540, 1100))},
             card={"kind": "rule", "n": 4, "text": "DON'T ANSWER ANY VOICE", "sub": "EVEN ONE YOU KNOW.", "at": 0.1,
                   "reveal": 0.85, "boom": False},
             params={"ellie": "lean", "shape": "lean"}),
        # ---------- twist su nero: muto vero nella pausa prima di "read", colpo 5 sulla sua ultima consonante ----------
        # "red": Kokoro legge "read" isolato al presente; a schermo resta READ (le didascalie qui sono spente)
        Beat("Nobody said it out loud. But it was... red.", scene="black_title", hold=1.1,
             card={"kind": "black_reveal", "l1": "NOBODY EVER SAID IT.", "l2": "IT WAS READ.", "sub": "MOM · READ 11:51 PM",
                   "l1_at": "@nobody", "l2_at": "@red:end-0.18"},
             mute=(("@red-0.21", 0.12),), music=0.6),
        # ---------- la domanda ----------
        Beat("So... do you answer her?", scene="front_walk", cam={"z": (1.0, 1.08), "c": ((540, 1050), (540, 1080))},
             params={"ellie": "lean", "shape": "lean", "you": True},
             card={"kind": "question", "text": "DO YOU ANSWER HER?", "sub": "TYPE IT. DON'T SAY IT.", "sub_at": 0.8,
                   "boom": False},
             hold=0.2, music=1.0),
        # cartello finale: l'outro torna dalla cassa staccata ed è l'ultimo suono
        Beat("", scene="endcard", clock="", card={"kind": None}, hold=2.0, cam={"z": (1.0, 1.0), "sway": 0.0},
             sfx=(("echo_last", "end", 0.6), ("glitch", 0.45, 0.05)), music=0.3),
    ]
    return Story(
        name="dont_answer", title="DON'T ANSWER", day="DAY 1", place="41 LINDEN ST", beats=beats, scenes=DA.SCENES,
        speed=1.31,
        char_voice="af_heart", char_speed=1.0, char_pitch=2.5, char_name="ELLIE", char_tag="THROUGH THE GLASS",
        char_filter="glass",
        end_label="FOLLOW · STAY QUIET", end_glitch=0.45, end_echo="You already know rule number four.",
        copy={
            "title": "She knows the password nobody said. Do you answer? (DON'T ANSWER · Day 1)",
            "lines": [
                "Imagine it's midnight. Ellie from next door is lost in the fog outside your window, holding your "
                "mom's phone. She knows the family password. Nobody ever said it out loud.",
                "",
                "Now look behind her.",
                "",
                "Rule #4: Do not answer any voice, even one you know.",
                "",
                "So... do you answer her? Type it. Don't say it.",
                "",
                "DON'T ANSWER, Day 1. A Rule Number Four story. Subscribe for Day 2.",
                "",
                "Fiction · animated · synthetic narrator voice",
            ],
            "hashtags": ["#rulenumberfour", "#dontanswer", "#povhorror", "#horrorstory", "#animatedhorror"],
            "tags": ["rule number four", "don't answer", "pov horror", "horror story", "animated horror",
                     "rules horror", "survival story", "what would you do", "scary story", "fog", "day 1",
                     "stickman"],
        },
    )


STORIES = {"dont_answer": dont_answer}
