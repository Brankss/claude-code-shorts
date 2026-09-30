# claude-code-shorts

Generatore di YouTube Shorts faceless fatti interamente in codice: simulazione fisica, motion graphics e audio procedurale. Niente AI video, niente stock.

## Format 1: Contagio

12 squadre (per ora i segni zodiacali), 4 palline ciascuna, dentro un'arena circolare. Quando due palline di squadre diverse si scontrano, una converte l'altra. Vince l'ultima squadra rimasta.

Cosa succede nei ~40 secondi:

| Tempo | Evento |
|---|---|
| 0s | Hook: la domanda grande sopra l'arena già in movimento |
| 8.5s | *Speed up*: le palline accelerano |
| 15s | *Gravity on* |
| 20s | *Gravity flipped* |
| 24.5s | *The wall opens*: si apre un varco rotante, chi esce è fuori |
| finale | slow-mo e zoom leggero sul colpo decisivo, "X wins", dissolvenza sul primo frame per il loop |

### Stile

Minimal e rilassante: niente flash, scossoni, coriandoli o banner urlati.

- **Grafica**: colori piatti e morbidi, anello sottile, barra sottile a segmenti, didascalie piccole che entrano e escono in dissolvenza. A ogni conversione la pallina sfuma nel nuovo colore e parte un anello sottile.
- **Audio**: pad ambient, una nota tipo kalimba a ogni conversione (ogni segno ha la sua nota della scala pentatonica), campane morbide per eliminazioni ed eventi. La coda del riverbero rientra all'inizio, così anche l'audio fa il loop senza tagli.

### Drama score

Il generatore simula centinaia di partite senza renderizzarle e tiene la più drammatica, cioè quella con:
- tanti cambi di leader
- vincitore che a un certo punto era ridotto a 1-2 palline (rimonta)
- vincitore che non era tra i primi a metà partita
- duello finale né troppo corto né troppo lungo
- niente tempi morti tra un'eliminazione e l'altra

Tra i seed viene scelta la partita più bella, non il vincitore: nei titoli e nelle descrizioni non va scritto "100% random".

## Uso

```bash
pip install -r requirements.txt   # su Linux serve anche libegl1 per skia
python make_contagio.py --theme zodiac --seeds 1000 --out out/zodiac_001.mp4
```

Il comando produce `out/zodiac_001.mp4` (1080×1920, 60fps, H.264 + AAC) e `out/zodiac_001.json` con il seed, le statistiche e un titolo e una descrizione suggeriti.

Per controllare singoli frame senza renderizzare tutto il video:

```bash
python make_contagio.py --seed 149 --stills 0.1,6,25,34 --out out/preview
```

Per rigenerare lo stesso identico video basta rilanciarlo con `--seed N`.

Video del giorno, pensato per un'automazione giornaliera:

```bash
python daily.py                     # oggi, in out/daily/
python daily.py --date 2026-10-02   # un giorno specifico, sempre identico
```

Il numero di episodio e il vincitore dipendono solo dalla data: in ogni ciclo di 12 giorni ogni segno vince una volta, in ordine rimescolato.

## Struttura

- `shorts/contagio.py`: fisica, regole, eventi, drama score, ricerca dei seed
- `shorts/contagio_render.py`: timeline (slow-mo), arena, HUD, didascalie, schermata finale
- `shorts/contagio_audio.py`: colonna sonora sincronizzata con gli eventi
- `shorts/audio.py`: sintetizzatori (pad, kalimba, campane) e mixer con riverbero
- `shorts/gfx.py`: helper skia (font, testo, easing)
- `shorts/themes.py`: squadre (nome, glifo, colore). Per un nuovo tema basta aggiungerlo qui.

Font: Montserrat (OFL) e DejaVu Sans (licenze in `assets/fonts`).
