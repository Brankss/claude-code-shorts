# LOW TIDE · Day 1 · "The Road"

Short animato verticale da 73,7 s. È la nuova serie che sostituisce DON'T ANSWER, bocciata dal proprietario per tre motivi: una storia "messa sulla casa" senza senso, scene ferme e numeri a caso. Dello stile vecchio restano solo la grafica (flat vector, stickman crema senza volto, HUD, didascalie karaoke, card) e il motore `rules`.

Codice:
- `shorts/pov_stories.py` → `low_tide()`: battute, tempi e suoni;
- `shorts/low_tide.py`: scene e marea;
- `shorts/low_tide_audio.py`: effetti.

Render: `python make.py --format rules --episode 1 --out out/low_tide_001.mp4`.

## La storia in due frasi

Gli zombie non sanno nuotare: l'isola di Eli è salva, tranne quando la marea scende e il mare diventa una strada. Eli resta bloccato a metà strada, il nonno suona per abitudine la campana che porta 14 morti sulla strada, e lui si salva in un box sui pali. A mezzanotte meno venti l'acqua scende e i 14 sono ancora lì: non sono annegati.

## Perché è il posto a muovere la trama

| Proprietà del posto | Problema che crea |
|---|---|
| L'acqua è il muro (non nuotano) e la marea lo toglie a orario | Il conto alla rovescia di tutto l'episodio |
| Le FLATS: il tratto più basso, piatto, un quarto di miglio | Si allagano tutte insieme alle 6:13. Eli resta fuori |
| Sull'acqua calma il suono arriva lontano | La campana del nonno, pensata per Eli, arriva ai morti |
| Sei pollici d'acqua che scorre buttano giù una persona | Guadare è escluso: resta solo il box |
| Il box sui pali sul bordo delle FLATS | Eli sale dall'asciutto. Il box ha una sola scala, che si tira su |
| L'acqua che scende scopre le teste (6 ft) due ore prima della strada | Il climax alle 11:39, mentre la strada riapre solo all'1:46 |
| La marea successiva (6:38 AM) bagna di nuovo la strada | È l'ora in cui il nonno suona da 40 anni: il Day 2 |

## La marea: un modello solo

Tutti gli orari e le misure a schermo escono da `low_tide.tide(h)`:
- ciclo coseno, periodo 12,42 h, escursione 12 ft;
- bassa marea alle 3:47 PM;
- le FLATS stanno 4 ft sopra la bassa marea.

L'ora la decide l'HUD (`Beat.clock`, con `Beat.roll` per lo scorrimento), e le scene la leggono da lì. Per questo acqua, pollici, piedi e mappa non possono andare fuori tempo tra loro.

| Ora | Acqua sulle FLATS | Cosa succede |
|---|---|---|
| 6:04 PM | −5 in (asciutto) | Eli all'ingresso. Il cartello: UNDER WATER 6:13 PM – 1:46 AM → FLOODS IN 9:00 |
| 6:05 | | Eli parte. Cammina in silenzio a ~2 mph: mezzo miglio fino al bordo delle FLATS |
| 6:12 | | L'allarme si spegne. I morti restano fermi attorno all'auto |
| 6:13 | 0 | Le FLATS si allagano. Eli è ancora a ~6 minuti di cammino: STILL OUT HERE |
| 6:14–6:15 | | Campana. I 14 più vicini all'acqua corrono sulla strada (ON THE ROAD 0 → 5 → 10 → 14) |
| 6:19 | 3,5 in | Eli al bordo, sull'asciutto. Davanti un quarto di miglio d'acqua che sale (~0,6 in/min) |
| 6:20–6:21 | 4–4,6 in | Sale sulla scala di corda e la tira su. I morti arrivano di corsa |
| 7:34 / 7:55 / 8:20 | 4 / 5 / 6 ft | Le teste (5,5–6 ft) vanno sotto tra 8:07 e 8:20: IN SIGHT 14 → 0 |
| 10:00 PM | 8 ft | Alta marea, un piede sotto il pavimento del box (a 9 ft) |
| 11:39 PM | 6 ft (scende) | Biscuit guarda giù. Riemerge la prima testa |
| 11:52 PM | 5,5 ft | Tutte e 14 fuori |
| 1:46 AM | 0 | La strada riapre (Day 2) |
| 6:38 AM | 0 (sale) | La strada si allaga di nuovo: il nonno suona (Day 2) |

