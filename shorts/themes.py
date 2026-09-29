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


# 12 tinte ben distinte su sfondo scuro (ruota cromatica completa).
ZODIAC = [
    Team("ARIES", "♈", _hex("#FF3B3B")),
    Team("TAURUS", "♉", _hex("#2ECC71")),
    Team("GEMINI", "♊", _hex("#FFD60A")),
    Team("CANCER", "♋", _hex("#5AC8FA")),
    Team("LEO", "♌", _hex("#FF9F0A")),
    Team("VIRGO", "♍", _hex("#A3E635")),
    Team("LIBRA", "♎", _hex("#FF6FB5")),
    Team("SCORPIO", "♏", _hex("#C04BFF")),
    Team("SAGITTARIUS", "♐", _hex("#6C63FF")),
    Team("CAPRICORN", "♑", _hex("#E0B084")),
    Team("AQUARIUS", "♒", _hex("#2F80FF")),
    Team("PISCES", "♓", _hex("#14D9C4")),
]

THEMES = {
    "zodiac": {
        "teams": ZODIAC,
        "title": ["WHICH ZODIAC", "SIGN WINS?"],
        "subtitle": "COMMENT YOUR SIGN BEFORE IT ENDS",
        "hashtags": ["#zodiac", "#astrology", "#simulation", "#satisfying", "#shorts"],
    },
}
