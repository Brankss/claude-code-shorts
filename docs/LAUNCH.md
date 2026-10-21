# Lancio account: kit per LOW TIDE

Kit per aprire l'account (TikTok, Instagram, YouTube) e pubblicare l'episodio 1.

- **Video:** `out/low_tide_001.mp4`, LOW TIDE · Day 1, 74,6 s.
- **Testi:** quelli da incollare sono in inglese, perché il pubblico è inglese/USA.
- **Storia, fatti e fonti:** in `docs/LOW_TIDE.md`.

DON'T ANSWER (il vecchio Day 1) è stato scartato. Il suo kit resta nella storia git (commit `be2803d`).

## 1. Nome dell'account: DA DECIDERE prima di aprirlo

Il nome scelto prima, **Rule Number Four** (@rulenumberfour.pov), era costruito sul vecchio format: 4 regole, la #4 censurata e l'outro "You already know rule number four". LOW TIDE non ha regole e il narratore è in terza persona. Con quel nome l'account prometterebbe una cosa diversa da quella che si guarda.

Le opzioni:

| Opzione | Pro | Contro |
|---|---|---|
| **A. LOW TIDE** · @lowtide.story | Chi guarda il video trova lo stesso nome sul profilo. Il titolo è già nel video e sulla copertina | Se poi fai una seconda serie, il nome non c'entra più |
| **B. Un nome-contenitore** per storie di sopravvivenza (es. "Last Resort Stories" · @lastresort.stories) | Regge più serie. "Last resort" è anche una battuta chiave dell'episodio | Va verificato che non sia già preso o troppo generico |
| C. Tenere Rule Number Four | Niente | Il nome non dice niente di questa storia |

**Il mio consiglio è A**: per i primi episodi conta che chi arriva dal video riconosca subito il profilo. Se un giorno arriva una seconda serie, si rinomina quando l'account è ancora piccolo.

Dimmi quale scegli e rigenero foto profilo e banner con `python -m shorts.branding`. Per ora vanno bene in ogni caso:
- `brand/avatar_1_faceless.png` (lo stickman senza faccia, senza scritte);
- `brand/cover_low_tide_day1.png`.

`avatar_3_rule4.png` e il banner YouTube hanno scritto RULE #4: **non usarli**.

Qualsiasi nome scegli, il giorno stesso prendi l'handle su tutte e tre le piattaforme. Da qui non posso verificare se sono liberi.

## 2. Bio (versione per l'opzione A)

**TikTok**
```
Zombies can't swim. The tide doesn't care.
Animated survival story · new day every week
```

**Instagram** (nel campo Nome: `LOW TIDE · animated zombie story`)
```
Zombies can't swim. Twice a day, the sea becomes a road.
Day 1 is up. Follow for Day 2.
Fiction · animated · synthetic narrator voice
```

**YouTube** (descrizione del canale)
```
LOW TIDE is an animated survival story told one day at a time.

Zombies can't swim, so Eli's island is safe. Except twice a day, when the tide goes out and the sea becomes a road.

Every number on screen is counted from the tide: the minutes until the road floods, the inches of water, the heads still in sight.

Fiction · animated · synthetic narrator voice
Real life: tidal roads publish safe crossing times. Never race the tide.
```

## 3. Episodio 1: cosa caricare

**Video.** `out/low_tide_001.mp4`:
- 1080x1920, 60 fps, 1:15, nessun watermark;
- -14 LUFS, cioè il volume standard delle piattaforme;
- carica sempre questo file, mai quello riscaricato da un'altra app.

**Copertina.** `brand/cover_low_tide_day1.png`: le 14 teste viste dalla botola, LOW TIDE, DAY 1 e "ZOMBIES CAN'T SWIM...". Se l'app non ti fa caricare un'immagine, scegli il fotogramma a **1:05**.

### TikTok
```
LOW TIDE · Day 1
Zombies can't swim. So the island is safe... until the tide goes out.
How would you warn Grandpa without making a sound?
#lowtide #zombie #animatedstory #survival #horrorstory
```

Impostazioni:
- pubblico: **Tutti**;
- commenti, Duetto e Stitch: **sì**;
- **"Contenuto generato dall'IA": SÌ** (la voce è sintetica).

### Instagram Reels
```
LOW TIDE · Day 1

Zombies can't swim. So Eli's island is safe... until the tide goes out and the sea becomes a road.

Nine minutes before the road floods, he's on the wrong side. Then Grandpa rings the bell.

How would you warn Grandpa without making a sound?

Follow for Day 2.

Real life: tidal roads publish safe crossing times. Never race the tide, never walk into moving water.
Fiction · animated · synthetic narrator voice

#lowtide #zombie #animatedstory #survival #horrorstory
```

