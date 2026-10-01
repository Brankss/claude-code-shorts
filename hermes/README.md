# Softloop su Hermes Agent

Hermes genera lo Short ogni giorno sulla sua VM e lo manda sul canale Discord **#yt-shorts** con video e dettagli: titolo, descrizione, tag, impostazioni e orario di uscita.
- È un cron **senza LLM**, quindi zero token.
- Se `YT_AUTO_PUBLISH=1`, carica e programma anche su YouTube.

## 1. Il messaggio da mandare a Hermes

Copialo così com'è:

```
Installa e programma Softloop, il mio generatore di YouTube Shorts.

1. Clona https://github.com/Brankss/claude-code-shorts (branch claude/great-gauss-3mek6s) in ~/claude-code-shorts, poi esegui:
   bash ~/claude-code-shorts/hermes/setup.sh
   Fa tutto lui: pacchetti di sistema (usa sudo se serve), ambiente Python, script e job cron "softloop-daily" che consegna su discord:#yt-shorts.
2. Controlla con `hermes cron list` che il job softloop-daily esista, poi lanciarlo una volta subito con `hermes cron run <id>` per provarlo: su #yt-shorts deve arrivare un messaggio con video e dettagli.
3. Dimmi com'è andata: id del job, prossima esecuzione, eventuali errori.

Regole: non modificare il codice del repo e non leggere né modificare ~/claude-code-shorts/.env, contiene segreti e lo compilo io.
```

Il bot di Hermes deve poter scrivere e allegare file nel canale #yt-shorts del tuo server Discord.

## 2. I segreti (li metti tu, non Hermes)

Entra nella VM:

```
ssh -i "C:\Users\lacuf\Downloads\hermes_key.pem" branko@20.91.131.120
nano ~/claude-code-shorts/.env
```

Compila `YT_CLIENT_ID`, `YT_CLIENT_SECRET` e `YT_REFRESH_TOKEN` (come ottenerli è in `docs/YOUTUBE_SETUP.md`). Poi verifica il collegamento:

```
cd ~/claude-code-shorts && set -a && . ./.env && set +a
~/venvs/softloop/bin/python publish.py out/daily/<un video>.mp4 --test
```

- **Il video di prova non risulta "Bloccato"** in YouTube Studio: metti `YT_AUTO_PUBLISH=1` nel `.env` e da lì Hermes pubblica da solo.
- **Risulta "Bloccato"**: serve l'audit di Google. Nel frattempo Hermes ti manda il video su Discord e lo carichi a mano.

I segreti non vanno mai in chat, né con Claude né con Hermes. Restano solo nel file `.env` sulla VM.

## Come funziona

- **Orario**: il job parte alle 7:45 nell'orario della VM (su Azure di solito è UTC, quindi le 9:45 in Italia). Il video esce alle 19:00 italiane, quindi c'è tutto il margine.
- **Aggiornamenti automatici**: a ogni giro `softloop.py` fa `git pull`, quindi le modifiche fatte con Claude sul repo arrivano da sole. Se cambia anche lo script stesso, si aggiorna e la nuova versione vale dal giorno dopo.
- **Video su Discord**: Discord senza boost accetta file fino a 10 MB. Lo script manda il video originale se ci sta, altrimenti una copia 1080p ricompressa (7-9 MB), che va bene anche da caricare a mano su YouTube.
- **Pulizia**: sulla VM restano gli ultimi 14 giorni di video.
- **Errori**: se qualcosa va storto Hermes manda l'avviso sul canale. Se fallisce solo l'upload su YouTube, il video arriva comunque con l'errore scritto sopra.
- **Per rilanciare a mano**: `hermes cron run <id>`. Per cambiare orario o canale: `hermes cron edit <id> --schedule "..."` oppure `--deliver "..."`.
