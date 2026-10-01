"""Job giornaliero di Softloop per Hermes Agent (cron senza LLM, zero token).

Hermes lo lancia una volta al giorno e consegna tutto quello che stampa sul canale scelto
(es. discord:#yt-shorts): le righe "MEDIA:/percorso" diventano allegati video nativi.
Se qualcosa va storto esce con errore e Hermes manda l'avviso.

Cosa fa:
1. aggiorna il repo (così le modifiche fatte con Claude arrivano da sole sulla VM)
2. genera il video del giorno con daily.py
3. se YT_AUTO_PUBLISH=1 lo carica su YouTube e lo programma (publish.py)
4. stampa titolo, descrizione, tag, impostazioni e orario, più il video in versione sotto 10 MB

Si installa con hermes/setup.sh; i segreti stanno in <repo>/.env (mai nel repo).
"""

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(os.environ.get("SOFTLOOP_DIR", "~/claude-code-shorts")).expanduser()
BRANCH = os.environ.get("SOFTLOOP_BRANCH", "claude/great-gauss-3mek6s")
FORMAT_NAMES = {"contagio": "Contagio", "maze": "Labirinto", "sync": "Sync"}


def load_env(path):
    """Legge KEY=VALUE da un file .env senza sovrascrivere variabili già presenti."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def run(cmd, what):
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        tail = "\n".join((r.stderr or r.stdout).strip().splitlines()[-15:])
        print(f"Softloop: {what} fallito.\n```\n{tail}\n```")
        sys.exit(1)
    return r.stdout


def self_update():
    """Se nel repo c'è una versione nuova di questo script, la copia al posto suo (vale dal giorno dopo)."""
    new = REPO / "hermes" / "softloop.py"
    me = Path(__file__).resolve()
    if new.exists() and new.resolve() != me and new.read_bytes() != me.read_bytes():
        me.write_bytes(new.read_bytes())


def main():
    if not (REPO / ".git").exists():
        print(f"Softloop: repo non trovato in {REPO}. Lancia hermes/setup.sh oppure imposta SOFTLOOP_DIR.")
        sys.exit(1)
    run(["git", "pull", "--ff-only", "origin", BRANCH], "aggiornamento del repo")
    self_update()
    load_env(REPO / ".env")
    sys.path.insert(0, str(REPO))
    from shorts.produce import small_copy  # noqa: E402  (dopo il pull, dal repo aggiornato)

    today = dt.datetime.now(ZoneInfo("Europe/Rome")).date()
    run([sys.executable, "daily.py", "--date", str(today)], "generazione del video")
    videos = sorted((REPO / "out" / "daily").glob(f"{today}_*.mp4"))
    videos = [v for v in videos if not v.stem.endswith("_discord")]
    if not videos:
        print(f"Softloop: daily.py non ha prodotto nessun video per il {today}.")
        sys.exit(1)
    video = videos[0]
    meta_path = video.with_suffix(".json")

    status = None
    if os.environ.get("YT_AUTO_PUBLISH") == "1":
        r = subprocess.run([sys.executable, "publish.py", str(video)], cwd=REPO, capture_output=True, text=True)
        if r.returncode == 0:
            yt = json.loads(meta_path.read_text()).get("youtube", {})
            status = f"Caricato e programmato su YouTube: {yt.get('url', '?')}"
        else:
            err = " ".join((r.stderr or r.stdout).split()) or "errore sconosciuto"
            status = f"⚠ Upload su YouTube fallito, va pubblicato a mano: {err[:300]}"

    meta = json.loads(meta_path.read_text())
    when = dt.datetime.fromisoformat(meta["publish_at"])
    rome = when.astimezone(ZoneInfo("Europe/Rome")).strftime("%d/%m alle %H:%M")
    ny = when.astimezone(ZoneInfo("America/New_York")).strftime("%H:%M")
    if status is None:
        status = f"Da pubblicare a mano il {rome} ora italiana ({ny} a New York)"
    else:
        status += f"\nUscita: {rome} ora italiana ({ny} a New York)"

    small = small_copy(video, video.with_name(video.stem + "_discord.mp4"))
    fmt = FORMAT_NAMES.get(meta["format"], meta["format"])
    lines = [
        f"**Softloop · {fmt} #{meta['episode']}** · {today.strftime('%d/%m/%Y')}",
        status,
        "",
        "**Titolo**",
        meta["title"],
        "",
        "**Descrizione**",
        meta["description"],
        "",
        "**Tag**",
        ", ".join(meta["tags"]),
        "",
        "**Impostazioni**",
        "Non destinato ai bambini · Nessun contenuto sintetico · Intrattenimento · Inglese",
        "",
        f"MEDIA:{small.resolve()}",
    ]
    print("\n".join(lines))

    # Pulizia: tiene solo gli ultimi 14 giorni di video sulla VM.
    cutoff = today - dt.timedelta(days=14)
    for f in (REPO / "out" / "daily").glob("*"):
        try:
            if dt.date.fromisoformat(f.name[:10]) < cutoff:
                f.unlink()
        except ValueError:
            pass


if __name__ == "__main__":
    main()