Impostazioni:
- **etichetta IA: SÌ**;
- tieni l'audio originale, perché la storia è nella voce.

### YouTube Shorts

**Titolo**
```
Zombies can't swim... so why is the road the scariest place? (LOW TIDE · Day 1)
```

**Descrizione**: il testo della caption di Instagram, più `#shorts`.

**Tag**
```
low tide, zombie story, zombies can't swim, tidal road, causeway, survival story, animated horror, what would you do, refuge box, day 1, stickman, cliffhanger
```

Impostazioni:
- non destinato ai bambini;
- **contenuti alterati o sintetici: No**: è animazione, non una persona o un evento reali;
- categoria Intrattenimento.

### Commento da fissare (uguale ovunque, entro il primo minuto)
```
At 6:38 AM the sea touches the road. Grandpa rings the bell.
How do you warn him without making a sound?
LIGHT · BISCUIT · WAIT
Day 2 starts with the most-picked answer.
```
Promessa da mantenere: il Day 2 parte davvero dalla risposta più scelta.

### Risposta con i fatti (da fissare sotto il primo commento)
```
The real stuff:
· Some tidal roads really have refuge boxes on stilts for people caught by the tide (Holy Island causeway, UK · Passage du Gois, France).
· 6 inches of moving water can knock you down (FEMA / NWS).
· Most coasts get two high and two low tides a day, about 50 minutes later each day (NOAA).
Never race the tide.
```

### Risposte pronte, in personaggio
```
(LIGHT)    The lighthouse is on every night. Grandpa isn't watching the light. He's watching the road.
(BISCUIT)  Biscuit hasn't made a sound since 6:21. Eli would like to keep it that way.
(WAIT)     The road dries at 1:46. The bell rings at 6:38. That's a lot of hours with fourteen of them under the floor.
("part 2?")  The tide's on its way back. Follow so you're on the right side of it.
```

## 4. Quando pubblicare

**Prima di pubblicare, guardalo in cuffia.** Io l'audio non lo posso sentire: ho controllato volume e tempi solo con le misure. I punti da sentire sono in `docs/LOW_TIDE.md`, in fondo.

**Orario consigliato: 22:30 ora italiana.** Negli USA è fine scuola o lavoro. Scegli comunque un'ora in cui puoi stare sui commenti per la prima ora.

Occhio al cambio dell'ora:

| Date | 22:30 a Roma = |
|---|---|
| fino a sab 24/10 | 16:30 New York · 13:30 Los Angeles |
| dom 25/10 – sab 31/10 | 17:30 New York · 14:30 Los Angeles |
| da dom 1/11 | 16:30 New York · 13:30 Los Angeles |

| Quando | Cosa |
|---|---|
| **gio 22/10, 22:30** | Day 1 **solo su TikTok**. Commento fissato, prima ora sui commenti |
| ven 23/10 | Day 1 su Shorts e Reels. Comincia a contare LIGHT / BISCUIT / WAIT |
| dom 25/10 | Chiudi il conteggio. Script del Day 2 dalla risposta più scelta |
| **mar 27/10** | **Day 2** (l'1:46 e le 6:38: la strada che si asciuga, il nonno e la campana) |
| **sab 31/10** | Day 3 la sera di Halloween |

Il Day 2 non esiste ancora. Set, mappa e marea sono pronti e riusabili: le maree arrivano ~50 minuti più tardi ogni giorno, ed è già nel modello.

## 5. Cose da non fare

- Non cancellare e ricaricare un video che parte piano: si giudica dopo 48-72 ore.
- Non comprare follower o like e non usare bot.
- Non caricare un file con il watermark di un'altra piattaforma.

## 6. Etichetta IA

La voce del narratore è sintetica (TTS) e realistica, il resto è animazione disegnata.

| Piattaforma | Etichetta |
|---|---|
| TikTok | Sì |
| Instagram | Sì (audio realistico creato digitalmente) |
| YouTube | No: è animazione, non persone o eventi reali |

In ogni caption c'è "Fiction · animated · synthetic narrator voice". Le regole cambiano spesso: quando pubblichi, leggi il testo dell'interruttore.

## 7. Note oneste

- **L'audio non l'ho sentito.** Ho misurato volume e picchi (-14,1 LUFS, picco −1,1 dBTP) e ho messo i suoni sui tempi delle parole. Prima di pubblicare va ascoltato in cuffia. Se una frase o un suono non va, dimmi il secondo e lo sistemo.
- **La sezione laterale non è in scala.** Il mezzo miglio di strada è compresso, così il box e la terraferma ci stanno nella stessa inquadratura. Le distanze vere le tiene la mappa vista dall'alto.
- Gli handle non li posso verificare da qui.
