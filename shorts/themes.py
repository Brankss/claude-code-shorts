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


# 12 tinte morbide ma distinguibili su sfondo scuro.
ZODIAC = [
    Team("Aries", "♈", _hex("#E0625C")),
    Team("Taurus", "♉", _hex("#7DBB7B")),
    Team("Gemini", "♊", _hex("#EBD27A")),
    Team("Cancer", "♋", _hex("#8FCBE6")),
    Team("Leo", "♌", _hex("#EFA25A")),
    Team("Virgo", "♍", _hex("#BCD57E")),
    Team("Libra", "♎", _hex("#EA9EC0")),
    Team("Scorpio", "♏", _hex("#A98BE0")),
    Team("Sagittarius", "♐", _hex("#C3C8D2")),
    Team("Capricorn", "♑", _hex("#C4A386")),
    Team("Aquarius", "♒", _hex("#6C98E4")),
    Team("Pisces", "♓", _hex("#6CCBBA")),
]

# Quattro colori per i format a 4 squadre (Labirinto).
COLORS4 = [
    Team("Red", "", _hex("#E0625C")),
    Team("Yellow", "", _hex("#EBD27A")),
    Team("Blue", "", _hex("#6C98E4")),
    Team("Green", "", _hex("#7DBB7B")),
]

THEMES = {
    "zodiac": {
        "teams": ZODIAC,
        "title": ["Which zodiac", "sign wins?"],
        "subtitle": "Comment your sign before it ends",
    },
}
