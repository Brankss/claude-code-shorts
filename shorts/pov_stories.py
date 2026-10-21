"""Storie del format "rules". Ogni storia è una funzione che restituisce una rules.Story."""

import numpy as np

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


def low_tide():
    """LOW TIDE, Day 1: "The Road". Gli zombie non sanno nuotare, quindi l'isola di Eli è salva... finché la
    marea scende e il mare diventa una strada. Eli è dalla parte sbagliata a 9 minuti dall'allagamento; il nonno,
    per abitudine, suona la campana; il suono sull'acqua porta 14 morti sulla strada dietro di lui; il box sui pali
    lo salva e la marea li copre. A mezzanotte meno venti l'acqua scende: non sono annegati.

    Ogni numero nasce da qualcosa che si vede (il cartello, la campana, il palo in pollici, la scala dipinta) e
    l'ora dell'HUD muove la marea di tutte le scene (low_tide.tide). Vedi docs/LOW_TIDE.md."""
    from . import low_tide as LT
    from . import low_tide_audio  # noqa: F401  (registra gli effetti in rules_audio.SFX)
    rising =(("TIDE ↑ RISING", (150, 200, 255)),)
    falling = (("TIDE ↓ FALLING", REDV),)
    beats = [
        # ---------- hook: il genere entro mezzo secondo, la strada che esce dal mare su "out" (colpo 1) ----------
        Beat("Zombies can't swim. So Eli's island is safe... until the tide goes out.", scene="world", clock="",
             cam={"z": (1.45, 1.0), "c": ((-60, 900), (470, 960))}, music=0.35,
             params={"act": "hook", "h": 17.35, "hit_at": "@swim-0.05", "drain_at": "@out-0.2"},
             sfx=(("wave", "@swim-0.45", 0.7, 0.2), ("drain", "@out-0.25", 0.6), ("boom", "@out", 0.5))),
        Beat("Twice a day, the sea becomes a road.", scene="bay", cut="fade",
             cam={"z": (1.0, 1.06), "c": ((540, 1080), (540, 1060))},
             card={"kind": "title", "boom": False, "dur": 2.0, "y": 260, "size": 170, "hud": True},
             params={"act": "lapse", "lapse": True}, sfx=(("drain", 0.4, 0.3), ("wave", 1.6, 0.3))),
        # ---------- 6:04: dalla parte sbagliata. Il cartello dà il 9:00 e l'1:46 ----------
        Beat("Day one.", scene="world", clock="6:04 PM", hud=rising, card={"kind": None}, hold=0.4,
             cam={"z": (1.75, 1.8), "c": ((-260, 860), (-250, 860))}, music=0.45,
             params={"act": "arrive", "slap_at": "@one-0.05"},
             sfx=(("run_steps", 0.0, 0.4), ("thud", "@one", 0.7))),
        Beat("The road floods in nine minutes...", scene="sign", cam={"z": (1.0, 1.08), "c": ((540, 860), (540, 840))},
             params={"peel_at": "@nine"}, sfx=(("click", "@nine", 0.4),)),
        Beat("and Eli's on the wrong side.", scene="world", cam={"z": (2.3, 2.4), "c": ((-290, 800), (-280, 800))},
             params={"act": "hide", "dies_at": "@wrong"}, sfx=(("power_off", "@wrong", 0.25),)),
        # ---------- l'allarme li porta via; lui va in silenzio ----------
        Beat("He sets off a car alarm.", scene="world", cam={"z": (2.3, 2.2), "c": ((-330, 760), (-360, 740))},
             params={"act": "throw", "throw_at": "@sets"}, sfx=(("whoosh", "@car", 0.3),)),
        Beat("The dead run to the sound.", scene="bay", cam={"z": (1.9, 1.95), "c": ((370, 1650), (360, 1650))},
             params={"act": "run", "go_at": "@run-0.2", "alarm": True},
             sfx=(("car_alarm", 0.0, 0.45, -0.6), ("run_crowd", "@run", 0.45, -0.3)), music=0.55),
        Beat("So Eli walks. Silent. But silent is slow.", clock="6:09 PM", roll=2.4, scene="bay",
             cam={"z": (1.3, 1.35), "c": ((560, 1260), (560, 1220))},
             params={"act": "walk", "alarm": True}, duck=(("@Silent", 1.4, 0.85),),
             sfx=(("car_alarm", 0.0, 0.22, -0.7),), music=0.4),
        Beat("The alarm dies...", clock="6:12 PM", scene="bay", cam={"z": (1.35, 1.4), "c": ((560, 1220), (560, 1200))},
             params={"act": "walk", "alarm": True, "alarm_off": "@dies", "alarm_off_tag": True},
             sfx=(("car_alarm", 0.0, 0.22, -0.7), ("alarm_stop", "@dies", 0.35, -0.7))),
        Beat("and the sea gets there first.", clock="6:13 PM", roll=1.2,
             params={"act": "walk", "alarm": True, "alarm_off": -1, "short": "@first", "flats_label": True},
             sfx=(("water_rush", 0.2, 0.45),)),
        # ---------- il nonno: vede solo l'acqua e il nipote. Il suono è un gesto d'amore (colpo 2) ----------
        Beat("Grandpa sees the water...", scene="binoc", cam={"z": (1.0, 1.12), "c": ((560, 1080), (570, 1120))},
             sfx=(("static", 0.0, 0.08),), music=0.45),
        Beat("and rings the bell. For forty years, it's meant: come home.", scene="gallery",
             cam={"z": (1.0, 1.08), "c": ((540, 900), (520, 880))}, params={"grab_at": 0.0, "ring_at": "@bell"},
             sfx=(("bell", "@bell", 0.8, 0.4), ("boom", "@bell", 0.4), ("bell", "@years", 0.55, 0.4),
                  ("bell", "@home", 0.55, 0.4)), music=0.5),
        Beat("But over calm water...", scene="world", clock="6:14 PM",
             cam={"z": (2.6, 2.7), "c": ((150, 900), (150, 890))}, params={"act": "walk_side", "turn_at": 0.12},
             sfx=(("bell", 0.15, 0.4, 0.7),)),
        Beat("sound carries.", scene="bay", cam={"z": (1.0, 1.02), "c": ((540, 1080), (540, 1060))},
             params={"act": "rings", "ring_at": 0.0, "calm": True}, sfx=(("bell", 0.0, 0.35, 0.6),)),
        Beat("Five. Ten. Fourteen... on the road behind him.", clock="6:15 PM", scene="bay",
             cam={"z": (1.55, 1.6), "c": ((540, 1440), (540, 1400))},
             params={"act": "count", "c1": "@Five", "c2": "@Ten", "c3": "@Fourteen", "calm": True},
             sfx=(("bell", "@Five-0.4", 0.4, 0.6), ("bell", "@Ten-0.4", 0.4, 0.6), ("bell", "@Fourteen-0.4", 0.4, 0.6),
                  ("run_crowd", "@Five", 0.4, -0.3)), music=0.6),
        # ---------- il bordo delle FLATS: guadare no, il box sì ----------
        Beat("Ahead: a quarter mile of water, rising. Six inches of moving water can knock you down.",
             scene="world", clock="6:19 PM", cam={"z": (1.6, 1.5), "c": ((450, 960), (470, 940))},
             params={"act": "edge", "h": (18.30, 18.333), "ghost_at": "@Six-0.1"},
             sfx=(("water_rush", 0.0, 0.3), ("splash", "@down", 0.35))),
        Beat("Last resort: a box on stilts. Some tidal roads really have them.", clock="6:20 PM",
             cam={"z": (1.6, 1.3), "c": ((420, 980), (430, 860))},
             params={"act": "run", "run_at": "@box", "head_at": "@stilts", "chip_at": "@Some"},
             sfx=(("run_steps", "@box", 0.35),), music=0.65),
        Beat("He climbs. He hauls the rope ladder up.", clock="6:21 PM",
             cam={"z": (1.5, 1.55), "c": ((420, 900), (430, 900))},
             params={"act": "climb", "in_at": "@hauls-0.25", "haul_at": "@hauls", "arrive_at": "@rope-0.3"},
             sfx=(("ladder", "@climbs", 0.4), ("ladder", "@hauls", 0.5), ("run_crowd", 0.2, 0.45, -0.4))),
        # ---------- il suono costa: il box trema (colpo 3); Biscuit zitto ----------
        Beat("But the ladder clatters... and the box shakes. So Biscuit... not one bark.", scene="world",
             cam={"z": (2.35, 2.45), "c": ((LT.XB + 30, 990), (LT.XB + 30, 1000))},
             params={"act": "shake", "cutaway": True, "shove_at": "@shakes-0.3", "zip_at": "@not-0.35",
                     "calm_at": "@bark"},
             fx=(("shake", "@shakes-0.3", 16), ("shake", "@shakes+0.35", 10)),
             sfx=(("ladder", "@clatters", 0.55), ("thud", "@shakes-0.3", 0.8), ("boom", "@shakes-0.3", 0.45),
                  ("creak", "@shakes", 0.5), ("yip", "@Biscuit-0.5", 0.35), ("zip", "@not-0.35", 0.4)),
             duck=(("@not", 1.3, 0.9),), music=0.7),
        # ---------- la marea sale: 4, 5, 6 piedi, le teste spariscono (IN SIGHT 14 -> 0 solo sul 6) ----------
        Beat("Four feet.", clock="7:34 PM", cut="black", cam={"z": (2.05, 2.1), "c": ((500, 1000), (500, 990))},
             params={"act": "rise", "tick_at": 0.0, "cutaway": True}, sfx=(("water_rise", 0.0, 0.4),), music=0.5),
        Beat("Five.", clock="7:55 PM", params={"act": "rise", "gauge_hot": 5, "cutaway": True}),
        Beat("Six... and the sea swallows them.", clock="8:20 PM", roll=2.1,
             params={"act": "rise", "gauge_hot": 6, "egg_at": "@swallows:end+0.2", "cutaway": True}, hold=0.35,
             sfx=(("gulp", "@sea", 0.4),)),
        # ---------- il respiro: l'unico verde (IN SIGHT 0) ----------
        Beat("Zero in sight. The road opens at one forty-six.", clock="10:00 PM", hold=0.5,
             cam={"z": (1.6, 1.65), "c": ((LT.XB + 60, 900), (LT.XB + 60, 900))},
             params={"act": "high", "cutaway": True, "insight": False},
             card={"kind": "ledger", "title": "REFUGE BOX · NIGHT 1", "y": 520, "rows": [
                 {"label": "IN SIGHT", "from": 14, "to": 0, "at": "@Zero", "dur": 0.8, "color": [90, 220, 120]},
                 {"label": "ROAD OPENS", "value": "1:46 AM", "color": [255, 200, 90]},
                 {"label": "HIGH TIDE · FLOOR AT 9", "value": "8 FT", "color": [120, 180, 255], "bar": True,
                  "max": 9, "fill": 8},
                 {"label": "PHONE", "value": "0%", "color": [255, 90, 80]}]},
             music=0.35),
        # ---------- il minuto: Biscuit prima, poi tre graffi bagnati, poi le parole ----------
        Beat("Eleven thirty-nine. Biscuit stares down.", clock="11:39 PM", clock_color=RED_CLOCK, hud=falling,
             card={"kind": None}, hold=1.0, cam={"z": (3.3, 3.5), "c": ((LT.XB + 10, 800), (LT.XB + 10, 810))},
             params={"act": "freeze", "cutaway": True, "freeze_at": "@thirty", "hand_at": "@down"},
             sfx=(("wet_scrape", "@down:end+0.15", 0.5), ("wet_scrape", "@down:end+0.45", 0.55),
                  ("wet_scrape", "@down:end+0.72", 0.6)), duck=((0.0, 2.5, 0.8),), music=0.7),
        Beat("The water's back to six feet.", cam={"z": (2.2, 2.3), "c": ((LT.STILTS[1], 1010), (LT.STILTS[1], 1000))},
             params={"act": "gauge_down", "h": (23.64, 23.66), "gauge_hot": 6, "cutaway": True},
             sfx=(("drip", 0.3, 0.4),)),
        # ---------- la rivelazione: il fascio del faro, 1, 6, 14 (colpo 4) ----------
        Beat("One head... six... all fourteen. Looking up.", scene="down", clock="11:52 PM", roll=3.0,
             cam={"z": (1.0, 1.1), "c": ((540, 1000), (540, 1020))},
             params={"s1": "@One", "s2": "@six", "s3": "@fourteen"},
             fx=(("shake", "@fourteen", 12),),
             sfx=(("beam", "@One-0.2", 0.3), ("beam", "@six-0.2", 0.3), ("beam", "@fourteen-0.2", 0.3),
                  ("boom", "@fourteen", 0.5), ("heartbeat", "@Looking", 0.4)), music=0.9),
        # ---------- twist su nero: muto vero prima dell'ultima parola, colpo 5 sulla sua ultima consonante ----------
        Beat("Zombies can't swim... They don't drown.", scene="black", clock="", hold=1.0,
             card={"kind": "black_reveal", "l1": "ZOMBIES CAN'T SWIM.", "l2": "THEY DON'T DROWN.",
                   "l1_at": "@Zombies", "l2_at": "@drown:end-0.18"},
             mute=(("@drown-0.2", 0.12),), music=0.6),
        # ---------- cartello finale: la minaccia di domani. L'ultimo suono è la campana ----------
        Beat("At dawn... Grandpa rings the bell.", scene="end_map", caption=False, hold=1.5, card={"kind": None},
             cam={"z": (1.0, 1.04), "c": ((540, 960), (540, 980)), "sway": 0.3},
             params={"l1_at": 0.1, "l2_at": "@rings", "l3_at": "@bell:end+0.15"},
             sfx=(("bell", "@bell:end+0.35", 0.55, 0.5),), music=0.3),
    ]
    return Story(
        name="low_tide", title="LOW TIDE", day="DAY 1", place="WREN ISLAND", beats=beats, scenes=LT.SCENES,
        speed=1.32, bed=sea_bed,
        copy={
            "title": "Zombies can't swim... so why is the road the scariest place? (LOW TIDE · Day 1)",
            "lines": [
                "Zombies can't swim. So Eli's island is safe, until the tide goes out and the sea becomes a road.",
                "",
                "Nine minutes before the road floods, he's on the wrong side. Then Grandpa rings the bell.",
                "",
                "How would you warn Grandpa without making a sound?",
                "",
                "LOW TIDE, Day 1. Follow for Day 2.",
                "",
                "Real life: tidal roads publish safe crossing times. Never race the tide, never walk into "
                "moving water.",
                "Fiction · animated · synthetic narrator voice",
            ],
            "hashtags": ["#lowtide", "#zombie", "#animatedstory", "#survival", "#horrorstory"],
            "tags": ["low tide", "zombie story", "zombies can't swim", "tidal road", "causeway", "survival story",
                     "animated horror", "what would you do", "refuge box", "day 1", "stickman", "cliffhanger"],
        },
    )


def sea_bed(tl, D, rng):
    """Mare e vento per tutto il video: risacca lenta, più forte sulle scene all'aperto."""
    from . import rules_audio as RA
    n = int(D * RA.SR)
    t = np.arange(n) / RA.SR
    surf = RA._f(rng.normal(0, 1, n), "band", [180, 1400]) * (0.55 + 0.45 * np.sin(2 * np.pi * t / 7.5) ** 2)
    wind = RA._f(rng.normal(0, 1, n), "band", [400, 2600]) * (0.4 + 0.25 * np.sin(2 * np.pi * t / 11 + 1))
    x = 0.05 * surf + 0.02 * wind
    fade = np.minimum(1, t / 0.6) * np.minimum(1, (D - t) / 0.8)
    return x * fade


STORIES = {"low_tide": low_tide, "dont_answer": dont_answer}
