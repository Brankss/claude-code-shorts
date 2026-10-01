#!/usr/bin/env bash
# Installa Softloop sulla VM di Hermes e programma il job giornaliero. Si può rilanciare senza danni.
#
#   bash hermes/setup.sh                                   # consegna su discord:#yt-shorts alle 7:45
#   bash hermes/setup.sh --deliver telegram --schedule "0 6 * * *"
set -euo pipefail

DELIVER="discord:#yt-shorts"
SCHEDULE="45 7 * * *"
while [ $# -gt 0 ]; do
  case "$1" in
    --deliver) DELIVER="$2"; shift 2 ;;
    --schedule) SCHEDULE="$2"; shift 2 ;;
    *) echo "opzione sconosciuta: $1"; exit 1 ;;
  esac
done

REPO_URL="https://github.com/Brankss/claude-code-shorts.git"
BRANCH="claude/great-gauss-3mek6s"
DIR="${SOFTLOOP_DIR:-$HOME/claude-code-shorts}"
VENV="$HOME/venvs/softloop"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
JOB="softloop-daily"

echo "[1/6] Pacchetti di sistema"
if command -v apt-get >/dev/null 2>&1; then
  SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
  $SUDO apt-get update -qq
  $SUDO apt-get install -y -qq git python3-venv libegl1 libgl1 fontconfig >/dev/null
fi

echo "[2/6] Repo in $DIR"
if [ -d "$DIR/.git" ]; then
  git -C "$DIR" fetch -q origin "$BRANCH"
  git -C "$DIR" checkout -q "$BRANCH"
  git -C "$DIR" pull -q --ff-only origin "$BRANCH"
else
  git clone -q -b "$BRANCH" "$REPO_URL" "$DIR"
fi

echo "[3/6] Ambiente Python in $VENV"
if command -v uv >/dev/null 2>&1; then
  uv venv -q --allow-existing "$VENV" --python 3.11
  uv pip install -q --python "$VENV/bin/python" -r "$DIR/requirements.txt"
else
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
    || { echo "Serve Python 3.10 o più recente (oppure installa uv)"; exit 1; }
  [ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q --upgrade pip
  "$VENV/bin/pip" install -q -r "$DIR/requirements.txt"
fi

echo "[4/6] Script per Hermes e file dei segreti"
mkdir -p "$HERMES_HOME/scripts"
cp "$DIR/hermes/softloop.py" "$HERMES_HOME/scripts/softloop.py"
if [ ! -f "$DIR/.env" ]; then
  cp "$DIR/hermes/env.example" "$DIR/.env"
  echo "      creato $DIR/.env (da compilare a mano con le credenziali YouTube)"
fi
chmod 600 "$DIR/.env"

echo "[5/6] Prova di render"
(cd "$DIR" && "$VENV/bin/python" make.py --format sync --episode 1 --stills 1 --out /tmp/softloop-check >/dev/null)
echo "      ok ($(nproc) core: la generazione richiede circa $(( 12 / $(nproc) + 1 ))-$(( 40 / $(nproc) + 2 )) minuti al giorno)"

echo "[6/6] Job cron di Hermes"
if ! command -v hermes >/dev/null 2>&1; then
  echo "      comando 'hermes' non trovato: crea il job a mano con"
  echo "      hermes cron create \"$SCHEDULE\" --no-agent --script softloop.py --interpreter $VENV/bin/python --deliver \"$DELIVER\" --name $JOB"
elif hermes cron list 2>/dev/null | grep -q "$JOB"; then
  echo "      il job $JOB esiste già: lo lascio com'è"
else
  hermes cron create "$SCHEDULE" --no-agent --script softloop.py \
    --interpreter "$VENV/bin/python" --deliver "$DELIVER" --name "$JOB"
fi

echo
echo "Fatto. Per provarlo subito: hermes cron list  →  hermes cron run <id del job $JOB>"
