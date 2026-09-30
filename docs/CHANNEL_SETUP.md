# Setup del canale

Tutto quello che serve per aprire e sistemare il canale. Le immagini stanno in `assets/channel/` e si rigenerano con `python branding.py`, anche con un altro nome: `--name "..."`.

## 0. Crea il canale come Brand Account

Da YouTube: *Impostazioni → Aggiungi o gestisci i tuoi canali → Crea un canale*. Così il canale ha il suo nome, separato dal tuo account personale (è faceless anche lì), e in futuro puoi aggiungere altri gestori senza dargli la tua password.

## 1. Nome e handle

| | |
|---|---|
| **Nome** | Softloop |
| **Handle** | `@softloop` |
| **Handle di riserva** | `@softloopsims`, `@softloop.daily`, `@softloop_tv` |

Perché questo nome: "soft" come lo stile calmo e i colori pastello, "loop" come i video che ripartono senza stacco. È corto, si pronuncia uguale in inglese e in italiano e vale per tutti e tre i format.

La disponibilità degli handle non si può verificare da qui: controllala tu quando lo scegli. Se il nome non ti convince, le alternative sono **Calm Chaos** e **Pastel Physics**.

## 2. Immagini

Carica da *YouTube Studio → Personalizzazione → Branding*:

| File | Dove | Note |
|---|---|---|
| `assets/channel/avatar.png` (800×800) | Immagine | Anello pastello aperto con un pallino che esce dal varco, come nell'arena di Contagio. Si legge anche a 36px. |
| `assets/channel/banner.png` (2560×1440) | Immagine del banner | Nome e tagline stanno nell'area sicura 1546×423, quindi si vedono su ogni dispositivo. Palline e archi ai lati appaiono solo su desktop e TV. |
| `assets/channel/watermark.png` (150×150) | Filigrana video | Sugli Shorts non compare, ma è pronta per eventuali video lunghi. |

## 3. Descrizione del canale

*Personalizzazione → Informazioni di base → Descrizione*:

```
Calm simulations to watch, guess and relax. A new one every day.

Three series, all made entirely in code (no AI video, no stock footage):
• Which zodiac sign wins? 12 signs, 48 balls, one winner.
• Which color reaches the center? Four colors race through a maze.
• Wait for them to sync. Dots, notes and a perfect loop.

New short every day at 1 PM ET. Pick a side in the comments before it ends.
```

- **Link**: nessuno per ora.
- **Email di contatto**: usa una casella dedicata al canale, non la tua personale.

## 4. Impostazioni (*YouTube Studio → Impostazioni*)

### Canale → Informazioni di base
- **Paese di residenza**: Italia (serve per la monetizzazione e le tasse, deve essere vero).
- **Parole chiave**: `softloop, satisfying, oddly satisfying, relaxing, calm, simulation, physics simulation, zodiac, astrology, maze, polyrhythm, asmr, hypnotic, loop`

### Canale → Impostazioni avanzate
- **Pubblico**: *No, imposta questo canale come non destinato ai bambini*.

### Impostazioni predefinite di caricamento
Valgono per i caricamenti a mano. Quelli automatici hanno già tutto nel `.json`.
- **Visibilità**: Privato. Un caricamento sbagliato così non esce per errore.
- **Categoria**: Intrattenimento.
- **Lingua del video e di titolo/descrizione**: Inglese.
- **Licenza**: Licenza YouTube standard, incorporamento consentito, pubblicazione nel feed Iscrizioni.
- **Remix degli Shorts**: consenti remix di video e audio. I remix degli altri portano visibilità gratis.
- **Commenti**: *Trattieni i commenti potenzialmente inappropriati*, ordinamento *Principali*.
- **Mostra quanti spettatori hanno messo Mi piace**: sì.

### Community
- **Blocca i link** nei commenti, per tagliare lo spam.
- Aggiungi le parole bloccate che vuoi.

## 5. Layout del canale

Crea tre playlist pubbliche, una per format:

| Playlist | Descrizione |
|---|---|
| Which Zodiac Sign Wins? | 12 zodiac signs, 48 balls, one winner. A new match every episode. |
| Color Maze Race | Four colors, one maze, one center. Pick yours before it starts. |
| Wait for the Sync | Polyrhythms that line up again in a perfect loop. |

Poi, in *Personalizzazione → Layout*, aggiungi le sezioni in quest'ordine:
1. Shorts
2. le tre playlist

Metti ogni video nella sua playlist quando lo pubblichi: le playlist degli Shorts si guardano di fila nel feed, e chi finisce un episodio passa al successivo.

## 6. A ogni pubblicazione

- **Copertina**: gli Shorts non hanno miniature personalizzate. Nell'app, al caricamento, scegli come copertina il primo frame, quello con la domanda grande.
- **Commento fissato**: pubblicalo e fissalo subito, fa partire i commenti.
  - **Contagio**: `Which sign are you? Tell us below.`
  - **Labirinto**: `Which color did you pick before it started?`
  - **Sync**: `Did you wait for the sync? Rate it from 1 to 10.`
- **Prima ora**: rispondi ai primi commenti. È quando l'algoritmo decide se spingere il video.
