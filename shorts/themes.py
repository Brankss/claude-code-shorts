"""Squadre riutilizzabili tra le modalità. Ogni squadra: nome, glifo, colore."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Team:
    name: str
    glyph: str
    color: tuple  # (r, g, b)


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# 12 tinte piene e distinguibili su sfondo scuro (piene, non neon: devono restare piacevoli).
ZODIAC = [
    Team("Aries", "♈", _hex("#FF5A50")),
    Team("Taurus", "♉", _hex("#43C463")),
    Team("Gemini", "♊", _hex("#FFD23F")),
    Team("Cancer", "♋", _hex("#4FC8F5")),
    Team("Leo", "♌", _hex("#FF953A")),
    Team("Virgo", "♍", _hex("#B4E043")),
    Team("Libra", "♎", _hex("#FF74B6")),
    Team("Scorpio", "♏", _hex("#A66CFF")),
    Team("Sagittarius", "♐", _hex("#DCE1EA")),
    Team("Capricorn", "♑", _hex("#D9A066")),
    Team("Aquarius", "♒", _hex("#3F82FF")),
    Team("Pisces", "♓", _hex("#21D4B4")),
]

# Quattro colori per i format a 4 squadre (Labirinto).
COLORS4 = [
    Team("Red", "", _hex("#FF5A50")),
    Team("Yellow", "", _hex("#FFD23F")),
    Team("Blue", "", _hex("#3F82FF")),
    Team("Green", "", _hex("#43C463")),
]

THEMES = {
    "zodiac": {
        "teams": ZODIAC,
        "title": ["Which zodiac", "sign wins?"],
        "subtitle": "Comment your sign before it ends",
    },
}
