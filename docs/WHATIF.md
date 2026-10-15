# What If: come funziona il format e cosa farci

Il format `whatif` rifà in codice la struttura dei video "What if everyone on Earth followed the escalator rule?": una regola di tutti i giorni, un effetto farfalla che esce di potenze di dieci fino allo spazio, poi un dato reale che ribalta tutto. Niente voce, niente AI video: simulazione, mappe vere e audio procedurale.

```bash
python make.py --format whatif --episode 1 --out out/whatif_zipper.mp4            # storia 1: zipper merge
python make.py --format whatif --episode 2 --out out/whatif_tiktok.mp4            # storia 2: tutti cancellano TikTok
python make.py --format whatif --episode 2 --stills 0.5,17,44 --out out/prev       # solo frame PNG per controllare
```

## 1. Anatomia del video di riferimento (94 s)

| Tempo | Cosa succede | Perché funziona |
|---|---|---|
| 0-3 s | Domanda grande sopra un primo piano già in movimento | Hook: la domanda è una regola che tutti conoscono e su cui tutti hanno un'opinione |
| 3-8 s | "Holborn station, London. Monday, 8:31 a.m." + HUD: luogo, orologio che corre, data, contatore "PEOPLE PER MINUTE 115" | Un posto vero e un'ora precisa = credibilità da documentario |
| 9-19 s | "Every morning, this man stands on the left." Lui è giallo, la folla è grigia. "Except this morning, the whole planet follows the rule." | Un protagonista unico, riconoscibile a colpo d'occhio |
| 20-31 s | Il contatore sale (115 → 150, ▲30%); "Walkers save 30 seconds", "Trains run on time" | Prima conseguenza piccola e plausibile, con numeri |
| 32-67 s | Zoom continuo: stazione → Londra → UK → Europa → globo → sistema solare → Marte. A ogni salto "+3 MONTHS", "+1 YEAR"... e una conseguenza più grande e più assurda (cani portati a spasso, fame nel mondo, statua su Marte) | Escalation a potenze di dieci: ogni 4 secondi qualcosa di nuovo, la curiosità non cala mai |
| 68-70 s | Rewind: numeri e date che girano all'indietro, suono di nastro | Cambio di ritmo, segnala che arriva la verità |
| 70-88 s | "In 2016, London actually tested it." Dato vero: in piedi su entrambi i lati 151 persone al minuto invece di 115 | Il twist ribalta la premessa con un dato verificabile |
| 88-94 s | Di nuovo il primo piano: "The man on the left was right." | Chiusura sulla stessa inquadratura dell'inizio: il loop riparte da solo |

Dettagli di stile che contano:
- **HUD in monospace** in alto (luogo, ora, data, T+, contatore con variazione in ambra, metrica secondaria con freccia). Il tempo che scorre tiene incollati.
- **Una sola tinta d'accento** (ambra) su un mondo desaturato. Il protagonista è l'unica cosa colorata.
- **Didascalie corte** (massimo ~8 parole), centrate sulla scena e a macchina da scrivere sulle mappe.
- **Barra di scala** sulle mappe ("10 KM", "2,000 KM", "100 MILLION KM"): fa sentire lo zoom.
- **Nessuna voce**: funziona in qualunque lingua e a volume zero.
- **Numeri assurdamente precisi** ("214,000 more dogs get an evening walk"): fanno ridere e sembrano veri.

## 2. La formula (vale per ogni storia)

1. **Regola o abitudine quotidiana divisiva**: tutti hanno un'opinione e qualcuno che li fa arrabbiare (chi sta a sinistra sulla scala mobile, chi si immette all'ultimo).
2. **Premessa**: "E se TUTTI seguissero la regola 'giusta'?". Il protagonista è quello che la infrange.
3. **Escalation inventata** (e deve sembrarlo): 5-6 salti di zoom e di tempo, ognuno con un numero preciso. L'ultimo salto è assurdo e, se possibile, anticipa il twist (nella nostra Luna: "Everyone merges early. It lasts three days.").
4. **Rewind.**
5. **Twist vero, con fonte**: un test reale dimostra che quello che "sbagliava" aveva ragione. Il dato va nella descrizione con la fonte.
6. **Chiusura**: "The [protagonist] was right." sulla stessa inquadratura del primo frame.

