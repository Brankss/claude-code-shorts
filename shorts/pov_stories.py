"""Storie del format "rules". Ogni storia è una funzione che restituisce una rules.Story."""

from . import dont_answer as DA
from .rules import Beat, Story

GREEN = (60, 190, 90)
VIS = (190, 196, 205)
DIM = (150, 152, 160)
REDV = (255, 120, 110)


def vis(ft, extra=()):
    return ((f"VISIBILITY {ft} FT", VIS if ft else REDV),) + tuple(extra)


def dont_answer():
    """DON'T ANSWER, Day 1: una nebbia che copia le voci. L'allerta dice di non rispondere a nessuna voce,
    nemmeno a una che conosci. A mezzanotte la bambina della casa accanto è là fuori, con il telefono della mamma
    e la password di famiglia che nessuno ha mai detto ad alta voce. E qualcosa dietro di lei."""
    pw = [("password?", True, -9), ("blue kite. never out loud.", False, -9)]
    evening = pw + [("voices stopped. walking home now. stay quiet.", False, -9)]
    mom_del = ("MOM · DELIVERED 8:06 PM", DIM)
    mom_read = ("MOM · READ 11:51 PM", DIM)
    beats = [
        # --- 0-6 s: l'hook, con la contraddizione dentro la prima frase ---
        Beat("Imagine you hear your mom calling from the backyard... while she's texting you. From work.",
             scene="bedroom", clock="6:41 AM", hud=vis(300), music=0.35,
             cam={"z": (1.0, 1.14), "c": ((560, 960), (720, 880))},
             sfx=(("fog", 0.0, 0.5), ("say:af_heart:Sweetie?", "@backyard+0.1", 0.45, 0.6), ("buzz", "@texting", 0.45))),
        Beat("", card={"kind": "title", "dur": 1.0, "hud": True, "y": 820, "size": 210}, hold=1.0,
             sfx=(("say:af_heart:Come outside...", 0.2, 0.25, 0.8),)),
        Beat("She texts: if you hear me outside... that's not me.", scene="phone", card={"kind": None},
             cam={"z": (1.0, 1.32), "c": ((540, 900), (540, 960))},
             params={"ui": "lock", "time": "6:41", "notifs": [
                 ("Mom", "Mom", "at work. people keep hearing family outside", GREEN, -9),
                 ("Mom", "Mom", "if you hear me outside... that's not me.", GREEN, "@that's")]},
             sfx=(("buzz", "@that's", 0.4), ("text", "@that's", 0.4)), music=0.4),
        Beat("Every phone in town screams: don't answer any voice...", scene="phone", clock="6:42 AM", cut="flash",
             cam={"z": (1.0, 1.12), "c": ((540, 880), (540, 960))},
             params={"ui": "alert", "hot": "answer", "line_at": [0.2, 0.5, 0.5, 0.9]},
             sfx=(("alert", 0.0, 0.42), ("alert", 0.25, 0.14, -0.7), ("alert", 0.5, 0.1, 0.7)), music=0.6),
        Beat("Even one you know.", cam={"z": (2.2, 2.45), "c": ((540, 1000), (540, 1010))},
             params={"ui": "alert", "dim_but": (3,)}, scene="phone"),
        Beat("Outside... just fog. Full of voices.", scene="house_ext", clock="6:43 AM", music=0.45,
             cam={"z": (1.0, 1.28), "c": ((470, 1000), (900, 1080))},
             params={"mood": "dawn", "pin": "YOU · 41 LINDEN ST", "rings": [(990, 1080), (120, 980), (700, 760)]},
             sfx=(("say:af_bella:Hello?", "@voices", 0.3, -0.7), ("say:bm_george:Over here...", "@voices+0.5", 0.25, 0.7),
                  ("say:af_nicole:Come out...", "@fog+0.2", 0.2, 0.3))),
        # --- 7:15: il vicino ---
        Beat("Across the street, a man hears his wife calling.", scene="window_view", clock="7:15 AM", hud=vis(200),
             cam={"z": (1.0, 1.25), "c": ((540, 960), (470, 1060))}, cut="fade",
             params={"mood": "dawn", "vis": 0.85, "what": "street", "man": "up", "you": True},
             sfx=(("say:af_bella:Honey?", "@wife", 0.3, -0.8),)),
        Beat("He walks toward her voice...", scene="street_top",
             cam={"z": (1.1, 1.3), "c": ((820, 990), (330, 820)), "r": (0.0, 3.0)}, params={"walk_dur": 2.6},
             sfx=(("steps", 0.1, 0.3),)),
        Beat("She's on the porch. Behind him.", scene="window_view", clock="7:16 AM",
             cam={"z": (1.15, 1.3), "c": ((480, 1040), (420, 1060))},
             params={"mood": "dawn", "vis": 0.75, "what": "street", "man": "up", "walk_at": -0.4, "wife": True,
                     "hook": True, "ellie_out_at": 1.0, "you": True},
             sfx=(("whoosh_down", 1.4, 0.25),), music=0.5),
        # --- RULE #1 ---
        Beat("Rule number one: cover every window.", scene="living", clock="9:00 AM", hud=vis(150),
             cam={"z": (1.0, 1.08), "c": ((760, 1000), (780, 980))},
             card={"kind": "rule", "n": 1, "text": "COVER EVERY WINDOW", "at": 0.3},
             params={"act": "cover", "led": 1.0}, sfx=(("tape", 1.2, 0.5), ("tape", 2.0, 0.4)), music=0.45),
        Beat("If you can see out... it can see in.", card={"kind": None},
             cam={"z": (1.55, 1.75), "c": ((880, 780), (875, 780))},
             params={"act": "strip", "led": 1.0}, sfx=(("boom", 0.3, 0.3), ("thud", "@in", 0.35)), music=0.55),
        # --- RULE #2 ---
        Beat("Rule number two: unplug every speaker. It talks through anything.", scene="living", clock="10:30 AM",
             hud=vis(120), cam={"z": (1.15, 1.25), "c": ((1250, 1100), (1260, 1080))},
             card={"kind": "rule", "n": 2, "text": "UNPLUG EVERY SPEAKER", "at": 0.3},
             params={"act": "unplug", "tv": 1.0, "led": 1.0, "unplug_tv": "speaker", "unplug_spk": "talks"},
             sfx=(("static", 0.0, 0.25), ("say:af_bella:...stay with us...", 0.6, 0.12, 0.2), ("unplug", "@speaker", 0.6),
                  ("unplug", "@talks", 0.6), ("power_off", "@talks+0.1", 0.3))),
        Beat("Next door, Ellie's house is talking... and nobody's home.", scene="window_view", clock="12:02 PM",
             hud=vis(100), card={"kind": None}, cam={"z": (1.0, 1.14), "c": ((540, 940), (560, 900))},
             params={"mood": "day", "vis": 0.6, "what": "ellie", "gap": 420, "tap_word": "home"},
             sfx=(("say:af_heart:Mommy? Daddy?", 0.2, 0.18, 0.3), ("say:bm_george:We're home!", 0.9, 0.16, 0.4),
                  ("tap_soft", "@home", 0.4, 0.4)), music=0.55),
        # --- RULE #3: la password ---
        Beat("Rule number three: pick a family password.", scene="living", clock="3:30 PM", hud=vis(60),
             cam={"z": (1.0, 1.1), "c": ((460, 1000), (420, 980))},
             card={"kind": "rule", "n": 3, "text": "FAMILY PASSWORD", "at": 0.3}, params={"act": "sit", "led": 0.0,
                                                                                        "unplugged": True}),
        Beat("Text it. Never say it.", scene="phone", card={"kind": None},
             cam={"z": (1.0, 1.45), "c": ((540, 900), (470, 720))},
             params={"ui": "chat", "msgs": [("password?", True, 0.0), ("blue kite. never out loud.", False, 0.55)],
                     "typing": 0.15, "typing_until": 0.55, "highlight": "blue kite.", "status": "online"},
             sfx=(("text", 0.0, 0.3), ("text", 0.55, 0.45)), hold=0.9),
        Beat("Anything you say... it can say back.", scene="living", clock="3:31 PM",
             card={"kind": "banner", "title": "ALERT UPDATE", "text": "IT REPEATS WHAT IT HEARS", "at": 0.1},
             cam={"z": (1.1, 1.25), "c": ((560, 1000), (640, 960))},
             params={"act": "listen", "led": 0.0, "unplugged": True, "ring_fabric": True},
             sfx=(("text", 0.1, 0.35), ("echo:back", 0.0, 0.45)), music=0.55),
        # --- tramonto: le voci si fermano ---
        Beat("By sunset, the voices stop. All at once.", scene="house_ext", clock="7:51 PM", hud=vis(50), cut="black",
             card={"kind": None},
             cam={"z": (1.0, 1.1), "c": ((540, 980), (560, 1000))},
             params={"mood": "sunset", "up_lamp": False, "blanket_line": 1.0, "pin": "YOU · 41 LINDEN ST",
                     "pin_at": (460, 990), "rings": [(990, 1080), (120, 980), (700, 760), (300, 1200)],
                     "rings_stop": "once"},
             sfx=(("say:af_bella:Hello?", 0.2, 0.22, -0.6), ("say:bm_george:Over here...", 0.8, 0.2, 0.6),
                  ("say:af_nicole:Come out...", 1.4, 0.18, 0.0)), music=0.3),
        Beat("The man across the street... is back.", scene="window_view", clock="7:52 PM",
             cam={"z": (1.0, 1.2), "c": ((540, 1000), (470, 1150))},
             params={"mood": "sunset", "vis": 0.55, "what": "street", "man": "bent", "porch": False, "hook": False,
                     "gap": 460, "gap_x": 470, "clock": True, "close_at": 2.2}, music=0.6),
        Beat("Your mom heads home... and stops texting.", scene="phone", clock="8:06 PM", hud=vis(20, (mom_del,)),
             cam={"z": (1.0, 1.1), "c": ((540, 900), (540, 860))},
             params={"ui": "chat", "msgs": evening + [("ok. text me every 5 min", True, 0.25)],
                     "receipt": ("Delivered", 99, ""), "typing": 1.1, "typing_until": 2.1},
             sfx=(("text", 0.25, 0.3),), music=0.5),
        # --- blackout ---
        Beat("Then the power dies.", scene="house_ext", clock="10:40 PM",
             hud=(("VISIBILITY 20 FT", VIS, 0.25, "VISIBILITY 0 FT", REDV), mom_del),
             cam={"z": (1.0, 1.06)},
             params={"mood": "night", "up_lamp": False, "blanket_line": 1.0, "pin": "YOU · 41 LINDEN ST",
                     "pin_at": (460, 990), "lamps_die_at": 0.1, "line_off_at": 1.5, "to_black": 1.85}, hold=0.5,
             sfx=(("click", 0.15, 0.3), ("click", 0.47, 0.3), ("click", 0.79, 0.35), ("click", 1.11, 0.4),
                  ("power_down", 1.4, 0.65)), music=0.65),
        # --- mezzanotte ---
        Beat("And in the dark... a small voice.", scene="living", clock="11:57 PM", hud=vis(0, (mom_read,)),
             cam={"z": (1.0, 1.12), "c": ((600, 1100), (700, 1000))},
             params={"act": "dark_phone", "dark": 0.93, "unplugged": True, "led": 0.0}, music=0.7),
        Beat("Hello? It's Ellie... I can't see anything.", who="char", cam={"z": (1.5, 1.65), "c": ((800, 780), (790, 770))},
             params={"act": "ellie", "dark": 0.9, "unplugged": True, "ring_fabric": True, "ring_dx": 120}),
        Beat("Please... say something so I can find you.", who="char", scene="flashlight",
             cam={"z": (1.0, 1.08), "c": ((540, 960), (540, 940))}),
        Beat("You lift the blanket. Flashlight on.", scene="front_walk", clock="11:58 PM",
             hud=(("VISIBILITY 0 FT", REDV, "@on", "VISIBILITY 8 FT", VIS), mom_read),
             cam={"z": (1.0, 1.15), "c": ((540, 1000), (550, 1080))}, params={"ellie": "lost", "strike": True},
             sfx=(("drag", 0.0, 0.25), ("click", "@on", 0.6)), music=0.75),
        Beat("It's Ellie. Same yellow raincoat.", cam={"z": (1.45, 1.65), "c": ((560, 1180), (560, 1180))},
             params={"ellie": "lost"}, hud=vis(8, (mom_read,))),
        Beat("Rule number four...", scene="phone", cut="flash",
             cam={"z": (1.9, 2.0), "c": ((540, 940), (540, 950))}, params={"ui": "alert", "glitch": True, "dim_but": (1, 2)},
             sfx=(("alert", 0.0, 0.22), ("glitch", 0.35, 0.35)), music=0.8),
        Beat("You already know rule number four.", scene="front_walk",
             cam={"z": (1.0, 1.08), "c": ((540, 1080), (540, 1100))},
             card={"kind": "rule", "n": 4, "text": "DON'T ANSWER ANY VOICE", "sub": "EVEN ONE YOU KNOW.", "at": 0.1,
                   "reveal": 0.85},
             params={"ellie": "lost"}),
        Beat("Your mom sent me. The password is... blue kite.", who="char", card={"kind": None}, last_pitch=0.8,
             last_delay=0.1, cam={"z": (1.3, 1.5), "c": ((560, 1200), (560, 1260))}, params={"ellie": "step"},
             hud=(("VISIBILITY 8 FT", VIS, "@blue", "VISIBILITY -- FT", REDV, 0.6), mom_read), music=0.9),
        Beat("Nobody said it out loud. Someone read it.", scene="phone",
             cam={"z": (1.0, 1.06), "c": ((540, 900), (540, 880))},
             params={"ui": "chat", "msgs": evening + [("ok. text me every 5 min", True, -9)],
                     "receipt": ("Read 11:51 PM", -9, "Read 11:51 PM"), "highlight": "blue kite.", "dim": 0.35,
                     "receipt_zoom": "@read"}, hud=vis(8, (mom_read,)),
             sfx=(("tick", "@read", 0.9), ("hit", "@read", 0.6))),
        Beat("She has your mom's phone.", scene="ellie_phone", cam={"z": (1.0, 1.15), "c": ((540, 960), (540, 900))},
             sfx=(("heartbeat", 0.0, 0.5),)),
        # --- i colpi ai vetri ---
        Beat("Behind you... a tap. Kitchen. One.", scene="window_tap", clock="11:59 PM",
             cam={"z": (1.0, 1.06)}, params={"tap_word": "One"},
             sfx=(("whoosh", 0.0, 0.3), ("tap", "@One", 0.7, -0.8)), music=0.95),
        Beat("Hallway. Two.", scene="window_tap", cam={"z": (1.0, 1.08)}, params={"tap_word": "Two", "small": True},
             sfx=(("whoosh", 0.0, 0.3), ("tap_hard", "@Two", 0.8, -0.4))),
        Beat("No third tap... It's behind her.", scene="front_walk",
             cam={"z": (1.0, 1.1), "c": ((540, 1000), (560, 950))},
             params={"ellie": "near", "shape": 1, "shape_at": 0.6}, sfx=(("boom", 0.6, 0.4),)),
        Beat("If she's real... she has seconds.", cam={"z": (1.25, 1.4), "c": ((600, 1000), (600, 1000))},
             params={"ellie": "lean", "shape": "lean"}, sfx=(("heartbeat", 0.0, 0.6),)),
        Beat("So... do you answer her?", cam={"z": (1.0, 1.08), "c": ((540, 1050), (540, 1080))},
             params={"ellie": "lean", "shape": "lean", "you": True},
             card={"kind": "question", "text": "DO YOU ANSWER HER?", "sub": "TYPE IT. DON'T SAY IT.", "sub_at": 0.9},
             hold=0.6, music=1.0),
        Beat("", scene="endcard", clock="", card={"kind": None}, hold=4.3, cam={"z": (1.0, 1.0), "sway": 0.0},
             sfx=(("glitch", 1.4, 0.4), ("echo_last", 1.9, 0.6), ("tap_soft", 3.7, 0.5)), music=0.3),
    ]
    return Story(
        name="dont_answer", title="DON'T ANSWER", day="DAY 1", place="41 LINDEN ST", beats=beats, scenes=DA.SCENES,
        char_voice="af_heart", char_speed=0.9, char_pitch=2.5, char_name="ELLIE", char_tag="THROUGH THE GLASS",
        char_filter="glass",
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
