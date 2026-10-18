"""Storie del format "rules". Ogni storia è una funzione che restituisce una rules.Story."""

from . import pov_gfx as G
from .rules import Beat, Story
from .stick import POSES, Figure, breathe

YOU = Figure(height=560)


def _test():
    """Storia minima per provare il motore."""
    def bedroom(c, s, b, R):
        G.room(c, (58, 66, 92), (70, 62, 72), horizon=1250)
        G.window(c, 380, 380, 700, 760, lambda c, r: G.skyline(c, *r, mood="dawn", seed=3))
        G.bed(c, 160, 1250, 760)
        YOU.draw(c, 540, 1250, breathe(POSES["sit_up_bed"], s), facing=1)

    def phone(c, s, b, R):
        c.clear(0xFF141216)
        G.phone(c, 540, 960, 520, 1080, lambda c, r: G.alert_screen(c, r, "EMERGENCY ALERT", "EXTREME THREAT", [
            ("STAY INSIDE.", (255, 255, 255), 0.3), ("DO NOT ANSWER", (255, 90, 70), 0.8), ("ANY VOICE.", (255, 190, 70), 1.2)],
            t=s), glow_col=(255, 60, 50), tilt=-4)

    beats = [
        Beat("Imagine you wake up... and the whole street is silent.", scene="bedroom", clock="6:42 AM", music=0.3),
        Beat("", card={"kind": "title"}, hold=1.4, cam={"z": (1.1, 1.18)}),
        Beat("Your phone won't stop buzzing.", scene="phone", card={"kind": None}, sfx=(("buzz", 0.0), ("alert", 0.6)),
             music=0.5),
        Beat("Rule number one: do not answer.", scene="bedroom", clock="7:15 AM",
             card={"kind": "rule", "n": 1, "text": "DON'T ANSWER"}, music=0.6),
        Beat("Hello? It's me. Please... open the door.", who="char", card={"kind": None}, sfx=(("knock", 0.0),),
             music=0.8),
        Beat("So... do you answer?", card={"kind": "question", "text": "DO YOU ANSWER?"}, music=0.9),
        Beat("", scene="endcard", clock="", card={"kind": None}, hold=3.0, cam={"z": (1, 1)}, sfx=(("glitch", 1.4),)),
    ]
    return Story(name="test", title="SAY NOTHING", day="DAY 1", place="HOUSE 12", beats=beats,
                 scenes={"bedroom": bedroom, "phone": phone}, char_name="Mom", char_tag="Through the door",
                 char_filter="door", char_voice="af_heart", copy={"title": "test", "lines": ["test"], "hashtags": [],
                                                                    "tags": []})


STORIES = {"test": _test}