Regole che non si toccano:
- Il twist deve essere vero e citabile. Se il dato è conteso, si usa la formulazione prudente ("up to 40%", "crashes went down").
- I numeri dell'HUD nel twist non devono contraddire la didascalia (per questo la simulazione dello zipper è tarata sul −40% di MnDOT).
- La parte inventata non deve sembrare un dato reale: è nel blocco "what if", con salti di tempo nel futuro.

## 3. Lo zipper merge (storia 1)

"What if every driver merged early?" Tutti odiano chi usa la corsia che chiude fino alla fine. Il Minnesota DOT dice che lo zipper merge (usare entrambe le corsie e alternarsi alla fine) accorcia la coda fino al 40%, e in Germania è obbligatorio (StVO §7 comma 4).

- Il traffico è una **simulazione vera** (Intelligent Driver Model, `shorts/highway.py`): due simulazioni con stessa domanda e stesso seed, una "early" e una "zipper". Nel cantiere la velocità pulsa (mezzi che entrano ed escono), quindi la coda è stop-and-go come nella realtà.
- Il confronto finale è affiancato: le due code dopo 16 minuti, con la lunghezza. Con metà dei guidatori che si immette comunque presto per abitudine, la sim dà −40%, in linea col dato MnDOT.
- I clacson nell'audio sono quelli della simulazione: suonano quando l'eroe sorpassa la coda e spariscono quando tutti si immettono presto.

## 3b. Tutti cancellano TikTok (storia 2)

"What if everyone on Earth deleted TikTok at the same time?" Più dopaminica dello zipper: il telefono è la prima cosa che si vede, chi guarda ha lo stesso gesto in mano, e la domanda tocca qualcosa che tutti hanno pensato almeno una volta.

| Tempo | Cosa succede |
|---|---|
| 0-2.6 s | Primo piano sul telefono che scrolla (video veri disegnati, UI, swipe). Hook sopra. Contatore "HOURS SCROLLED TODAY" che corre |
| 2.6-11 s | Dormitorio a Chicago, 2:47 di notte. "He said 'one more video.' Three hours ago." |
| 11-14 s | Tieni premuto l'icona, "Delete app?", tap, l'icona esplode, lo schermo si spegne, il telefono va a faccia in giù. Il contatore si blocca |
| 15.7-17 s | Fuori dalla stanza: tutto il dormitorio. Alle 17.0 tutte le luci blu dei telefoni si spengono insieme (flash + shake) |
| 18.8-37 s | Escalation: campus (+1 settimana) → Chicago (+1 mese) → USA (+6 mesi) → Terra (+1 anno) → Luna (+8 anni, "Nobody films it vertically.") |
| 40.2 s | Rewind fino alla stanza |
| 42.4-55 s | Twist vero: griglia di 1.000 telefoni, "$55 per smettere da soli", "$24 PAGATI perché smettano tutti", "58% preferisce un mondo senza" |
| 55.2-59.4 s | Di nuovo sul telefono che scrolla: "Everyone wants out. Nobody leaves first." Il finale è il primo frame: loop |

