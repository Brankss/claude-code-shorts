"""Le storie di What If. Ognuna è una funzione che prepara la scena e restituisce (Story, scena).

Regola d'oro: l'escalation è inventata (ed è chiaro che lo è), il twist no. Il dato del twist
deve avere una fonte vera, che finisce anche nella descrizione del video.
"""

import datetime as dt

from . import dorm
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


def tiktok():
    """E se tutti cancellassero TikTok nello stesso istante? Twist: lo vorrebbero quasi tutti, ma nessuno esce per primo.

    Fonte del twist: Bursztyn, Handel, Jiménez-Durán, Roth, "When Product Markets Become Collective Traps:
    The Case of Social Media" (NBER WP 31771, versione nov. 2024; AER 2025). Oltre 1.000 studenti universitari
    USA: per smettere da soli chiedevano circa $55; se smettessero tutti, pagherebbero circa $24; il 58%
    preferirebbe un mondo senza TikTok.
    """
    D = 59.4
    start = dt.datetime(2026, 10, 14, 2, 47, 0)
    H0 = 324_180_000.0           # ore passate su TikTok oggi nel mondo alle 07:47 UTC (stima: ~1 mld di ore al giorno)
    RATE = 1e9 / 86400           # ~11.574 ore al secondo
    T_DEL = dorm.T_OFF           # nella prima parte tempo scena = tempo video
    t_given, t_back = 18.8, 41.2
    end_hold = D - 55.2          # secondi di scena prima del primo frame, nel finale

    def kpi(vt, tl):
        secs = tl.clock_s(vt)
        if vt < T_DEL or vt >= t_back - 0.6:
            return H0 + RATE * secs                  # la realtà: il contatore corre
        if vt < t_given:
            return H0 + RATE * T_DEL                 # tutti hanno cancellato: si ferma
        return max(0.0, secs) / 86400 * 1e9          # ore restituite: un miliardo al giorno

    phone = {"w": 0.21, "c": "phone", "pitch": 18.0}
    room = {"w": 4.4, "c": (-0.35, -0.15), "pitch": 38.0}
    beats = [
        Beat(0.0, text="What if everyone on Earth deleted TikTok at the same time?", hook=True, cam=phone,
             scene=("dorm", 0.0), when=start, live=True, kpi_label="HOURS SCROLLED TODAY"),
        Beat(2.6, cam=room, move=1.6, text="A dorm room in Chicago. 2:47 a.m.", place="DORM ROOM · CHICAGO"),
        Beat(5.4, cam={"w": 1.6, "c": "hero", "dy": -0.25, "pitch": 30.0}, move=1.2,
             text="He said \u201cone more video.\u201d", sub="Three hours ago.", point="phone"),
        Beat(8.4, cam={"w": 3.6, "c": (-0.6, -0.2), "pitch": 40.0}, move=1.4,
             text="Except tonight, every user on Earth deletes it.", kpi2=("TIKTOK USERS", "1,000,000,000+")),
        Beat(11.2, cam={"w": 0.24, "c": "phone", "pitch": 18.0}, move=0.9, text="At the same time. Starting with him."),
        Beat(13.8, cam={"w": 3.4, "c": (-0.7, -0.3), "pitch": 36.0}, move=1.2, text="Asleep in four minutes.",
             kpi2=("SCROLLING NOW", "0"), when=start + dt.timedelta(minutes=4, seconds=13)),
        Beat(15.7, cam={"w": 34.0, "c": "building", "pitch": 26.0}, move=1.1, text="Everyone. Same second."),
        Beat(dorm.T_ALL, fx="flash", fx_dur=0.7),
        Beat(dorm.T_ALL, fx="shake", fx_dur=0.8),
        # Escalation: ogni salto di zoom è un salto di tempo.
        Beat(t_given, cam={"w": 1400.0, "c": (0.0, 0.0)}, move=2.2, when=start + dt.timedelta(days=7, hours=19, minutes=23),
             jump="+1 WEEK", place="HYDE PARK · CHICAGO", text="The whole campus sleeps 8 hours.",
             kpi_label="HOURS GIVEN BACK", kpi2=("AVG SLEEP", "+1H 12M")),
        Beat(22.4, cam={"w": 46_000.0, "c": (-2000.0, 6000.0)}, move=2.2, when=start + dt.timedelta(days=30, hours=15),
             jump="+1 MONTH", place="CHICAGO", text="Chicago: 3 million hours back. Every day.",
             kpi2=("FREE TIME / RESIDENT", "+52 MIN / DAY"), spread=35),
        Beat(26.0, cam={"w": 5_400_000.0, "c": (-880_000.0, -260_000.0)}, move=2.2,
             when=start + dt.timedelta(days=182, hours=11), jump="+6 MONTHS", place="UNITED STATES",
             text="America starts reading again.", kpi2=("BOOK SALES", "+38%"), spread=3000, hatch=(("states", "all"),)),
        Beat(29.6, cam={"w": 17_000_000.0, "c": (0.0, 0.0)}, move=2.2, when=start + dt.timedelta(days=365, hours=7),
             jump="+1 YEAR", place="EARTH", text="Humanity gets 1 billion hours back. Every day.",
             kpi2=("HOURS BACK / DAY", "1,000,000,000"), spread=13000,
             hatch=(("states", "all"), ("countries", "all"))),
        Beat(33.4, cam={"w": 1.3e9, "c": (MOON_POS[0] * 0.45, MOON_POS[1] * 0.45)}, move=2.2,
             when=start + dt.timedelta(days=8 * 365, hours=2), jump="+8 YEARS", place="EARTH-MOON SYSTEM",
             text="Humanity goes back to the Moon.", kpi2=("PHONES ON THE MOON", "0")),
        Beat(36.8, cam={"w": 9.0, "c": "lander", "dy": -2.6, "pitch": 30.0}, move=1.8, scene=("moon", 0.0, "moon"),
             when=start + dt.timedelta(days=8 * 365, hours=5), place="THE MOON"),
        Beat(38.5, cam={"w": 2.6, "c": "astronaut", "dy": -0.4, "pitch": 26.0}, move=1.1,
             text="Nobody films it vertically.", kpi2=("VERTICAL VIDEOS", "0")),
        # Rewind: fuori dalla Luna e giù nella stanza, con orologio e contatori che tornano indietro.
        Beat(40.2, fx="rewind", fx_dur=1.9, cam={"w": 1.6e9, "c": (MOON_POS[0] * 0.5, MOON_POS[1] * 0.5)}, move=1.0,
             text="", when=start - dt.timedelta(seconds=D - t_back), hatch=(), spread=0.0),
        Beat(t_back, cam=room, move=1.2, scene=("dorm", 3.0), place="DORM ROOM · CHICAGO",
             when=start - dt.timedelta(seconds=D - t_back), live=True, kpi_label="HOURS SCROLLED TODAY", kpi2=()),
        # Twist: lo studio vero.
        Beat(42.4, scene=("study", 0.0), place="UNIVERSITY OF CHICAGO", tag="REAL STUDY", fx="hit",
             text="Then economists actually asked.", sub="1,000+ college students. TikTok users."),
        Beat(45.6, text="Quit TikTok alone?", sub="They wanted $55 to do it."),
        Beat(48.8, text="But if EVERYONE quit?", sub="They'd PAY $24 to make it happen."),
        Beat(52.0, text="Most would rather it never existed."),
        Beat(55.2, cam=phone, move=1.4, scene=("dorm", -end_hold), place="DORM ROOM · CHICAGO", tag=None,
             when=start - dt.timedelta(seconds=end_hold), live=True, text="Everyone wants out."),
        Beat(57.2, text="Nobody leaves first.", fx="hit"),
    ]
    story = Story(
        name="tiktok", start=start, origin=(41.7886, -87.5987), duration=D, beats=beats,
        kpi_base=0.0, kpi_format=None, kpi_fn=kpi, kpi_fmt="{:,.0f}", units="imperial",
        palette={"sea": (5, 8, 17), "land": (28, 34, 50), "border": (60, 72, 98), "accent": (255, 190, 110),
                 "dots": (255, 190, 110)},
        labels=(("CHICAGO", 41.8781, -87.6298, 4_000, 400_000, (70, -90)),
                ("LAKE MICHIGAN", 42.6, -87.15, 50_000, 1_500_000, (60, 60))),
        copy={
            "title": "What if everyone deleted TikTok at the same time?",
            "lines": [
                "Economists asked 1,000+ college students how much they'd need to quit TikTok. Alone: about $55. "
                "But if everyone quit at once, they'd pay about $24 to make it happen. Most would rather live in a "
                "world without it.",
                "",
                "Everyone wants out. Nobody leaves first.",
                "",
                "The escalation in the middle is fiction; the study is real.",
                "",
                "Source: Bursztyn, Handel, Jiménez-Durán & Roth, \"When Product Markets Become Collective Traps: "
                "The Case of Social Media\" (NBER Working Paper 31771; American Economic Review, 2025).",
                "Map data: Natural Earth; lakes © OpenStreetMap contributors (ODbL).",
            ],
            "hashtags": ["#tiktok", "#whatif", "#socialmedia", "#screentime"],
            "tags": ["what if", "tiktok", "delete tiktok", "social media", "screen time", "phone addiction",
                     "economics", "study", "doomscrolling", "butterfly effect"],
        },
        sources=("Bursztyn, Handel, Jiménez-Durán, Roth (NBER WP 31771, Nov 2024; AER 2025): ~$55 to quit alone, "
                 "~$24 paid to have everyone quit, 58% prefer a world without TikTok",),
    )
    return story, dorm.DormScene(), {"duration": D}


STORIES = {"zipper": zipper, "tiktok": tiktok}
