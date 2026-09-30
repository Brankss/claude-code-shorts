"""Tutto quello che serve per pubblicare: titolo, descrizione, hashtag, tag, impostazioni e orario.

L'orario di default è pensato per gli Stati Uniti: 13:00 a New York (10:00 in California,
19:00 in Italia), così il video esce quando la costa est è in pausa pranzo, la ovest è sveglia
e in Europa è sera. Si cambia con le variabili d'ambiente YT_PUBLISH_TIME e YT_PUBLISH_TZ.
"""

import datetime as dt
import os
from zoneinfo import ZoneInfo

COPY = {
    "contagio": {
        "title": "Which zodiac sign wins? (Part {ep})",
        "lines": [
            "12 zodiac signs, 48 balls, one winner.",
            "Comment your sign before it ends.",
            "",
            "Every hit converts a ball. A real physics simulation made in code, a new match every episode.",
        ],
        "hashtags": ["#zodiac", "#astrology", "#satisfying", "#simulation"],
        "tags": ["zodiac", "zodiac signs", "which zodiac sign wins", "astrology", "horoscope", "simulation",
                 "physics simulation", "satisfying", "oddly satisfying", "relaxing", "ball simulation"],
    },
    "maze": {
        "title": "Which color reaches the center first? (Part {ep})",
        "lines": [
            "Four colors race through a maze to reach the center.",
            "Pick one and comment your color.",
            "",
            "Every cell takes a random time to fill, so nobody knows the winner in advance. A new maze every episode.",
        ],
        "hashtags": ["#maze", "#satisfying", "#colorrace", "#relaxing"],
        "tags": ["maze", "labyrinth", "color race", "which color wins", "satisfying", "oddly satisfying",
                 "simulation", "relaxing", "liquid", "maze race"],
    },
    "sync": {
        "title": "Wait for them to sync again (Part {ep})",
        "lines": [
            "Every dot plays a note each time it hits the line.",
            "Wait for the last second.",
            "",
            "Each orbit loops a different number of times, so they only line up again at the very end. "
            "Polyrhythm visualized in code.",
        ],
        "hashtags": ["#polyrhythm", "#satisfying", "#relaxing", "#asmr"],
        "tags": ["polyrhythm", "satisfying", "oddly satisfying", "relaxing", "calming", "asmr", "sync",
                 "visual music", "math art", "hypnotic"],
    },
}

# Impostazioni di pubblicazione uguali per tutti i video.
SETTINGS = {
    "category_id": "24",             # Entertainment
    "made_for_kids": False,          # pubblico generale, non rivolto ai bambini
    "synthetic_media": False,        # animazione astratta, niente di realistico da dichiarare
    "license": "youtube",
    "embeddable": True,
    "public_stats": True,
    "default_language": "en",
    "notify_subscribers": True,
}


def publish_at(date):
    """Orario di pubblicazione (UTC) per il video di quel giorno; se è già passato, il giorno dopo."""
    hh, mm = (int(x) for x in os.environ.get("YT_PUBLISH_TIME", "13:00").split(":"))
    tz = ZoneInfo(os.environ.get("YT_PUBLISH_TZ", "America/New_York"))
    when = dt.datetime.combine(date, dt.time(hh, mm), tz)
    now = dt.datetime.now(dt.timezone.utc)
    while when.astimezone(dt.timezone.utc) < now + dt.timedelta(minutes=30):
        when += dt.timedelta(days=1)
    return when.astimezone(dt.timezone.utc)


def build(fmt, episode, date=None):
    c = COPY[fmt]
    title = c["title"].format(ep=episode or 1)
    description = "\n".join(c["lines"]) + "\n\n" + " ".join(c["hashtags"] + ["#shorts"])
    meta = {"title": title, "description": description, "tags": c["tags"], "settings": SETTINGS}
    if date is not None:
        meta["date"] = str(date)
        meta["publish_at"] = publish_at(date).isoformat()
    return meta


def sheet(meta):
    """Scheda di pubblicazione leggibile, da copiare a mano su YouTube."""
    out = [
        "TITOLO", meta["title"], "",
        "DESCRIZIONE", meta["description"], "",
        "TAG", ", ".join(meta["tags"]), "",
        "IMPOSTAZIONI",
        "- Pubblico: No, non è destinato ai bambini",
        "- Contenuti alterati o sintetici: No",
        "- Categoria: Intrattenimento",
        "- Lingua: Inglese",
    ]
    if meta.get("publish_at"):
        t = dt.datetime.fromisoformat(meta["publish_at"])
        rome = t.astimezone(ZoneInfo("Europe/Rome")).strftime("%d/%m %H:%M")
        ny = t.astimezone(ZoneInfo("America/New_York")).strftime("%H:%M")
        out += ["", "PROGRAMMAZIONE", f"{rome} ora italiana ({ny} a New York)"]
    return "\n".join(out) + "\n"