Il guado "fantasma" (beat 16) parte alle 6:19 a 2 mph sul quarto di miglio. La profondità supera i 6 pollici a poco più di metà strada, e lì il fantasma cade.

## Copione (190 parole, voce narrante a speed 1.32)

| # | Battuta | Immagine | Numero legato all'azione |
|---|---|---|---|
| 1 | Zombies can't swim. So Eli's island is safe... until the tide goes out. | Tramonto, i morti sul bagnasciuga. Uno in acqua viene ribaltato dall'onda e la corrente se lo porta. Su "out" il mare si ritira e la strada emerge (colpo 1) | – |
| 2 | Twice a day, the sea becomes a road. | La baia dall'alto, un ciclo di marea, titolo LOW TIDE | – |
| 3 | Day one. | Eli arriva di corsa e si butta dietro l'auto. Un morto appoggia la mano sul cofano | HUD 6:04 |
| 4 | The road floods in nine minutes... | Il cartello delle maree. FLOODS IN 9:00 si stacca dal 6:13 | 9:00 = 6:13 − 6:04 |
| 5 | and Eli's on the wrong side. | Il telefono passa da 1% a nero | PHONE 1% → 0% |
| 6 | He sets off a car alarm. | Lancia un sasso lontano | – |
| 7 | The dead run to the sound. | Dall'alto: i puntini corrono all'auto che suona, l'ingresso si libera | – |
| 8 | So Eli walks. Silent. But silent is slow. | Il puntino di Eli sulla strada | FLATS FLOOD IN (con l'HUD) |
| 9–10 | The alarm dies... and the sea gets there first. | ALARM · OFF. Le FLATS si allagano, Eli è ancora fuori | 0:00 rosso, STILL OUT HERE |
| 11 | Grandpa sees the water... | Il binocolo: solo l'acqua e Eli. La spiaggia è dietro il promontorio | – |
| 12 | and rings the bell. For forty years, it's meant: come home. | Il nonno tira la corda (colpo 2). La targa: RING WHEN THE SEA TOUCHES THE ROAD. La radio fa solo fruscio | – |
| 13–14 | But over calm water... sound carries. | Eli si gira di scatto verso la spiaggia. Gli anelli sulla baia, le teste si girano | – |
| 15 | Five. Ten. Fourteen... on the road behind him. | A ogni rintocco un gruppo passa la linea d'ingresso | ON THE ROAD 0 → 5 → 10 → 14 |
| 16 | Ahead: a quarter mile of water, rising. Six inches of moving water can knock you down. | Eli sull'asciutto. Il palo in pollici. Il fantasma che guada cade | WATER 3 → 4 IN; IF HE WADES → 6 IN |
| 17 | Last resort: a box on stilts. Some tidal roads really have them. | Corre alla scala. REAL: SOME TIDAL ROADS HAVE THESE. Il primo morto entra in campo | – |
| 18 | He climbs. He hauls the rope ladder up. | Sale, tira su la scala. I morti arrivano di corsa | – |
| 19 | But the ladder clatters... and the box shakes. So Biscuit... not one bark. | Sezione: spingono tutti insieme, il box barcolla, cade polvere (colpo 3). La zip sul muso | – |
| 20–22 | Four feet. Five. Six... and the sea swallows them. | La scala dipinta, THEIR HEADS · 6 FT, le teste sotto. Le mani restano sulle traverse | IN SIGHT 14 → 0 solo sul 6 |
| 23 | Zero in sight. The road opens at one forty-six. | Registro REFUGE BOX · NIGHT 1 | IN SIGHT 0 (l'unico verde), ROAD OPENS 1:46 AM; per chi mette in pausa HIGH TIDE 8 FT (pavimento a 9) e PHONE 0% |
| 24 | Eleven thirty-nine. Biscuit stares down. | HUD rosso, TIDE ↓ FALLING. Prima il cane, poi la mano sul muso, poi tre graffi bagnati | – |
| 25 | The water's back to six feet. | La scala dipinta: l'acqua scende sotto il 6 | 6 FT (paga il "SIX") |
| 26 | One head... six... all fourteen. Looking up. | Dalla botola: il fascio del faro passa tre volte (colpo 4) | IN SIGHT 1 → 6 → 14 |
| 27 | Zombies can't swim... They don't drown. | Nero: due righe, muto vero, la seconda in rosso (colpo 5) | – |
| 28 | At dawn... Grandpa rings the bell. | La baia di notte: 14 puntini sotto il box sulla strada per il nonno. 6:38 AM · THE ROAD FLOODS AGAIN / GRANDPA RINGS THE BELL. L'ultimo suono è la campana | 6:38 AM |

I colpi di sub sono 5: out, bell, shakes, fourteen, drown. Il titolo non fa boom.

## Fatti detti a voce (fact-check del 21/10)

| Frase | Esito | Fonte |
|---|---|---|
| "Twice a day, the sea becomes a road" | Vero per le coste semidiurne: due alte e due basse ogni 24 h 50 min, alte a 12 h 25 min di distanza. Alcune coste hanno una marea sola: non diciamo "ovunque" | NOAA Ocean Service, "Tides and Water Levels: Lunar day" (oceanservice.noaa.gov/education/tutorial_tides/tides05_lunarday.html) |
| "Six inches of moving water can knock you down" | Vero, quasi parola per parola | Ready.gov / FEMA Floods: "just six inches of moving water can knock you down". NWS Turn Around Don't Drown: "6 inches of fast-moving flood water can knock over an adult" |
| "Some tidal roads really have them" (box sui pali) | Vero, con il "some" | Holy Island / Lindisfarne causeway: rifugio sopraelevato per chi resta bloccato dalla marea (Northumberland County Council, holyislandcrossingtimes.northumberland.gov.uk; lindisfarne.org.uk). Passage du Gois (Francia): torri rifugio |
| "Over calm water... sound carries" | Vero, a condizioni (aria fresca sull'acqua, inversione termica, sera e acqua calma). Per questo "calm" e niente distanze | Penn State Acoustics (D. Russell), refraction demo; HyperPhysics, "Refraction of sound" |
| Faro che si accende da solo al buio | Vero (mostrato, non detto) | USCG Light List: i segnali luminosi hanno controlli crepuscolari che li accendono al buio |

Logica da film, solo per la minaccia: i morti non nuotano, non annegano, seguono i suoni, non si arrampicano e corrono verso un suono.

## Sicurezza (vale nella vita reale)

- Eli non entra mai nell'acqua che scorre: sale sul box dal pendio asciutto. Il guado lo fa solo il "fantasma", e cade.
- Il cartello all'ingresso dice NEVER RACE THE TIDE. Eli lo infrange solo perché i morti gli bloccano la terraferma, e la storia mostra quanto costa.
- La didascalia del post riporta: "Real life: tidal roads publish safe crossing times. Never race the tide, never walk into moving water."

## Day 2 (già piantato)

All'1:46 AM la strada si asciuga con i 14 sotto il box, sulla strada che porta al nonno. Alle 6:38 AM il mare tocca di nuovo la strada: è il momento in cui il nonno suona da quarant'anni. Eli ha il telefono morto e non può fare rumore.

La domanda del commento fissato è "How would you warn Grandpa without making a sound?". I semi sono già a schermo: il fascio del faro, Biscuit, la barca HULL CRACKED, la radio che fa solo fruscio. Le maree arrivano ~50 minuti più tardi ogni giorno (NOAA): ogni episodio la finestra di pericolo scivola più in là nella notte.

## Cosa resta da controllare a orecchio (io l'audio non lo posso sentire)

- **Campana:** che i tre rintocchi tra "Five / Ten / Fourteen" cadano nelle pause e non sopra le parole.
- **Muto prima di "drown":** che non tagli l'attacco della parola.
- **Tappeto del mare e allarme:** che non coprano la voce.
- **L'ultimo suono:** che sia la campana.