- **Fonte del twist**: Bursztyn, Handel, Jiménez-Durán, Roth, "When Product Markets Become Collective Traps: The Case of Social Media" (NBER WP 31771; American Economic Review 2025). Oltre 1.000 studenti universitari USA che usano TikTok: per disattivarlo da soli chiedevano circa $55; se lo disattivassero tutti, pagherebbero circa $24 perché succeda; il 58% preferirebbe un mondo senza TikTok.
- **La parte inventata** (sonno, libri, Luna) sta tutta nel blocco con i salti di tempo nel futuro; i numeri del contatore principale sono una stima (~1 miliardo di ore al giorno nel mondo) e non vengono citati come dato.
- **Il KPI è una funzione** (`kpi_fn`): corre col tempo reale, si ferma quando tutti cancellano, poi conta le ore restituite; nel rewind torna alla realtà.
- **Palette notturna** (`palette`): mare e terra più scuri, accento caldo, così la mappa continua l'atmosfera della stanza.
- La scena è `shorts/dorm.py`: stanza, telefono con 12 video procedurali e UI, dormitorio, campus, griglia di Chicago, Luna con astronauti, infografica dello studio. Ha anche l'audio suo (musica dal telefono, swipe, tap, room tone).
- Mappe: Natural Earth + laghi di OpenStreetMap (ODbL, attribuzione nella descrizione).
- **Audio livellato**: la stanza silenziosa dell'inizio era 15 dB sotto le mappe, e l'inizio è proprio la parte che deve agganciare. Il master passa da un livellatore lento (`whatif_audio.leveler`) che riduce la differenza a circa 10 dB senza toccare il loop.

## 4. Come si scrive una nuova storia

Una storia è una funzione in `shorts/stories.py` che restituisce `(Story, scena, stats)` e va aggiunta a `STORIES`. La storia è una lista di `Beat`: ogni beat cambia solo quello che gli serve, il resto prosegue dal beat prima.

