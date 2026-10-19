# Correzioni del critico (hanno la precedenza sulle analisi 1-5)

Il critico ha ricontrollato le analisi sui fotogrammi a 10 fps e sulla forma d'onda. Dove un'analisi dice una cosa diversa, vale questa.

## Errori nelle analisi

### struttura (§1 beat map 64.4-66.6, §5, §6.2), routine (§1 slot 'Twist su nero' e 'scheletro audio'), immedesimazione (§1, ultima riga). L'errore viene da audio.txt e transcript.txt; stile §1.10 invece ha i tempi giusti.

**Sbagliato:** struttura: "Nero, quasi silenzio (-30 dB) 64.4-65.0 (0,6 s)", card "ZOMBIES DON'T" a 65.0, "'KNOCK.' rosso arriva da solo a 66.0. Il colpo più forte del video è a 66.68 (-10 dB RMS)". routine: "'KNOCK.' in rosso (66,0 s): è il punto più forte del video (−10 dB RMS)" e "un secondo di vuoto (64–65 s)". immedesimazione: "silenzio a -30 dB (64-65), 'ZOMBIES DON'T' (65.0) → 'KNOCK.' (66.0)".

**Giusto:** L'inquadratura della porta dura fino a 64.4. Il nero è un solo fotogramma (64.5). "ZOMBIES DON'T" entra a 64.6 insieme alla voce. "KNOCK." rosso compare di colpo, senza animazione, a 65.5, nello stesso fotogramma del colpo più forte del video (65.45-65.50, -5,7 dB RMS su 50 ms). Quello a 66.5-66.7 è solo un secondo rimbalzo del sub sul taglio al nero. Il quasi silenzio (63.85-64.5, da -30 a -43 dB) cade sulla porta chiusa, dopo "THREE KNOCKS", non sul nero. Fra le due righe passano 0,9 s (64.6→65.5), non 1 s a partire da 65.0.

**Prova:** Fotogrammi a 10 fps in ref3/f10 (f_k = (k-1)/10 s, mappatura verificata su "MOST" a 0.2 e sul taglio a 7.1). f0645 (64.4) è ancora la porta. f0646 (64.5) è nero, luminosità media 4,1. f0647 (64.6) è il primo con testo bianco. A f0656 (65.5) i pixel rossi passano da 0 a 12.625 in un fotogramma. f0666 (66.5) è nero, f0667-f0670 sono la dissolvenza, f0671 (67.0) è la card. In ref.wav il picco full-band è -5,7 dB a 65.50 (sotto 70 Hz -6,8 dB, +24 dB sopra la mediana); a 66.55 si arriva solo a -8,1 dB. La cella 65.5 di half_d4 è presa un attimo prima del pop.

### struttura (§2 'L'audio segna gli atti'), routine (§1 'Uno scheletro audio'), stile (§2 'Colpi di sub sincronizzati'). Anche questo viene da audio.txt.

**Sbagliato:** "I colpi di sub cadono a ~5 s, ~13 s, ~29 s, ~44 s (primo +80 L) e ~66 s: cinque colpi per cinque svolte, nessuno sprecato". stile: "44,2 s: 45,6 dB, più debole. Prima pillola '+80 L'". Inoltre "X rossa a 33.5" (struttura, routine, stile, immedesimazione).

**Giusto:** A 44 s non c'è nessun colpo di sub. Sotto 70 Hz, fra 43.7 e 44.2 il livello è fra -33 e -44 dB, cioè pari o inferiore al tappeto (mediana -30,7 dB). L'energia fra 43.8 e 44.3 è la voce: "EIGHTY" detto forte (-10 dB nella banda voce), subito dopo un vuoto di 0,1-0,15 s (43.65-43.75, -32/-39 dB). La banda sotto i 150 Hz usata da audio.txt e da stile contiene la fondamentale del narratore (F0 92-118 Hz), quindi scambia la voce per un colpo. Manca invece un colpo vero a 33.0-33.1: -13,6 dB sotto 70 Hz, +17 dB sopra la mediana, più forte di quello sulla RULE #1 (29.6, +12,9 dB). È sincronizzato con la X rossa sull'orda, che compare a 33.1-33.2 e non a 33.5, mentre la didascalia dice ancora "AND IT LEADS", prima di "STRAIGHT TO THEM". I colpi veri sono: 5.6 orda, 13.2 blackout, 29.6 RULE #1, 33.0 X sulla via d'uscita, 65.5 KNOCK.

