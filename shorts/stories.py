"""Le storie di What If. Ognuna è una funzione che prepara la scena e restituisce (Story, scena).

Regola d'oro: l'escalation è inventata (ed è chiaro che lo è), il twist no. Il dato del twist
deve avere una fonte vera, che finisce anche nella descrizione del video.
"""

import datetime as dt

from . import highway as hw
from .whatif import MOON_POS, Beat, Story, fmt_dist

DAY = dt.timedelta(days=1)


def zipper():
    """E se tutti si immettessero presto? Il "furbo" che usa la corsia vuota fino alla fine aveva ragione."""
    T0 = 900.0                      # 15 minuti di simulazione prima del primo frame: la coda c'è già
    D = 70.0                        # durata del video
    loop_at = 64.0                  # da qui si torna all'inquadratura iniziale
    tail = D - loop_at              # secondi di scena prima di T0 nel finale, così l'ultimo frame = il primo
    A = hw.run("early", 11, T0 - tail - 2, T0 + 62, hero_at=(T0 - 8, -600.0), switch_t=T0 + 14,
               late_at=[(T0 - 12, -600.0)])
    B = hw.run("zipper", 11, T0 + 45, T0 + 62)
    scene = hw.HighwayScene({"A": A, "B": B}, "imperial", tags=((3.4, 10.4),), switch_sim=T0 + 14)

    start = dt.datetime(2026, 10, 13, 17, 42, 0)
    base = A.backup_at(T0)
    early, zip_ = A.backup_at(T0 + 58), B.backup_at(T0 + 58)
    hero = {"w": 34.0, "c": "hero", "dy": 8.0, "pitch": 42.0}
    t_twist = 50.0
    beats = [
        Beat(0.0, text="What if every driver merged early?", hook=True, cam=hero, scene=("A", T0),
             when=start, live=True, kpi=base, kpi_label="BACKUP"),
        Beat(3.0, text="I-35W, Minneapolis. Rush hour.", sub="Tuesday, 5:42 p.m.", place="I-35W · MINNEAPOLIS"),
        Beat(6.8, text="Every evening, this driver skips the line.", point="hero",
             kpi2=("HONKS PER MINUTE", "11")),
        Beat(10.6, text="Except tonight, every driver merges early."),
        Beat(14.0, text="Starting with him.", point="hero"),
        Beat(17.4, text="Nobody cuts in. Nobody honks.", kpi=base * 0.8, kpi2=("HONKS PER MINUTE", "0"),
             cam={"w": 110.0, "c": "hero", "dy": 26.0, "pitch": 28.0}, move=3.2),
        # Escalation: ogni salto di zoom è un salto di tempo, e la conseguenza è più grande.
        Beat(21.2, cam={"w": 42_000.0, "c": (0.0, 0.0)}, move=2.6, place="MINNEAPOLIS", when=start + 92 * DAY + dt.timedelta(hours=-9),
             jump="+3 MONTHS", text="Minneapolis: commutes 4 minutes shorter.",
             kpi2=("TIME SAVED PER DRIVER", "+4 MIN / DAY"), spread=30),
        Beat(25.6, cam={"w": 1_150_000.0, "c": (-60_000.0, 150_000.0)}, move=2.4, place="MINNESOTA", when=start + 183 * DAY,
             jump="+6 MONTHS", text="Minnesota: road rage down 60%.", kpi2=("ROAD RAGE", "-60%"),
             hatch=(("states", ["Minnesota"]),), spread=420),
        Beat(30.0, cam={"w": 5_400_000.0, "c": (650_000.0, -500_000.0)}, move=2.4, place="UNITED STATES",
             when=start + 380 * DAY + dt.timedelta(hours=5),
             jump="+1 YEAR", text="The US copies Minnesota. Economy: +$9 billion.", kpi2=("US GDP", "+$9 BN"),
             hatch=(("states", "all"),), spread=3200),
        Beat(34.4, cam={"w": 17_000_000.0, "c": (1_500_000.0, -1_200_000.0)}, move=2.4, place="EARTH",
             when=start + 5 * 365 * DAY + dt.timedelta(hours=14),
             jump="+5 YEARS", text="The whole planet merges early.", kpi2=("QUEUE JUMPERS", "0"),
             hatch=(("states", "all"), ("countries", "all")), spread=13000),
        Beat(38.4, cam={"w": 1.3e9, "c": (MOON_POS[0] * 0.45, MOON_POS[1] * 0.45)}, move=2.4, place="EARTH-MOON SYSTEM",
             when=start + 40 * 365 * DAY + dt.timedelta(hours=3),
             jump="+40 YEARS", text="Humanity goes back to the Moon. And builds a highway.",
             kpi2=("LANES ON THE MOON", "2")),
        Beat(42.4, cam={"w": 75.0, "c": "hero", "dy": 14.0, "pitch": 34.0}, move=2.8, scene=("A", T0 + 41, "moon"),
             place="MARE TRANQUILLITATIS · MOON", when=start + 40 * 365 * DAY + dt.timedelta(hours=7),
             text="The first traffic jam on the Moon.", sub="Everyone merges early. It lasts three days.",
             kpi2=("BACKUP", "212 MI")),
        # Rewind: fuori dalla Luna e giù fino alla strada, con orologio e numeri che tornano indietro.
        Beat(47.4, fx="rewind", fx_dur=2.6, cam={"w": 1.6e9, "c": (MOON_POS[0] * 0.5, MOON_POS[1] * 0.5)}, move=1.2,
             text="", when=start + 40 * 365 * DAY + dt.timedelta(hours=8), hatch=(), spread=0.0),
        Beat(48.6, cam={"w": 60.0, "c": "hero", "dy": 10.0, "pitch": 34.0}, move=1.4, scene=("A", T0 + 48.6 - 4),
             kpi=base, kpi2=(), place="I-35W · MINNEAPOLIS",
             when=start - dt.timedelta(seconds=loop_at - t_twist + tail)),
        # Twist: il dato vero.
        Beat(t_twist, text="Minnesota's DOT actually ran the numbers.", sub="Their advice: don't merge early.", fx="hit",
             when=start - dt.timedelta(seconds=loop_at - t_twist + tail), live=True, tag="REALITY CHECK"),
        Beat(54.0, cam={"w": 4_600.0, "c": (0.0, -1_250.0)}, move=2.4, scene=("A", T0 + 48),
             text="Merging early leaves a whole lane empty.", kpi=early, kpi_base=early),
        Beat(55.3, split=1.0),  # le due strade si separano solo a zoom già aperto
        Beat(58.0, text="Zipper merging: backups up to 40% shorter.", sub="Use both lanes. Take turns at the end.",
             kpi=zip_),
        Beat(61.6, text="In Germany, it's the law."),
        Beat(62.2, split=0.0),  # e si richiudono prima di tornare giù sull'eroe
        Beat(loop_at, cam=hero, move=2.2, scene=("A", T0 - tail), text="", kpi=base, kpi_base=base,
             when=start - dt.timedelta(seconds=tail), live=True),
        Beat(loop_at + 1.2, text="The guy who “cut in” was right.", fx="hit"),
    ]
    story = Story(
        name="zipper", start=start, origin=(44.9778, -93.2650), duration=D, beats=beats,
        kpi_base=base, kpi_format=lambda m: fmt_dist(m, "imperial"), units="imperial",
        labels=(("MINNEAPOLIS", 44.9778, -93.2650, 6_000, 300_000, (70, -90)),
                ("ST. PAUL", 44.9537, -93.0900, 9_000, 150_000, (60, 80)),
                ("MINNESOTA", 46.4, -94.6, 500_000, 3_000_000, (110, -60))),
        copy={
            "title": "What if every driver merged early?",
            "lines": [
                "Everyone hates the guy who drives to the end of the closing lane. The data doesn't.",
                "",
                "Minnesota's Department of Transportation says zipper merging (use both lanes, take turns at "
                "the end) can cut the length of a backup by up to 40%. In Germany it's required by law "
                "(StVO §7(4)).",
                "",
                "The escalation in the middle is fiction. The traffic is a real car-following simulation "
                "made in code.",
                "",
                "Sources: MnDOT zipper merge (dot.state.mn.us/zippermerge), German StVO §7 Abs. 4.",
            ],
            "hashtags": ["#zippermerge", "#traffic", "#whatif", "#driving"],
            "tags": ["zipper merge", "what if", "traffic", "merge", "driving", "road rage", "lane closure",
                     "traffic simulation", "minnesota", "butterfly effect"],
        },
        sources=("MnDOT: zipper merge reduces backups by up to 40%", "StVO §7(4) Reißverschlussverfahren"),
    )
    stats = {"backup_start_m": round(base), "backup_early_m": round(early), "backup_zipper_m": round(zip_),
             "zipper_vs_early": round((zip_ - early) / early * 100, 1)}
    return story, scene, stats


STORIES = {"zipper": zipper}
