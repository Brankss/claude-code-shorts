# claude-code-shorts

Generatore di YouTube Shorts faceless fatti interamente in codice: simulazione, motion graphics e audio procedurale. Niente AI video, niente stock.

Genere: relax / ipnotico. Tre format completamente diversi che si alternano ogni giorno, tutti nello stesso stile minimal:
- **Grafica**: colori piatti e morbidi, linee sottili, testo sobrio, niente flash o scossoni.
- **Audio**: pad ambient più note tipo kalimba o campane legate a quello che succede a schermo.
- **Durata e loop**: 25 secondi, con dissolvenza finale sul primo frame così il loop non ha stacchi.
- **Hook**: dal primo frame lo schermo è già pieno di colore e azione. Il labirinto parte con la gara già al 20%, il Sync da un pattern sparpagliato (si allinea al secondo 20), Contagio con palline grandi e scontri immediati.

## Format 1: Contagio (`contagio`)

12 squadre (i segni zodiacali), 4 palline ciascuna, dentro un'arena circolare. Quando due palline di squadre diverse si scontrano, una converte l'altra. Vince l'ultima squadra rimasta.

| Tempo | Evento |
|---|---|
| 0s | Hook: la domanda grande sopra l'arena già in movimento |
| 4s | *Speed up*: le palline accelerano |
| 8s | *Gravity on* |
| 12s | *The wall opens*: si apre un varco rotante, chi esce è fuori |
| finale | slow-mo e zoom leggero sul colpo decisivo, "X wins" |

Il generatore simula centinaia di partite senza renderizzarle e tiene la più drammatica (**drama score**), cioè quella con:
- tanti cambi di leader
- una rimonta di chi era ridotto a 1-2 palline
- un duello finale né troppo corto né troppo lungo

Tra i seed si sceglie la partita, non il vincitore: nei titoli non va scritto "100% random".

## Format 2: Labirinto (`maze`)

Quattro liquidi colorati partono dagli angoli di un labirinto 13×13 e scorrono nei corridoi. Vince il primo che arriva al centro.
- Ogni cella ha un tempo di attraversamento casuale, quindi la gara non si risolve a occhio.
- Chi arriva prima in una cella la occupa e blocca gli altri: un colore può restare intrappolato.
- Durante la gara: barrette di progresso, chi è più vicino e quanti passi mancano, avvisi *is trapped* e *final stretch*.
- Alla fine si disegna il percorso del vincitore.

Il drama score premia gli arrivi al fotofinish, i cambi di chi è più vicino e un colore intrappolato.

## Format 3: Sync (`sync`)

Pallini su orbite concentriche a velocità diverse (polyrhythm). Ogni colpo suona una nota.
- Il video parte da un pattern già sparpagliato e i pallini si allineano tutti al secondo 20, poi il loop riparte senza stacchi.
- Un countdown "Next sync in 0:12" tiene lo spettatore fino al payoff.
- Due varianti si alternano: **arcs** (vanno e vengono su semicerchi, con riflesso) e **rings** (girano in tondo).
- Ogni episodio cambia numero di orbite, velocità, palette e scala musicale.

## Format extra: What If (`whatif`)

Genere diverso dagli altri tre: storie "e se tutti facessero X?" a effetto farfalla, con un twist vero alla fine. Non è nella rotazione giornaliera (ogni storia è scritta e verificata a mano). Analisi del video di riferimento, formula, guida per scrivere storie nuove e idee con fonti: [docs/WHATIF.md](docs/WHATIF.md).

- Scena vera simulata (traffico IDM per lo zipper merge), camera inclinata che segue il protagonista giallo in mezzo a una folla grigia.
- Zoom continuo a potenze di dieci: strada, città, stato, paese, globo, spazio, Luna. Mappe vere (Natural Earth).
- HUD da documentario: luogo, orologio che gira durante i salti di tempo, contatore con variazione %, metrica secondaria, barra di scala.
- Rewind, twist con il dato reale e chiusura sulla stessa inquadratura del primo frame (loop).
- Audio senza voce: traffico e clacson presi dalla simulazione, pad e campane che salgono con l'escalation, whoosh, macchina da scrivere, nastro che riavvolge.