**Prova:** Classifica dei livelli sotto 70 Hz su finestre da 100 ms in ref.wav: 65.5 (-6,8), 5.6 (-10,0), 13.2 (-11,8), 33.0 (-13,6), 29.6 (-17,8); il 44 non compare fra i primi 14. Nell'inviluppo a 43.9: banda voce -10,4 dB, sotto 150 Hz -18,7 dB. Fotogrammi: f0332 (33.1) X appena visibile, f0333 (33.2) X piena; la linea tratteggiata è già arrivata in fondo a f0329 (32.8).

### stile (§0 'Non ho visto flash né scossoni', §1.9 'Dissolvenze, whip, flash o scossoni non se ne vedono')

**Sbagliato:** Montaggio fatto solo di tagli netti, senza flash, scossoni o dissolvenze.

**Giusto:** I tre colpi alla porta sono tre flash a pieno schermo (62.9, 63.1, 63.2), e sul terzo c'è anche uno scossone. Sono gli unici flash di tutto il video: l'effetto è tenuto da parte per il climax. Ci sono anche due dissolvenze dal nero: l'apertura (0.0-0.2) e la end card (66.6-67.0).

**Prova:** Luminosità media: f0629 31,3 → f0630 38,7 → f0631 31,6 → f0632 38,3 → f0633 44,3 → f0634 31,8. Anche gli angoli del quadro passano da 15 a 22-26, quindi il flash è su tutta l'immagine, non solo sulla luce sotto la porta. Il bordo della porta salta da x=157 a x=132 a f0633 (lo scossone). Su tutti i 680 fotogrammi la ricerca di picchi di un solo fotogramma trova solo 62.9 e 63.2. Noi ne usiamo due nel Day 1 (pov_stories.py:38 e :137), coerente con l'idea di usarli poco.

### struttura (§1 riga 0.0-0.2, §3 punto 1, §7 ultimo punto) e stile (§1.9)

**Sbagliato:** "0.0-0.2 Nero. Frame morto, da evitare" e "come anteprima è peggio di qualsiasi immagine".

**Giusto:** È una dissolvenza dal nero di 0,2 s. Il primo fotogramma è già l'esterno del palazzo al 14% di luminosità, e la voce entra a 0.2 a pieno volume. Non è un fotogramma morto. Inoltre su TikTok e Shorts la copertina si sceglie a parte.

**Prova:** f0001 ha media 16,1 contro 112,4 di f0003, con correlazione della struttura 0,98 (stessa immagine). ref.wav: -63 dB a 0.00, -10 dB a 0.25.

### struttura (§0 tabella 'Pause "..."', §5 'Le pause', §9 'Ritocchi al motore' punto 1)

**Sbagliato:** "Pause '...' 0,6-1,0 s, solo prima della parola che rivela (5.4→6.1, 11.9→13.0, 26.9→27.7, 42.1→42.7)" contro i nostri ~0,3 s, "la voce per il resto è secca e senza respiri", e la proposta di portare la pausa a 0,6-0,9 s.

**Giusto:** Quei valori sono distanze fra gli attacchi delle didascalie e includono la durata della parola. Nella banda voce i silenzi veri sono di 0,30-0,40 s: 12.72-13.02, 27.32-27.70, 42.30-42.70, e circa 0,35 s fra 5.7 e 6.05 (coperto dall'effetto dell'orda). Sono solo ~0,1 s più lunghi dei nostri (0,24 + 0,05 s, rules.py:171). I respiri più lunghi (0,5-0,6 s) cadono dopo la parola-evento, non prima: dopo DIES (13.82-14.36), prima e dopo SILENCE (36.52-37.06 e 37.22-37.80), fra LITERS e THIRTY SEVEN (50.06-50.62), dopo FREEZES (61.28-61.76). La regola da copiare è quindi "respiro dopo la parola che cambia lo stato". Allungare i "..." a 0,9 s ci renderebbe più lenti del reference.

**Prova:** ref.wav filtrato 300-3400 Hz, finestre da 20 ms, soglia 18 dB sotto il 90° percentile. Attacchi delle parole da cap_0 e cap_1 (es. "AT 7:15" 11.9 e "THE" 13.0: le due parole durano ~0,7 s).

### struttura (§4 'le soluzioni lasciano le prove per il twist', §6.3 'preparato da tre indizi (28.6, 42.1, 54.4-58.6)'), immedesimazione (§1, nota sul finale 'forse a salire era una persona'). Il presunto buco di continuità 'porta al 4° / passi dal piano 1' è in struttura §7, viveri §5.9, routine §2 e stile §3.6.

**Sbagliato:** La porta che si apre al 4° piano (28.6) e i passi sarebbero indizi di un essere umano nel palazzo. Il pallino che parte dal piano terra sarebbe un errore di continuità.