| Campo del Beat | Cosa fa |
|---|---|
| `at` | secondo del video in cui parte |
| `text`, `sub` | didascalia e sottotitolo (`text=""` la toglie); `hook=True` per la domanda iniziale |
| `point` | linea dalla didascalia a un'ancora della scena (es. `"hero"`) |
| `cam`, `move` | `{"w": larghezza in metri, "c": (x, y) o "hero", "pitch": gradi, "dy": metri}` e durata del movimento. Da 30 m a 1.3 miliardi di metri senza tagli |
| `place`, `when`, `live`, `tag` | luogo nell'HUD, orologio (durante i movimenti gira veloce), tempo reale, riga in ambra (di default T+, DAY n, YEAR n) |
| `jump` | "+3 MONTHS" a macchina da scrivere sopra la didascalia |
| `kpi`, `kpi_label`, `kpi_base`, `kpi2` | contatore principale con variazione %, metrica secondaria |
| `spread`, `hatch` | onda che si allarga sulla mappa (km) e regioni tratteggiate (stati USA, paesi) |
| `scene`, `split` | quale registrazione mostrare e confronto affiancato |
| `fx`, `fx_dur` | `"rewind"`, `"hit"` (colpo basso nell'audio), `"flash"` (lampo bianco), `"shake"` (scossone della scena) e quanto durano |

Campi della `Story` oltre ai soliti: `palette` (colori di mare, terra, confini, accento), `kpi_fn(vt, tl)` per un contatore che non è una semplice interpolazione, `kpi_fmt` per formattarlo (es. `"{:,.0f}"`).

Tempi che funzionano: un beat ogni 3-4 s (nella storia TikTok anche meno all'inizio), movimenti di camera da 1-2.4 s, video tra 55 e 75 s. Qualcosa deve cambiare sullo schermo almeno ogni 2-3 s.

La scena è l'unica parte specifica di ogni storia: deve saper disegnarsi (`draw`) e dare la posizione delle ancore (`anchor`). Opzionali: `bind(renderer)` per avere l'atlante, `point_r` (raggio del puntatore per ancora), `near_log10` (fino a che zoom si sente l'audio "vicino") e `audio(mx, r, ts, near, rng)` per i suoni della scena. La mappa, il globo, lo spazio, l'HUD, il rewind e l'audio di base sono già pronti.

## 5. Idee per i prossimi video (twist verificati)

Ordinate per rapporto tra potenziale e lavoro. "Riuso" = quanto del codice esistente serve.

### 1. Il tizio che lascia spazio (phantom traffic jam)
- **Hook**: "What if every driver closed the gap?"
- **Protagonista**: quello lento che lascia un buco davanti e tutti gli tagliano la strada.
- **Escalation**: niente buchi, più macchine per chilometro, città più veloci... fino al primo ingorgo su Marte.
- **Twist**: nel 2008 Sugiyama mise 22 auto su un anello di 230 m e chiese di andare a 30 km/h costanti: l'ingorgo si formò da solo, senza nessun ostacolo. Nel test sul campo di Stern et al. (2018) una sola auto che teneva un'andatura regolare smorzava le onde, e secondo il riassunto del Dipartimento dei Trasporti USA i consumi scendevano fino al 40%.
- **Chiusura**: "The slow guy leaving a gap was right."
- **Riuso**: altissimo. Stesso modello IDM di `highway.py`, ma su un anello. È il più veloce da fare.
- Fonti: [ScienceDaily 2008](https://sciencedaily.com/releases/2008/03/080304075707.htm), [Stern et al., arXiv 1705.01693](https://arxiv.org/pdf/1705.01693), [US DOT ITS](https://www.itskrs.its.dot.gov/2019-b01402)

### 2. Chi ignora il gruppo d'imbarco
- **Hook**: "What if every passenger waited for their boarding group?"
- **Protagonista**: quello che si mette in fila quando chiamano il gruppo 1 e lui è nel 5.
- **Twist**: test di Steffen e Hotchkiss (2011, finto 757, 72 passeggeri). Dal fondo verso il davanti 6:11, a sezioni 6:54, a caso circa 5 minuti, metodo Steffen 3:36. Il metodo "ordinato" per sezioni è stato il più lento, e imbarcare a caso li batteva.
- **Chiusura**: "The guy who ignored his group was right."
- **Riuso**: medio (nuova scena: corridoio dell'aereo visto dall'alto, stessa logica di coda).
- Fonti: [arXiv 1108.5211](https://arxiv.org/pdf/1108.5211), [UChicago Magazine](https://mag.uchicago.edu/node/873)

### 3. Bottoni placebo
- **Hook**: "What if nobody pressed the crosswalk button?"
- **Protagonista**: quello che lo preme dieci volte di fila.
- **Twist**: nel 2004 il New York Times scoprì che più di 2,500 dei 3,250 pulsanti pedonali di New York non facevano niente. E dopo l'ADA del 1990 molti tasti "chiudi porte" degli ascensori sono disattivati (a New York invece devono funzionare per legge). Ci sono anche termostati finti negli uffici, ma le stime su quanti siano vanno dal 2 al 90%: meglio non citarli con un numero.
- **Chiusura**: "The button was never connected."
- **Riuso**: medio (incrocio con pedoni; la mappa di New York è già nei dati).
- Fonti: [Reason, sull'articolo NYT](https://reason.com/2004/02/27/buttons-down/), [NPR 2004](https://www.npr.org/2004/03/26/1794049/pressing-the-button-to-cross-a-manhattan-street), [CBS sugli ascensori](https://www.cbsnews.com/boston/news/door-close-elevator-button-dont-work-placebo)

### 4. Tutta la Gran Bretagna accende il bollitore
- **Hook**: "What if all of Britain made tea at the same time?"
- **Escalation**: la rete elettrica va in tilt, la Francia deve mandare corrente...
- **Twist**: è successo davvero. Il 4 luglio 1990, finiti i rigori di Inghilterra-Germania Ovest, la domanda salì di 2,800 MW in pochi minuti (circa 1.1 milioni di bollitori secondo National Grid). È ancora il record per un programma TV.
- **Chiusura**: "Britain did it. 26 million people. One kettle each."
- **Riuso**: alto per mappe e HUD (UK); la scena è una cucina vista dall'alto, semplice.
- Fonti: [Wikipedia, TV pickup](https://en.wikipedia.org/wiki/TV_pickup), [Drax](https://drax.com/?p=708)

### 5. Una città intera tira lo sciacquone
- **Hook**: "What if a whole city flushed at once?"
- **Twist**: Edmonton, finale olimpica di hockey Canada-USA 2010. Il gestore dell'acqua (EPCOR) ha misurato il consumo minuto per minuto: piatto durante la partita, picchi enormi a ogni intervallo.
- **Chiusura**: "Canada did it. Three times. Once per intermission."
- **Riuso**: alto (mappa del Canada, grafico del consumo come KPI che sale a scatti).
- Fonti: [UNC Environmental Finance Center](https://efc.web.unc.edu/2014/06/13/snapshot-the-big-flush/), [Chris Blattman](https://chrisblattman.com/blog/2010/03/08/graph-of-the-day-canadians-pee-between-periods/)

### 6. La monetina nella Fontana di Trevi (adatta anche a una versione italiana)
- **Hook**: "What if every tourist threw a coin in the Trevi Fountain?"
- **Escalation**: montagna di monete, Roma affonda, la BCE stampa più centesimi...
- **Twist**: lo fanno già. Circa 1.4 milioni di euro nel 2022 (le stime per il 2023 vanno da 1.5 a 1.6 milioni) e vanno alla Caritas di Roma, che ci finanzia mense ed empori solidali.
- **Chiusura**: "Make a wish. Someone gets dinner."
- **Riuso**: medio (scena della fontana dall'alto, mappa di Roma/Europa pronta).
- Fonti: [Euronews 2024](https://euronews.com/travel/2024/03/29/tourists-throw-over-1-million-into-italys-trevi-fountain-each-year-heres-what-happens-to-i), [Finestre sull'Arte](https://www.finestresullarte.info/en/news/protocol-renewed-for-three-years-trevi-fountain-coins-go-to-caritas-for-charitable-activities)

### 7. La città senza semafori
- **Hook**: "What if a city removed every traffic light?"
- **Escalation**: caos annunciato, incidenti, paralisi...
- **Twist**: Drachten (Paesi Bassi) l'ha fatto all'incrocio Laweiplein, circa 20,000 veicoli al giorno: secondo i funzionari gli incidenti sono diminuiti e sono meno gravi. I numeri precisi variano tra le fonti, quindi la didascalia resta generica: "Crashes went down."
- **Chiusura**: "The city with no rules was safer."
- **Riuso**: medio (rotatoria con auto, modello IDM riusabile).
- Fonti: [Grist](https://grist.org/article/shared-space/), [Big Think](https://bigthink.com/articles/want-less-car-accidents-get-rid-of-traffic-signals-road-signs)

### Da non fare
- La scala mobile di Holborn: è il video di riferimento, sarebbe una copia.
- "What if everyone jumped at the same time?": già fatto da tutti (Vsauce e altri).
- Twist senza fonte o con dati troppo contesi (i termostati finti con una percentuale precisa).

## 6. Note oneste

- **Genere diverso dal canale.** Il canale attuale è relax/ipnotico. What If è narrativo e "da discussione". Mischiarli sullo stesso canale confonde il pubblico e l'algoritmo: meglio un secondo canale o almeno una serie con playlist propria. Per questo `whatif` non è nella rotazione giornaliera di `daily.py`.
- **Ritmo realistico.** Ogni storia va scritta e verificata a mano: 1-2 a settimana, non una al giorno.
- **3D.** Il reference è renderizzato in 3D (manichini, stile Blender). Qui la scena è 2D vista dall'alto con prospettiva: gira ovunque, anche sulla VM di Hermes, ed è coerente con lo stile del canale. Il 3D vero si potrebbe fare con Blender da script, ma richiede GPU o tempi di render molto più lunghi.
- **Lingue.** Non c'è voce, quindi una versione italiana (o spagnola) costa solo la traduzione delle didascalie: stesse simulazioni, stesso render.
- **I commenti sono il motore.** Lo zipper merge, l'imbarco e il "chi lascia spazio" scatenano discussioni ("io lo faccio e mi suonano!"): è proprio quello che spinge questi video.
