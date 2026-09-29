# claude-code-shorts

Generatore di YouTube Shorts faceless fatti interamente in codice: simulazione fisica, motion graphics e audio procedurale. Niente AI video, niente stock.

## Format 1: Contagio

12 squadre (per ora i segni zodiacali), 4 palline ciascuna, dentro un'arena circolare. Quando due palline di squadre diverse si scontrano, una converte l'altra. Vince l'ultima squadra rimasta.

Cosa succede nei ~40 secondi:

| Tempo | Evento |
|---|---|
| 0s | Hook: titolo gigante sopra l'arena già in movimento |
| 8.5s | **SPEED UP!** le palline accelerano |
| 15s | **GRAVITY ON** |
| 20s | **GRAVITY FLIP!** |
| 24.5s | **THE WALL BREAKS!** si apre un varco rotante: chi esce è fuori |
| finale | slow-mo + zoom sul colpo decisivo, festa del vincitore, dissolvenza sul primo frame per il loop |

Durante tutta la partita: barra delle percentuali in tempo reale, leader, toast "IS OUT!" / "LAST BALL!", particelle e onde d'urto a ogni conversione.

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

## Struttura

- `shorts/contagio.py`: fisica, regole, eventi, drama score, ricerca dei seed
- `shorts/contagio_render.py`: timeline (slow-mo), arena, HUD, banner, festa finale
- `shorts/contagio_audio.py`: colonna sonora sincronizzata con gli eventi
- `shorts/audio.py`: sintetizzatori (kick, hat, pluck, riser, boom…) e mixer
- `shorts/gfx.py`: helper skia (font, testo, easing)
- `shorts/themes.py`: squadre (nome, glifo, colore). Per un nuovo tema basta aggiungerlo qui.

Font: Anton e Montserrat (OFL), DejaVu Sans (licenza in `assets/fonts`).