**Giusto:** Chi apre la porta al 4° piano è uno zombie. Fra 27.9 e 28.4, proprio su "A DOOR CREAKS", una testa verde con due occhi rossi (lo stesso disegno dell'orda a 6.1-6.4) sbuca dal bordo sinistro del corridoio. Le contact sheet a 0,5 s non lo catturano. Inoltre l'orda è disegnata dentro il piano terra dello spaccato (29.5-34.5), quindi i passi che partono dal piano 1 a 40.0 sono coerenti con una minaccia che sale dall'atrio: non è per forza un errore. Gli indizi che fuori c'è un essere umano sono tutti dopo i 54 s: la finestra di Maya accesa (54.4-58.6), la luce sotto la porta in un palazzo senza corrente (62.8-64.4) con due ombre di piedi, e i colpi regolari a 0,18 s l'uno dall'altro. La tesi dei "tre indizi" è quindi sbagliata per un terzo: il twist è più netto di come lo descrivono.

**Prova:** Ritagli di f0280-f0285 (x 0-120, y 700-1060): testa verde con due pupille rosse sul bordo sinistro. Lo stesso disegno degli occhi è visibile nell'orda (ritaglio di f0064). Fotogramma f0300: icone dell'orda nella fila sotto il piano 1.

### viveri (§5.10). La stessa scena è giudicata 'ambigua' anche in struttura §7, routine §2, stile §3.7 e immedesimazione §3.

**Sbagliato:** "la finestra accesa è una luce forte, non una candela, ed è a metà facciata: non si capisce se sia quella di Maya"

**Giusto:** È lo stesso palazzo dell'apertura: 4 colonne, 12 piani, ingresso al centro. La finestra accesa è nella 3ª fila dall'alto (10° piano su 12), 2ª colonna: la stessa casella accesa dal fotogramma 0.2 e contornata in giallo come "la sua" a 3.5. L'immagine dice quindi che è la finestra di Maya, che brilla subito dopo che lei l'ha coperta (53.5-54.0). O è una perdita di luce voluta, cioè il seme dei colpi, o è una svista. Non è una finestra qualsiasi e non è a metà facciata.

**Prova:** Ritagli di f0011 (1.0) e f0571 (57.0): in entrambi 12 file di finestre, accesa la 3ª dall'alto nella 2ª colonna, ingresso al centro in basso. f0036 (3.5): contorno giallo sulla stessa casella.

### stile (§1.10 'due o tre ombre scure'). transcript.txt dice 'tre ombre/colpi'; immedesimazione ('due ombre') ha ragione.

**Sbagliato:** Sotto la porta ci sarebbero tre ombre, o "due o tre".

**Giusto:** Le ombre sono due, cioè due piedi, già dal primo fotogramma della porta (62.9), quindi sul primo colpo. Sulla porta si vede anche uno spioncino (62.8-64.4), un oggetto che resta disponibile per il Part 2.

**Prova:** Ritaglio ingrandito della soglia in f0640 (63.9): la striscia di luce è interrotta da due tagli scuri. Le stesse due interruzioni sono visibili in f0630-f0645.

### stile (§1.5 'Tutte in alto (y ≈ 8-23% dell'altezza)')

**Sbagliato:** Tutte le card stanno in alto e lasciano il centro all'azione.

**Giusto:** Vale per la card del giorno, NO WATER, il countdown, RULE #1, SILENCE, 11:47 PM e VISIBLE FROM. Invece SUPPLIES — DAY 1 è centrata a metà schermo (circa dal 33% al 62% dell'altezza, 49.0-52.0), e la card del twist (64.6-66.5) e quella PART 2 (67.0) sono al centro. Per il nostro ledger la regola giusta è: la card dei numeri occupa il centro e la didascalia resta sotto.

**Prova:** half_d3, celle 49.0-52.0; half_d4, celle 65.0-67.5.

### viveri (§1 e §2.2 'sparisce a 21.5'), immedesimazione (§3 'sparisce a 21.5 s', 'il tubo blu... si svuota tra 17.0 e 34.5')

**Sbagliato:** Il countdown sparisce a 21.5; il tubo dello spaccato si svuota piano piano fra 17.0 e 34.5.

**Giusto:** Countdown e pillola dei litri spariscono a 21.1, su un taglio a un'inquadratura più stretta in cui la vasca è già piena per circa due terzi. È un'ellissi: il riempimento viene saltato sulla parola "BUT". Il tubo si svuota fra 16.5 e 17.5, poi resta fermo all'altezza del 4°-5° piano in tutte le apparizioni seguenti (26.1, 29.9, 34.4, 40.0, 43.5).

**Prova:** f0211 (21.0): 02:39 e 33 L, vasca bassa. f0212 (21.1): niente card, niente pillola, vasca alta, anelli dei tubi. Striscia di f0141, f0171, f0176, f0262, f0300, f0345, f0401 e f0436.

### viveri (§1, 'Il colore dice da che parte sta il numero')

**Sbagliato:** "I numeri in rosso misurano quanto è vicina la minaccia: 7:15 'DIES', SIXTH, 11:47 PM, i colpi."

**Giusto:** Nelle didascalie l'unico numero rosso è SIXTH (41.1). "AT 7:15" (11.9), "11:47 PM" (58.8) e "THREE" (63.4) sono bianchi. È rossa solo la pillola "11:47 PM" in alto (59.0-62.7). Il codice colore sui numeri vale per pillole e barre, non per le didascalie.

**Prova:** cap_0 a 11.9; cap_2 a 41.1; cap_3 a 58.8 e 63.4.

### routine (§6, regole del template: 'Non copiare il 6:42/11:47... abbiamo già i nostri marcatori (6:41...)')

**Sbagliato:** Il 6:42 è un marcatore del reference che noi non abbiamo e che basta non copiare.

**Giusto:** Il nostro Day 1 mostra già nell'HUD 6:42 AM (l'allerta, pov_stories.py:38) e 7:15 AM (il vicino, pov_stories.py:50). Sono gli stessi due orari del reference: la card DAY 1 a 6:42 AM (8.0) e il blackout "At 7:15" (11.9). Nessuno l'ha notato. Nel Day 2 conviene non far dire a voce né mettere in grande questi due orari, per non sembrare derivati.

