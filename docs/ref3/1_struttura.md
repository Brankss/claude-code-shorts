# Reference 3 ("Maya / zombie, Day 1"): analisi della struttura del formato

Materiali usati: trascrizione e testi a schermo (`transcript.txt`), misure audio (`audio.txt`), fogli a 1 s (`sheet_a/b`), fogli a 0,5 s (`half_d1..d4`) e striscia delle didascalie (`cap_0..3`). Per il nostro episodio 1 ho ricalcolato la timeline dal motore (`rules.Timeline` sulla voce in cache): 100,26 s, 36 beat, 35 inquadrature, 232 parole.

Avvertenza: l'audio non posso ascoltarlo. Per i suoni mi baso solo sulle misure di `audio.txt`. In particolare non so dire se la card "ZOMBIES DON'T / KNOCK." (65.0-66.6) venga anche letta dal narratore: nella striscia delle didascalie dopo 64.5 non compare più niente.

---

## 0. I numeri a confronto

| | Reference | Nostro ep. 1 (DON'T ANSWER) |
|---|---|---|
| Durata | **68,1 s** | **100,26 s** |
| Parole del narratore | ~178 scritte (~190 contando i numeri pronunciati) in 0.2-64.4 s, cioè **~2,8-2,9 parole/s** | 232 in 0.12-95.91 s, cioè **2,42 parole/s** |
| Velocità per blocco | hook 3,4 p/s (22 parole in 0.2-6.6), parte centrale ~2,9, climax ~2,0 (58.8-64.4) | hook 2,9 p/s (15 parole in 0.12-5.36) |
| Inquadrature | 15 setup narrativi in 64,2 s, **durata media ~4,3 s**. Con neri e card finali sono 19 segmenti (3,6 s di media) | 35 inquadrature, **durata media 2,86 s** (mediana 2,8) |
| Inquadratura più lunga | 0.2-7.2 (≈7 s, esterno con push-in e orda), poi lo spaccato 11.7-17.7 (≈6 s) | 0.12-6.36 (6,24 s, hook + titolo) |
| Eventi visivi nuovi | ~55 in 68 s, **quasi uno al secondo**, senza contare i tick del countdown | non misurati |
| Premessa chiara (genere e minaccia) | **3.1-3.4 s** ("ZOMBIE APOCALYPSE") | **~13.5-14.9 s** ("Even one you know", "fog" a 14.94) |
| Pause "..." | **0,6-1,0 s**, solo prima della parola che rivela (5.4→6.1, 11.9→13.0, 26.9→27.7, 42.1→42.7) | **~0,3 s** fissi (0,24 s + 0,07 di coda, `shorts/rules.py:171`) |
| Dall'ultimo evento di storia alla fine | colpi 63.21 → fine 68.1: 4,9 s, di cui 1,5 s di twist e ~0,9 s di end card | domanda 93.24 → fine 100.26: 7 s, di cui **4,3 s di endcard** |

In sintesi: loro tagliano **meno spesso** di noi (4,3 s contro 2,86 s), ma ogni inquadratura cambia contenuto di continuo. Contatori, pillole, pallini e icone entrano ogni 0,5-1 s. Il ritmo nasce dalle informazioni nuove al secondo, non dalla frequenza dei tagli.

---

## 1. Beat map

| t | Narrazione | Cosa vediamo | Funzione | Inquadratura / taglio |
|---|---|---|---|---|
| 0.0-0.2 | (niente) | Nero | Frame morto, da evitare | 0,2 s |
| 0.2-4.0 | "Most people think the top floor is the *SAFEST* place in a *ZOMBIE* apocalypse." | Esterno di giorno, palazzo beige tra fumo e skyline, push-in continuo. A 3.5 una finestra accesa contornata (la sua) | **HOOK**: credenza comune più genere nominato a 3.1 | Setup 1: 0.2-7.2 (≈7 s), push-in |
| 4.4-6.6 | "Maya is about to learn... it's a *TRAP*." | A 5.5 l'orda entra dal basso, a 6.3 l'immagine vira al rosso su TRAP. Colpo di sub a ~5 s | **HOOK**: ribaltamento, nome della protagonista e promessa ("perché è una trappola?") | Stessa, il grade cambia sulla parola |
| 7.1-7.9 | "Day one." | Taglio a ~7.2: Maya di spalle alla finestra, gatto sul davanzale, card "ZOMBIE OUTBREAK / DAY 1" | Etichetta di serie | Setup 2: 7.2-11.7 (≈4,5 s) |
| 8.0-11.5 | "6:42 AM. The street below is already full." | La pillola "6:42 AM" si riempie (8.5) | **SETUP**: ora e minaccia già presente | Stessa |
| 11.7-13.8 | "At 7:15... the power *DIES*." | Taglio: spaccato del palazzo di 12 piani illuminato, "7:15 AM", tubo blu con "PUMP". Pausa di ~0,5-1 s tra "7:15" (11.9) e "THE" (13.0). Il buio scende a 13.3, "POWER GRID" con la X a 14.0. Sub a ~13 s, onset a 13.11 | **PROBLEMA 1** | Setup 3: 11.7-17.7 (≈6 s), push-in sul piano 10 verso 14.5 |
| 14.3-17.3 | "And on the tenth floor, no power means no *WATER*." | Pallino verde (Maya) al 10, goccia. A 16.5 goccia barrata, a 17.0 card "NO WATER / PUMPS PUSH WATER TO THE UPPER FLOORS", la colonna d'acqua cala | **INFO-DROP** e conseguenza | Stessa |
| 17.7-19.4 | "She has three minutes of pressure." | Taglio: bagno chiaro, card "WATER PRESSURE LEFT 02:57" che scala ogni 0,5 s (02:39 rossa a 21.0) | **SCADENZA** (conto alla rovescia) | Setup 4: 17.7-23.2 (≈5,5 s) |
| 19.6-21.0 | "She plugs the bathtub." | Rubinetto aperto, pillola dei litri 8 L (20.0) → 20 L (20.5) → 33 L (21.0) | **SOLUZIONE** con contatore | Stessa |
| 21.1-22.8 | "But old pipes are *LOUD*." | Onde gialle concentriche dai tubi (21.5-23.0) | **La soluzione crea il problema** ("but") | Stessa |
| 23.0-26.0 | "And sound *TRAVELS*... all the way down the *STAIRWELL*." | Taglio: spaccato scuro, archi gialli che scendono nella tromba delle scale fino al piano 1-2 (24.0-26.0) | **ESCALATION**: il problema si propaga | Setup 5: 23.2-26.3 (≈3,1 s) |
| 26.2-29.0 | "Six floors below... a *DOOR* creaks *OPEN*." | Taglio: corridoio rosso scuro, cartello del piano "4", porta nera che si apre (28.5) | **MINACCIA attivata**. Indizio: qualcuno apre le porte | Setup 6: 26.3-29.2 (≈2,9 s) |
| 29.2-34.3 | "Rule number one of a tall building: there's only one way *OUT*. And it leads straight to *THEM*." | Taglio: card "RULE #1 / ONE WAY OUT" sopra lo spaccato, linea rossa tratteggiata che scende (31.5-33.0) fino all'orda al piano terra, X rossa a 33.5. Sub a ~29 s | **INFO-DROP che paga l'hook** ("trap" spiegata) a metà video | Setup 7: 29.2-34.6 (≈5,4 s) |
| 34.6-37.7 | "So Maya does the only thing left. *SILENCE*." | Taglio: Maya inginocchiata di profilo che tiene il gatto, pillola "SILENCE" (37.0) | **SOLUZIONE** | Setup 8: 34.6-39.8 (≈5,2 s) |
| 37.8-39.7 | "Shoes off. Phone on mute." | Icone barrate: scarpe (38.0), telefono (39.0) | Micro-azioni concrete, a lista | Stessa |
| 39.9-41.9 | "The footsteps stop on the *SIXTH* floor." | Taglio: spaccato, pallino rosso che sale dal basso fino a "6TH FLOOR" (40.0-41.5). Maya, il pallino verde, è al 10 | **PICCO**: la minaccia è a 4 piani | Setup 9: 39.8-43.7 (≈3,9 s) |
| 42.1-43.6 | "Then... they go back down." | Il pallino rosso ridiscende (43.0-43.5) | **SOLLIEVO**. Indizio: si comporta come qualcuno che decide | Stessa |
| 43.8-48.3 | "*EIGHTY LITERS* in the tub. *NINE* in the toilet tank. *SIXTY* in the *WATER* heater." | Taglio: lo stesso bagno al buio, riempimenti blu luminosi con le pillole +80 L (44.0), +9 L (45.5), +60 L (47.0). Sub a ~44 s | **INVENTARIO**: consigli pratici reali | Setup 10: 43.7-48.4 (≈4,7 s) |
| 48.5-52.0 | "A hundred and forty *NINE LITERS*. *THIRTY SEVEN DAYS*." | Taglio: card "SUPPLIES — DAY 1" su legno. WATER 0 → 125 → 149 L (48.5-49.5), DAYS OF WATER ≈0 → 5 → 36 → 37 (50.0-51.5) contano in sincrono con la voce. FOOD ≈ 11 DAYS e PHONE 41% non vengono mai detti | **INVENTARIO e ricompensa** (37 in verde), più due semi per il Day 2 (cibo, batteria) | Setup 11: 48.4-52.1 (≈3,7 s) |
| 52.0-54.2 | "At night, she covers every window." | Taglio: notte, Maya di spalle con le braccia alzate, i pannelli coprono la finestra (53.5). Onset a 53.36 | **NOTTE**: prevenzione | Setup 12: 52.1-54.4 (≈2,3 s) |
| 54.4-58.6 | "In a dark city, a single *CANDLE* can be seen from over a *KILOMETER* away." | Taglio: esterno di notte, una sola finestra accesa con l'alone. Zoom indietro (57.0), pillola "VISIBLE FROM 1+ KM" e linea tratteggiata gialla (57.5) | **INFO-DROP e seme**: qualcuno può aver visto la luce | Setup 13: 54.4-58.8 (≈4,4 s), zoom indietro |
| 58.8-60.3 | "11:47 PM." | Taglio: buio, il gatto, "11:47 PM" rosso in alto. Onset a 59.56 | **SALTO TEMPORALE** (un'ora precisa annuncia un evento) | Setup 14: 58.8-62.8 (≈4 s) |
| 60.5-63.2 | "Pixel *FREEZES*. He stares at the *DOOR*." | A 61.0 si accendono gli occhi gialli del gatto | **MINACCIA** segnalata dall'animale | Stessa |
| 62.8-64.4 | "Three *KNOCKS*." | Taglio a ~62.8 sulla porta chiusa con la luce sotto. I tre colpi (62.85 / 63.03 / 63.21) cadono **sul taglio e prima della parola** (63.4-63.6) | **CLIMAX** | Setup 15: ≈1,6 s |
| 64.4-65.0 | (niente) | Nero, quasi silenzio (-30 dB) | Respiro prima del colpo | 0,6 s |
| 65.0-66.6 | (card) "ZOMBIES DON'T" ... "*KNOCK.*" | Testo bianco al centro, "KNOCK." rosso arriva da solo a 66.0. Il colpo più forte del video è a 66.68 (-10 dB RMS) | **TWIST / CLIFFHANGER**: cambia il senso di tutto, è un essere umano | ≈1,5 s |
| 66.5-68.1 | (niente) | Nero (66.5), poi la end card "PART 2 / WHO IS AT THE DOOR? / FOLLOW TO SURVIVE DAY 2" (67.0-~67.9), poi di nuovo nero (68.0) | **AGGANCIO DI SERIE** con un invito all'azione dentro la storia | Card di ~0,9 s, poi il loop |

---

## 2. Macro-struttura

| Atto | Tempo | Contenuto | Come finisce |
|---|---|---|---|
| 0. Hook | 0.2-7.0 (7 s) | Credenza ribaltata, genere, nome, orda | "it's a *TRAP*" (6.3), sub e virata al rosso |
| 1. Setup | 7.1-11.5 (4,5 s) | DAY 1, 6:42 AM, la strada piena | "already full": la minaccia è già sotto |
| 2. Catena dell'acqua | 11.7-22.8 (11 s) | Blackout → niente acqua → 3 minuti → riempire la vasca | "But old pipes are *LOUD*" (21.1): la soluzione apre il problema dopo |
| 3. Catena del suono | 23.0-43.6 (20,6 s) | Il suono scende → la porta si apre → RULE #1 → silenzio → passi al 6° → tornano giù | Sollievo (42.1-43.6), ma resta aperta la domanda "chi ha aperto la porta?" |
| 4. Inventario | 43.8-52.0 (8,2 s) | 80 + 9 + 60 = 149 L → 37 giorni | Ricompensa in verde ("*THIRTY SEVEN DAYS*") |
| 5. Notte | 52.0-58.6 (6,6 s) | Copre le finestre, la candela si vede a 1 km | Seme: la luce è visibile |
| 6. Climax e cliffhanger | 58.8-68.1 (9,3 s) | 11:47 PM → il gatto → tre colpi → twist → PART 2 | "ZOMBIES DON'T / KNOCK." e la domanda aperta |

**Ogni 5-10 s arriva un problema nuovo o una svolta.** Le svolte minori cadono ogni 2-4 s: 6.3 trap, 11.1 full, 13.4 dies, 16.9 no water, 18.9 tre minuti, 20.1 vasca, 22.2 loud, 23.6 travels, 28.6 open, 33.8 them, 36.9 silence, 41.1 sixth, 43.2 down, 47.8 inventario, 51.5 37 giorni, 53.6 finestre, 58.1 un chilometro, 58.8 11:47, 60.8 freezes, 63.6 knocks, 66.0 knock.

**Gli anelli aperti si sovrappongono, così in ogni secondo almeno una domanda resta aperta:**
- A, "perché l'ultimo piano è una trappola?": aperto a 6.3, chiuso a 34.3.
- B, "il rumore li porterà da lei?": aperto a 22.2, chiuso a 43.6.
- C, "chi c'è nel palazzo?": aperto a 28.6 (la porta), rinforzato a 42.1 (tornano indietro) e a 58.1 (la luce si vede), **mai chiuso**. È il gancio del Part 2.

L'unico tratto senza minaccia attiva è 43.8-52.0 (~8 s). Lo tengono in piedi i numeri che contano (149 L, 37 giorni) e il colore verde come ricompensa.

**L'audio segna gli atti.** I colpi di sub cadono a ~5 s (orda), ~13 s (blackout), ~29 s (RULE #1), ~44 s (primo +80 L) e ~66 s (KNOCK): cinque colpi per cinque svolte, nessuno sprecato.

**Pochi set riusati con luci diverse.** Lo spaccato del palazzo torna 4 volte (11.7-17.7, 23.2-26.3, 29.2-34.6, 39.8-43.7, ≈18 s, il 27% del video) come mappa fissa: pallino verde Maya, pallino rosso la minaccia, colonna blu l'acqua, archi gialli il suono, linea rossa la via d'uscita. Il bagno compare due volte (chiaro 17.7, buio 43.7), la finestra tre (giorno in piedi 7.2, inginocchiata 34.6, notte 52.1), l'esterno due (giorno 0.2, notte 54.4).

---

## 3. Come funziona l'hook (0-7 s)

1. **La prima parola arriva a 0.2 s** e la didascalia si costruisce parola per parola ("MOST" 0.2, "MOST PEOPLE" 0.5, "MOST PEOPLE THINK" 0.7). Il frame nero iniziale dura solo 0,2 s, ma resta un difetto.
2. **Una credenza che lo spettatore ha davvero.** Nella narrativa zombie "salire in alto" è il riflesso classico, quindi il ribaltamento colpisce un'idea che chi guarda condivide. Non è una stranezza qualsiasi.
3. **Genere e posta in gioco in 3,4 s**: "SAFEST" giallo (2.1), "ZOMBIE" rosso (3.1), "APOCALYPSE" (3.4). Nessuno deve indovinare di che video si tratta.
4. **Una vittima con un nome, al futuro**: "Maya is about to learn..." (4.4-5.4). "About to learn" promette una lezione, e lo spettatore si aspetta di imparare qualcosa anche lui.
5. **Una pausa di 0,7 s** (5.4 → 6.1) prima del verdetto "it's a *TRAP*" (6.1-6.6).
6. **L'immagine sale insieme alla voce**: palazzo tranquillo, poi la finestra di Maya contornata (3.5), l'orda (5.5) con il sub (~5 s), la virata al rosso su TRAP (6.3).
7. **La spiegazione arriva solo a 29.2-34.3** ("one way out... straight to them"). L'hook promette un'informazione e la consegna a metà video, quindi tiene fino alla metà. Poi a 28.6 si è già aperto l'anello successivo.

Il nostro hook ("Imagine you hear your mom calling from the backyard... while she's texting you. From work.", 0.12-5.36) è di un altro tipo: un paradosso sensoriale, cioè un mistero, non una lacuna di conoscenza. È forte, ma chiede due passaggi mentali ("while she's texting", poi "From work") e non dice il genere. "Fog" arriva a 14.94 e la regola del mondo a 13.45-14.94.

---

## 4. La catena problema → soluzione → nuovo problema

| # | t | Tipo | Anello |
|---|---|---|---|
| 1 | 13.1-13.8 | Problema | La corrente muore |
| 2 | 14.3-17.3 | Conseguenza e informazione | Niente pompe, niente acqua al 10° piano |
| 3 | 17.7-19.4 | Scadenza | 3 minuti di pressione (countdown 02:57 → 02:39) |
| 4 | 19.6-21.0 | Soluzione | Tappa la vasca (8 → 33 L) |
| 5 | 21.1-22.8 | **La soluzione causa un problema** | I tubi vecchi fanno rumore |
| 6 | 23.0-26.0 | Propagazione | Il suono scende per le scale |
| 7 | 26.2-29.0 | Minaccia | Una porta si apre 6 piani sotto |
| 8 | 29.2-34.3 | Regola e trappola | "ONE WAY OUT", e porta dritta a loro |
| 9 | 34.6-39.7 | Soluzione | Silenzio, via le scarpe, telefono muto |
| 10 | 39.9-41.9 | Picco | I passi si fermano al 6° |
| 11 | 42.1-43.6 | Sollievo | Tornano giù |
| 12 | 43.8-52.0 | Inventario | 149 L, 37 giorni (FOOD 11 DAYS e PHONE 41% scritti ma non detti) |
| 13 | 52.0-54.2 | Soluzione preventiva | Copre le finestre |
| 14 | 54.4-58.6 | Rischio e seme | Una candela si vede a più di 1 km |
| 15 | 58.8-64.4 | Minaccia | 11:47, il gatto si blocca, tre colpi |
| 16 | 65.0-66.6 | Twist | Gli zombie non bussano |

Il meccanismo più intelligente: **le soluzioni lasciano le prove per il twist finale.** La porta che si apre (28.6), i passi che si fermano e tornano indietro come farebbe qualcuno che decide (41.1-43.6) e la luce visibile da 1 km (54.4-58.6) diventano, dopo "ZOMBIES DON'T KNOCK" (65-66.6), indizi che c'è un essere umano nel palazzo e che può averla sentita e vista. A un secondo passaggio il video si rilegge da capo, e questo spinge rewatch e teorie nei commenti.

Altro dettaglio: **la regola arriva dopo il problema, come risposta.** La porta si apre a 28.6 e la "RULE #1" a 29.2. Noi facciamo il contrario: prima la regola ("Rule number one: cover every window.", 24.90), poi la giustificazione ("If you can see out... it can see in.", 27.36).

---

## 5. Ritmo

- **Velocità della voce**: ~2,85 p/s in media. 3,4 nell'hook, ~2,9 al centro, **~2,0 nel climax** (58.8-64.4: "11:47 PM. Pixel freezes. He stares at the door. Three knocks."). Nel finale le parole rallentano mentre i tagli accelerano: setup di 4,4 s (54.4), 4,0 (58.8), 1,6 (62.8), 0,6 di nero (64.4), 1,5 (65.0), 0,5 di nero (66.5), ~0,9 (67.0).
- **Le pause** sono poche e lunghe (0,6-1,0 s) e cadono solo davanti alla parola che rivela: TRAP, DIES, DOOR, "they go back down". La voce per il resto è secca e senza respiri.
- **Inquadrature**: media ~4,3 s, la più lunga ≈7 s (0.2-7.2), la più corta 1,5-1,6 s (porta 62.8, card del twist 65.0). Nessuna resta ferma, perché c'è sempre un push-in, uno zoom indietro o un contatore che si muove.
- **Didascalie**: 1-4 parole che si accumulano, con il **colore che ha un significato**. Rosso è pericolo (ZOMBIE, TRAP, DIES, DOOR, THEM, SIXTH, FREEZES, KNOCKS), giallo/arancio è informazione chiave (SAFEST, LOUD, TRAVELS, STAIRWELL, SILENCE, CANDLE, KILOMETER), blu è acqua (EIGHTY LITERS, NINE, SIXTY), verde è esito positivo (THIRTY SEVEN DAYS). Le altre parole restano bianche. Il senso si capisce anche senza audio. Noi coloriamo di lime la parola che si sta dicendo (`shorts/rules.py:456-481`), e il colore segue il tempo, non il significato.
- **Numeri detti a voce**: ~14 in 64 s (6:42, 7:15, tenth, three minutes, six floors, sixth, 80, 9, 60, 149, 37, un chilometro, 11:47, three). La precisione rende credibile la storia. Noi i numeri li mettiamo quasi solo nell'HUD.

---

## 6. Cliffhanger e aggancio di serie

1. **Le tre bussate si sentono prima di essere dette**: i colpi sono a 62.85, 63.03 e 63.21, sul taglio verso la porta, mentre "THREE KNOCKS" compare a 63.4-63.6. Lo spettatore sente, poi gli viene confermato.
2. **0,6 s di quasi silenzio sul nero** (64.4-65.0), poi la card "ZOMBIES DON'T" (65.0). "KNOCK." arriva **da sola e in rosso un secondo dopo** (66.0) sul colpo più forte del video (66.68). Il ritardo sull'ultima parola fa completare la frase allo spettatore.
3. **Il twist ribalta la minaccia senza cambiare mondo**: dagli zombie a una persona. È il cliché "il vero mostro sono gli uomini", ma qui è preparato da tre indizi (28.6, 42.1, 54.4-58.6).
4. **End card cortissima** (~0,9 s, 67.0-67.9) con una domanda **aperta** ("WHO IS AT THE DOOR?", in rosso), seguita dal nero a 68.0 e dal loop. Chi guarda arriva in fondo quasi per forza e riparte. La domanda chiede teorie ("è quello del 4° piano"), non un voto.
5. **L'invito a seguire sta dentro la storia**: "FOLLOW TO SURVIVE DAY 2". Seguire il canale diventa sopravvivere. C'è un'incoerenza: "PART 2" e "DAY 2" convivono nella stessa card.
6. **Semi lasciati senza parlarne**: FOOD ≈ 11 DAYS contro 37 giorni d'acqua, PHONE 41% (49.0-52.0). Il problema del Day 2 è già sullo schermo, solo per chi mette in pausa.

---

## 7. Punti deboli e affermazioni dubbie

- **L'hook non torna con la storia**: "the top floor is the safest place" (0.2-4.0), ma Maya è al **10° di 12** (spaccato 11.7-17.7). Non è all'ultimo piano.
- **"Rule number one of a tall building: there's only one way out"** (29.2-31.9) è presentata come legge universale ed è discutibile. Negli USA un residenziale di 12 piani ha quasi sempre due scale per la normativa antincendio. In UK e in parte d'Europa le torri con una sola scala sono state comuni. Va bene come finzione, ma i commenti "actually..." sono garantiti (che per l'engagement non è un male).
- **"RULE #1" senza una #2**: qui la regola è solo un'etichetta. Il formato a regole lo stanno usando anche altri, e la card rossa "RULE #n" con il testo condensato è quasi uguale alla nostra. Il nostro elemento distintivo deve restare la #4 come colpo finale.
- **Una piccola incoerenza**: la porta si apre al piano 4 (26.3-29.2), ma a 40.0 il pallino rosso dei passi parte dal piano terra.
- **Logica della notte ambigua**: "she covers every window" (52.0-54.2), poi l'inquadratura successiva mostra una finestra accesa che brilla (54.4-58.8). Si legge come spiegazione ("ecco perché"), ma anche come "troppo tardi". Forse è voluto (prepara i colpi), però confonde.
- **"Three minutes of pressure"** (17.7) è un numero inventato. Riempire 80 L (43.8) in meno di 3 minuti con la pressione che cala vuol dire ~27 L/min, al limite di un rubinetto da vasca a pressione piena. Il countdown poi è accelerato: 18 s di timer in 3 s reali (02:57 a 18.0, 02:39 a 21.0).
- **Le cose giuste**: "Pumps push water to the upper floors" (17.0) è vero per i palazzi oltre i ~6 piani senza serbatoio sul tetto. 149 L / 37 giorni fa ~4 L al giorno, in linea con la regola d'emergenza di un gallone (3,8 L) a persona al giorno, ma ignora il gatto. Scaldabagno e cassetta del WC come riserve sono consigli reali. La candela visibile "from over a kilometer" è prudente: uno studio del 2015 (Krisciunas e Carona) stima ~2,6 km in condizioni ideali.
- **Il tratto di sollievo 43.8-52.0** (~8 s senza minaccia) è rischioso per la retention. Lo salvano i contatori, ma è il punto più debole del video.
- **Il nome del gatto, Pixel, arriva solo a 60.5.** Funziona perché il gatto si vede dalla 7.2, ma come personaggio non ha nessuna preparazione.
- **Frame nero a 0.0-0.2**: come anteprima è peggio di qualsiasi immagine.

---

## 8. Confronto con il nostro episodio 1

### La nostra timeline (dal motore)

| Fase | t | Contenuto |
|---|---|---|
| Hook e titolo | 0.12-6.36 | Paradosso della mamma, card "DON'T ANSWER" (5.36) |
| Interfaccia del telefono | 6.36-14.94 | Messaggio della mamma, allerta "don't answer any voice... Even one you know" (3 inquadrature di UI, 8,6 s) |
| Dimostrazione | 14.94-24.90 | Nebbia piena di voci, il vicino segue la moglie, lei è dietro di lui |
| Regole 1-3 | 24.90-45.93 | Cover every window / unplug every speaker / family password, più l'aggiornamento dell'allerta "IT REPEATS WHAT IT HEARS" |
| Escalation per sottrazione | 45.93-56.77 | Le voci si fermano, il vicino torna, la mamma smette di scrivere, blackout (54.72) |
| Mezzanotte | 56.77-74.70 | Voce di Ellie, torcia, regola #4 (70.75-74.70) |
| Prove a favore e contro, seconda minaccia | 74.70-90.47 | blue kite, "Read 11:51 PM", il telefono della mamma, colpi su cucina e corridoio, "It's behind her" |
| Domanda e fine | 90.47-100.26 | "So... do you answer her?" (93.24), endcard di 4,3 s |

### Dove cadono i momenti chiave

| Momento | Reference | Nostro ep. 1 |
|---|---|---|
| Premessa chiara | 3.4 | ~14.9 |
| Primo problema fisico | 13.1 (blackout) | 18.0-24.9 (il vicino, una dimostrazione) |
| Prima regola | 29.2 (dopo il problema) | 24.90 (prima della giustificazione) |
| Hook ripagato | 29.2-34.3 | 10.05-14.94 (l'allerta spiega la contraddizione) |
| Sollievo vero | 42.1-52.0 | nessuno (45.93 "the voices stop" è un falso sollievo) |
| Inventario | 43.8-52.0 | nessuno (solo "VISIBILITY ... FT" nell'HUD) |
| Blackout | 13.1, fa partire la storia | 54.72, escalation tardiva |
| Minaccia alla porta o alla finestra | 62.85 | 56.77 |
| Twist o rivelazione | 65.0-66.6 | 70.75-74.70 (regola #4), 78.59-81.39 ("Someone read it.") |
| Domanda | 67.0 (aperta, solo testo) | 93.24 (sì/no, voce e card) |
| Fine | 68.1 | 100.26 |

### Cosa fanno loro e noi no
1. **Una catena causale dall'inizio.** Da 11.7 a 64.4 ogni anello è un "but" o un "so". Nel nostro primo tempo (24.90-45.93) le regole 1-3 sono una lista parallela ("and then"): nessuna regola nasce dall'effetto collaterale della precedente. La nostra parte causale c'è, ma comincia solo a 45.93.
2. **La regola come risposta a un problema appena visto** (28.6 → 29.2), non come titolo seguito dalla spiegazione.
3. **Informazioni utili nella vita vera** (scaldabagno, cassetta del WC, 4 L al giorno, finestre oscurate): fanno salvare e condividere. Le nostre regole valgono solo nel mondo della nebbia. In realtà una ce l'abbiamo: la **password di famiglia** è un consiglio reale contro le truffe con voce clonata dall'IA. Mi risulta che l'FBI l'abbia raccomandata in un avviso IC3 di dicembre 2024 (da verificare prima di citarlo). Nell'episodio però non lo diciamo.
4. **Un inventario con i contatori** ("SUPPLIES — DAY 1", 48.4-52.1) e un **conto alla rovescia** visibile (18.0-21.0). Sono progressi misurabili, come nell'interfaccia di un videogioco.
5. **Una mappa ricorrente** (lo spaccato, 4 volte), che dice dov'è la minaccia rispetto alla protagonista. Noi abbiamo dei frammenti (`house_ext` con il pin "YOU · 41 LINDEN ST" e gli anelli delle voci, `street_top`) ma non una mappa fissa da riprendere.
6. **Colori delle didascalie con un significato** invece del karaoke.
7. **Più velocità e meno durata**: 2,85 contro 2,42 p/s, 68 contro 100 s.
8. **Un finale compresso**: dal climax al loop passano ~4,9 s, con la card finale di ~0,9 s. Noi abbiamo 7 s dopo la domanda, di cui 4,3 di endcard di solo brand (`shorts/pov_stories.py:171`, `hold=4.3`).
9. **Il suono prima della parola** sul climax (i colpi a 62.85, la didascalia a 63.4) e **0,6 s di silenzio** prima del twist.
10. **Il blackout come scintilla** (13.1) invece che come escalation tarda (noi a 54.72): il mondo si rompe subito.
11. **Un animale che sente la minaccia per primo** (60.5-62.8): un cliché che costa poco e funziona.

### Cosa facciamo noi e loro no
1. **La seconda persona** ("Imagine you"): l'immedesimazione è diretta. Loro usano la terza persona con Maya quasi sempre di spalle (7.2-11.7, 52.1-54.4), un compromesso simile al nostro stickman senza faccia.
2. **Un'ossatura di 4 regole con il ritorno della #4.** Lo spettatore sa a che punto è (1/4, 2/4...) e la #4 premia chi era attento (allerta a 10.05-14.94, ritorno a 70.75-74.70). La loro "RULE #1" non ha seguito.
3. **Un personaggio che parla** (Ellie, voce e filtro diversi, con il cartellino). Loro hanno solo il narratore.
4. **Prove a favore e contro** (il telefono della mamma contro "Read 11:51 PM"), cioè un dilemma morale. Loro hanno solo un mistero.
5. **Una domanda sì/no** con un meccanismo per i commenti (BLUE KITE / NOT TONIGHT). Loro chiedono un'ipotesi, che dà commenti più lunghi ma meno numerosi.
6. **Un brand riconoscibile**: card del titolo a 5.36 e outro fisso. Loro hanno solo "ZOMBIE OUTBREAK / DAY 1" e un "PART 2" un po' confuso.
7. **Indizi più sottili e più numerosi** (il vicino con il collo piegato alle 7:52, "MOM · READ 11:51 PM" nell'HUD prima della rivelazione).

Una nota di genere: questo reference e "14 Floors Up" usano gli stessi motivi (piano alto, vasca da riempire, corrente che salta, qualcuno che bussa di notte). È una formula che si sta consolidando. Il nostro Day 1 se ne distingue (voce fuori dalla finestra, colpi sui vetri), e nel Day 2 conviene non scivolare sul "knock at the door".

---

## 9. Applicazione al Day 2 (giovedì 22/10)

Uno scheletro di **75 s**, tutti tempi indicativi:
- **0-6 s, hook in seconda persona con credenza ribaltata.** Il piano di lancio prevede già come prima riga "Most of you answered her." (`docs/LAUNCH.md`, riga 207), che è proprio la forma "Most people...": maggioranza → ribaltamento. Entro 4 s vanno dette le parole "fog" e "voice".
- **6-12 s, etichetta DAY 2 e primo problema fisico subito** (sul modello del blackout alla 13.1).
- **12-40 s, regole 1-3 in catena**: problema → regola come risposta → effetto collaterale che apre la regola dopo. Si controlla così: tra due regole consecutive si deve poter dire "but" o "so".
- **~30 s, ripagare l'hook**, dopo aver aperto il mistero successivo qualche secondo prima.
- **40-50 s, card di inventario con i contatori**, riusando `kinetic.rolling_number` (`shorts/kinetic.py:195`) in un nuovo `card kind` in `rules.py`. Per esempio batteria del telefono, ore all'alba, visibilità, più 1-2 righe non lette a voce che preparano il Day 3. Poi un sollievo vero.
- **50-62 s, notte e un indizio legato a un'azione del protagonista.**
- **62-72 s, minaccia (suono prima della parola) → "You already know rule number four." → card del twist di 3-4 parole con l'ultima che arriva dopo ~1 s in rosso** sul colpo più forte, preceduta da 0,5 s di quasi silenzio.
- **72-75 s, domanda sì/no ed endcard da 1,5 s al massimo.**

Ritocchi al motore:
1. Pausa dei "..." configurabile per singolo beat (oggi 0,24 s fissi, `shorts/rules.py:171`): 0,6-0,9 s solo sulle 4-5 parole che rivelano.
2. `speed` del narratore da 1.22 a ~1.3 per arrivare a ~2,8 p/s, da sentire in cuffia.
3. Colori delle didascalie per categoria su 1 parola chiave per gruppo, il resto bianco (`shorts/rules.py:456-481`).
4. Endcard con `hold` ≤1.5 (`shorts/pov_stories.py:171`).
5. Una scena "mappa" dall'alto di Linden St (TU, la casa di Ellie, il vicino, il bordo della nebbia), da riusare 3-4 volte aggiungendo ogni volta un elemento.


## TAKEAWAYS
- Scrivi le regole 1-3 del Day 2 come una catena causale, non come una lista. Ogni regola risponde al problema appena visto, e il suo effetto collaterale apre la regola successiva. Il reference lo fa da 11.7 a 64.4 s (vasca → tubi rumorosi → suono nelle scale → porta aperta → RULE #1). Il nostro Day 1 è a lista da 24.90 a 45.93 s. Si controlla così: tra due regole consecutive si deve poter dire 'but' o 'so'.
- Fai arrivare la regola dopo il problema, come risposta: la porta si apre a 28.6 e la RULE #1 compare a 29.2. Non come titolo seguito dalla spiegazione, come facciamo noi con 'Rule number one: cover every window.' (24.90) e 'If you can see out...' (27.36).
- Hook in seconda persona con una credenza ribaltata, che nomini la minaccia entro 4 s ('fog' e 'voice'). Nel reference il genere è chiaro a 3.4 s, nel nostro Day 1 a ~14.9 s. 'Most of you answered her.', già previsto in LAUNCH.md come prima riga del Day 2, ha esattamente questa forma. Ripaga l'hook verso i 30 s, dopo aver già aperto il mistero successivo.
- Aggiungi a ~60% del video una card di inventario con i numeri che contano in sincrono con la voce, riusando kinetic.rolling_number (shorts/kinetic.py:195). Per esempio batteria, ore all'alba, visibilità, più 1-2 righe mai lette a voce che preparano il Day 3. Il modello è 'SUPPLIES — DAY 1' a 48.4-52.1 s, con FOOD 11 DAYS e PHONE 41% non detti.
- Porta il Day 2 a 70-80 s e ~2,8 parole/s (oggi 100 s e 2,42 p/s): speed del narratore da 1.22 a ~1.3, da verificare in cuffia, e meno tempo sulle schermate del telefono (6.36-14.94 nel Day 1). Usa pause lunghe (0,6-0,9 s) solo davanti alle 4-5 parole che rivelano, invece dei 0,24 s fissi su ogni '...' (shorts/rules.py:171).
- Comprimi il finale: suono prima della parola sul climax (colpi a 62.85, didascalia a 63.4), 0,5 s di quasi silenzio, card del twist di 3-4 parole con l'ultima che arriva dopo ~1 s in rosso sul colpo più forte, poi la domanda sì/no ed endcard da 1,5 s al massimo (oggi hold=4.3 in shorts/pov_stories.py:171).
- Colora le didascalie in base al significato, non al tempo: rosso per il pericolo, giallo per l'informazione chiave, un colore fisso per le parole delle regole, verde per gli esiti positivi, una parola chiave per gruppo e il resto bianco. Va a sostituire il karaoke lime di shorts/rules.py:456-481, così la storia si capisce anche senza audio.
- Crea una mappa ricorrente (la strada di Linden St vista dall'alto, con TU, la casa di Ellie, il vicino e il bordo della nebbia) da riusare 3-4 volte, aggiungendo ogni volta un elemento. Il reference usa lo spaccato del palazzo per ~18 s su 68 (27%) per far capire quanto è vicina la minaccia.
- Fai in modo che ogni soluzione del protagonista lasci una prova per il twist finale, come la porta, i passi che tornano indietro e la candela prima di 'ZOMBIES DON'T KNOCK' (65-66.6 s). Servono almeno 3 indizi legati alle tue azioni, così il finale si rilegge e chi guarda torna indietro a rivederlo.
- Aggiungi un consiglio utile nella vita vera per episodio. Il nostro 'family password' contro le voci clonate dall'IA è un consiglio reale (mi risulta da un avviso FBI IC3 del dicembre 2024, da verificare prima di citarlo): dillo esplicitamente in una card o in didascalia per spingere salvataggi e condivisioni, come fa il reference con scaldabagno e cassetta del WC (43.8-48.3).