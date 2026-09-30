"""Carica un video su YouTube e lo programma, con titolo, descrizione, tag e impostazioni dal .json accanto.

    python publish.py out/daily/2026-10-01_maze.mp4             # carica e programma
    python publish.py out/daily/2026-10-01_maze.mp4 --dry-run   # mostra cosa invierebbe, senza caricare

Credenziali (variabili d'ambiente, vedi docs/YOUTUBE_SETUP.md):
    YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN

Attenzione: finché il progetto Google Cloud non ha passato l'audit delle YouTube API,
YouTube blocca come privato ogni video caricato così, e non si può più rendere pubblico.
"""

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from shorts import publishing

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"


def access_token():
    missing = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(k)]
    if missing:
        sys.exit(f"Mancano le variabili d'ambiente: {', '.join(missing)} (vedi docs/YOUTUBE_SETUP.md)")
    data = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=data)) as r:
        return json.load(r)["access_token"]


def body(meta, publish_at):
    s = meta["settings"]
    return {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta["description"],
            "tags": meta["tags"],
            "categoryId": s["category_id"],
            "defaultLanguage": s["default_language"],
        },
        "status": {
            # Un video programmato si carica privato e diventa pubblico da solo a publishAt.
            "privacyStatus": "private",
            "publishAt": publish_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "selfDeclaredMadeForKids": s["made_for_kids"],
            "containsSyntheticMedia": s["synthetic_media"],
            "license": s["license"],
            "embeddable": s["embeddable"],
            "publicStatsViewable": s["public_stats"],
        },
    }


def upload(video, payload, token, notify):
    size = video.stat().st_size
    params = urllib.parse.urlencode({"uploadType": "resumable", "part": "snippet,status",
                                     "notifySubscribers": str(notify).lower()})
    init = urllib.request.Request(
        f"{UPLOAD_URL}?{params}", data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
    with urllib.request.urlopen(init) as r:
        location = r.headers["Location"]
    put = urllib.request.Request(location, data=video.read_bytes(), method="PUT",
                                 headers={"Content-Type": "video/mp4", "Content-Length": str(size)})
    with urllib.request.urlopen(put, timeout=600) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    meta_path = args.video.with_suffix(".json")
    meta = json.loads(meta_path.read_text())
    date = dt.date.fromisoformat(meta["date"]) if meta.get("date") else dt.date.today()
    when = publishing.publish_at(date)
    payload = body(meta, when)

    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    try:
        res = upload(args.video, payload, access_token(), meta["settings"]["notify_subscribers"])
    except urllib.error.HTTPError as e:
        sys.exit(f"Richiesta a Google fallita ({e.code}): {e.read().decode(errors='replace')}")
    meta["youtube"] = {"id": res["id"], "url": f"https://youtube.com/shorts/{res['id']}",
                       "publish_at": when.isoformat()}
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False, default=str))
    print(f"caricato: {meta['youtube']['url']} (pubblicazione {when.isoformat()})")


if __name__ == "__main__":
    main()