**Prova:** Valori di clock in pov_stories.py: 6:41, 6:42, 6:43, 7:15, 7:16 AM... (17 valori). Reference: cap_0 a 8.0 ("6:42 AM") e a 11.9 ("AT 7:15").

## Cose che nessuna analisi aveva visto

### Il narratore legge davvero "Zombies don't... knock." e il colpo cade sull'ultima consonante. È la risposta alla domanda lasciata aperta da struttura.

**Prova:** Fra 64.55 e 65.10 c'è voce (periodicità 0,3-0,8, F0 90-115 Hz come nel resto del video): è "Zombies don't". Fra 65.12 e 65.24 tutto il mix, tappeto compreso, scende a zero digitale (da -51 a -71 dB). Fra 65.28 e 65.40 c'è un attacco sonoro ("knock"), a 65.44 una chiusura a -47 dB, e a 65.45-65.50 il boom. Il testo "KNOCK." compare nello stesso fotogramma (65.5).

**Perché conta:** È la ricetta precisa per il nostro momento della regola #4: ~0,1 s di silenzio assoluto (anche la musica), la parola, il boom sulla sua ultima consonante, il testo che appare di colpo nello stesso fotogramma. Stile segnala che il motore non ha un vero mute (Beat.music resta a ~0,55): questo dice quanto deve durare (0,1-0,15 s) e dove va il colpo.

### Il mix tace sulle parole SILENCE e FREEZES: l'audio fa quello che dice la didascalia.

**Prova:** Fra 36.45 e 37.85 tutto il mix scende a -28/-37 dB, contro una mediana di -17,7 dB fra 0.5 e 64 s. "Silence" è detta 8-10 dB più piano delle altre parole (banda voce al massimo -23,5 dB a 37.10, contro -12/-16). In questo tratto cadono 4 delle 12 finestre da 250 ms più silenziose prima del finale. Dopo "FREEZES" (61.0-61.15) il mix scende a -33/-37 dB (61.45-61.70): è il punto più silenzioso del video prima del finale. Stile scrive "Silenzi: due veri, entrambi prima del colpo finale", struttura scrive "voce secca e senza respiri".

**Perché conta:** Costa poco e funziona benissimo: un duck o mute agganciato alla parola (es. '@silence'). In DON'T ANSWER è il trucco perfetto. Su "quiet", "don't say it", "hold your breath" il mondo deve tacere davvero, e chi guarda senza audio lo vede comunque dalla didascalia.

### Uno zombie ai margini del quadro per 0,5 s (27.9-28.4): un easter egg che premia chi riguarda.

**Prova:** Ritagli di f0280-f0285: testa verde con due occhi rossi sul bordo sinistro del corridoio del 4° piano, mentre la didascalia dice "A DOOR CREAKS". Nessuna delle 5 analisi lo cita.