```bash
python make.py --format whatif --episode 1 --out out/whatif_zipper.mp4
```

## Uso

```bash
pip install -r requirements.txt   # su Linux serve anche libegl1 per skia
python make.py --format maze --episode 1 --out out/maze_001.mp4
python make.py --format contagio --seed 405 --out out/zodiac.mp4          # seed già noto, salta la ricerca
python make.py --format sync --episode 3 --stills 0.5,20,39 --out out/prev # solo frame PNG per controllare
```

Ogni video produce `.mp4` (1080×1920, 60fps, H.264 + AAC, sotto i 30 MB), `.json` con metadati e statistiche e `.txt` con titolo e descrizione da incollare.

### Video del giorno

```bash
python daily.py                     # oggi, in out/daily/
python daily.py --date 2026-10-02   # un giorno specifico, sempre identico
```

Tutto dipende solo dalla data, partendo dal 30/09/2026:
- **Rotazione dei format**: Contagio, Labirinto, Sync, e poi da capo.
- **Episodi**: ogni format ha la sua numerazione.
- **Vincitori**: nei format con vincitore, ogni squadra vince una volta per ciclo, in ordine rimescolato.

### Pubblicazione su YouTube

Ogni video ha già pronti titolo, descrizione con hashtag, tag e impostazioni (`shorts/publishing.py`). Tutto questo finisce nel `.json` e, in versione leggibile da copiare a mano, nel `.txt`.

```bash
python publish.py out/daily/2026-10-01_maze.mp4 --dry-run   # cosa verrebbe inviato
python publish.py out/daily/2026-10-01_maze.mp4             # carica e programma (13:00 New York)
```

Per credenziali, audit e accensione dell'automazione vedi [docs/YOUTUBE_SETUP.md](docs/YOUTUBE_SETUP.md).

### Su Hermes Agent

Per far girare tutto ogni giorno su una VM con Hermes Agent, con consegna su Discord e zero token, vedi [hermes/README.md](hermes/README.md).

### Canale

Nome, handle, descrizione, impostazioni e playlist sono in [docs/CHANNEL_SETUP.md](docs/CHANNEL_SETUP.md). Avatar, banner e watermark stanno in `assets/channel/` e si rigenerano con `python branding.py`.

## Struttura

- `shorts/base.py`: parti comuni (canvas, hook, header, loop finale)
- `shorts/formats.py`: registro dei format (scelta del seed, preparazione del render, titoli)
- `shorts/produce.py`: audio, encoding, metadati
- `shorts/publishing.py`: titoli, descrizioni, hashtag, tag, impostazioni e orario di pubblicazione
- `branding.py`: avatar, banner e watermark del canale
- `publish.py`: upload e programmazione su YouTube (API ufficiale); `youtube_auth.py`: refresh token, da lanciare una volta
- `shorts/contagio.py`, `contagio_render.py`, `contagio_audio.py`: Contagio
- `shorts/maze.py`, `maze_render.py`, `maze_audio.py`: Labirinto
- `shorts/sync.py`: Sync (parametri, render, audio)
- `shorts/audio.py`: sintetizzatori (pad, kalimba, campane) e mixer con riverbero
- `shorts/gfx.py`: helper skia (font, testo, colori, easing)
- `shorts/themes.py`: squadre (nome, glifo, colore)
- `shorts/whatif.py`: engine di What If (beat, camera a potenze di dieci, mappe, spazio, HUD, didascalie, rewind, loop)
- `shorts/stories.py`: le storie di What If; `shorts/highway.py`: simulazione del traffico e disegno della strada; `shorts/whatif_audio.py`: sound design
- `shorts/geo.py`: dati Natural Earth (TopoJSON in `assets/geo`), proiezione ortografica e path pronti

Font: Montserrat (OFL), IBM Plex Mono (OFL) e DejaVu Sans (licenze in `assets/fonts`). Mappe: Natural Earth (pubblico dominio) dai pacchetti world-atlas e us-atlas (ISC, licenze in `assets/geo`).