**Perché conta:** È un dettaglio che si nota solo mettendo in pausa e porta commenti del tipo "did anyone see the zombie at 0:28?". Per noi costa zero: una sagoma nella nebbia, o una seconda figura dietro il vicino, per 4-6 fotogrammi al bordo dell'inquadratura. Così l'episodio va rivisto e il commento si scrive da solo.

### Già nell'hook l'immagine smentisce "top floor", e la stessa finestra torna di notte: un fermalibri visivo.

**Prova:** Dal fotogramma 0.2 la finestra accesa è al 10° piano su 12 (3ª fila dall'alto). A 1.1-1.4 la didascalia dice "THE TOP FLOOR" mentre il push-in va proprio verso quella finestra, e a 3.5 la contorna in giallo. Tutte le analisi trovano l'incoerenza solo a 12-14 s, nello spaccato. La stessa casella brilla a 54.4-58.6.

**Perché conta:** L'incoerenza si vede nei primi 4 secondi, quindi il commento "she's not on the top floor" è quasi garantito: è un'esca, voluta o no. Il fermalibri (stessa finestra di giorno nell'hook e di notte prima dei colpi) è un dispositivo da copiare. Per esempio: la finestra di 41 Linden St in apertura e, alla fine, la stessa finestra vista da fuori, con dentro la luce dello schermo del telefono.

### La mappa annuncia dove arriverà la minaccia: l'etichetta "6TH FLOOR" c'è già prima del pallino.

**Prova:** f0401 (40.0): la scritta rossa "6TH FLOOR" è già disegnata, sbiadita, al 6° piano mentre il pallino rosso è al piano 1. Si accende a 41.0-42.0, e la parola "SIXTH" arriva solo a 41.1.

**Perché conta:** Lo spettatore vede la destinazione prima che la minaccia ci arrivi: è suspense ("so che arriva"), non sorpresa, dentro un'infografica. Se facciamo lo spaccato o la mappa di 41 Linden St, conviene segnare in anticipo il punto d'arrivo (la porta sul retro, la finestra della cucina) e lasciare che la voce ci arrivi dopo.

### Le scorte d'acqua sono già in scena 26 s prima: scaldabagno e cassetta si vedono dal bagno chiaro.

**Prova:** Lo scaldabagno (l'ovale bianco con il rettangolo sul muro sopra il WC) e la cassetta sono visibili per tutto il bagno di giorno, 17.7-23.2. Fra 43.8 e 48.3 è lo stesso set con la stessa inquadratura, ma al buio, e gli oggetti si illuminano di blu uno alla volta: +80 L a 44.0, +9 L a 45.5, +60 L a 47.0.

**Perché conta:** È un payoff senza spiegazione: chi riguarda scopre che lo scaldabagno c'era già, e lo spunto TIL nasce dall'immagine. Per il Day 2 vuol dire mostrare l'oggetto chiave (il campanello con lo speaker, il baby monitor) in un'inquadratura iniziale senza nominarlo, e accenderlo dopo.

### Nello spaccato l'acqua resta fino al 4°-5° piano: il grafico è fisicamente giusto e prepara un dilemma.

**Prova:** Il tubo si svuota fra 16.5 e 17.5 e poi tiene il livello all'altezza del 4°-5° piano a 26.1, 29.9, 34.4, 40.0 e 43.5. Immedesimazione lo descrive come un tubo che si svuota fino a 34.5.

**Perché conta:** Torna con "PUMPS PUSH WATER TO THE UPPER FLOORS" (17.0): ai piani bassi la pressione dell'acquedotto basta, ai piani alti servono le pompe. Questo dà credibilità ai numeri del video. Implica anche che più giù l'acqua c'è, cioè verso gli zombie: un dilemma pronto per il Day 2 e un'esca per i commenti ("just go to the 4th floor"). È un buon modello per noi: il dettaglio tecnico vero sta nel grafico, non nella voce.

### Il ruolo di Pixel nel montaggio: corpo che reagisce e sguardo che porta al taglio.

**Prova:** A 60.8 (f0609), sulla parola "FREEZES", la coda passa da arricciata in basso a dritta in verticale, insieme agli occhi che si accendono (le analisi citano solo gli occhi, a 61.0). Il gatto guarda a destra per tutta la scena, e il taglio di 62.8 va sulla porta, un attimo prima del primo colpo (62.85).

**Perché conta:** Il compagno non si limita a sentire la minaccia: orienta lo sguardo dello spettatore e giustifica il taglio verso la minaccia (raccordo di sguardo). Se usiamo il LED della cassa scollegata come "allarme" (proposta di routine), nell'inquadratura prima del taglio deve puntare o pulsare verso la direzione da cui arriva la voce.
