# DON'T ANSWER · Day 2, «Flash it twice»: le meccaniche di Maya applicate alla nebbia (Angolo A)

Il Day 2 riparte alle 12:00 AM esatte, dal voto dei commenti ("Most of you answered the voice in the fog... So did you."), e porta la nebbia ad attaccare un'altra regola: dopo la voce (Day 1) tocca alla luce. Le torri cellulari si spengono e il telefono, l'unico modo di parlare senza fare rumore, diventa una risorsa contata nell'"HOUSE LOG · DAY 2". Alle 11:57 PM la regola #4 regge, e proprio per questo arrivano tre messaggi da Mom: "flash ur light 2x so i know its u". Il dilemma sì/no ("So... do you flash it?") mette la regola #4 contro la regola #1, e nei commenti scatta la discussione da azzeccagarbugli: una luce non è una voce.

# DON'T ANSWER · Day 2, «Flash it twice»

Angolo A: le meccaniche del reference 3 (Maya, zombie, Day 1) applicate alla nostra serie, senza toccare le regole del brand.

## 0. Il concept in breve

Il Day 2 riprende dall'ultimo fotogramma del Day 1. L'endcard passa da "DAY 1 11:59 PM" a "DAY 2 12:00 AM" (`rules.py:490-535`), quindi apriamo alle 12:00 AM con il risultato del voto (BLUE KITE o NOT TONIGHT, il commento fissato di `docs/LAUNCH.md:163-168`).

La giornata segue lo scheletro "a routine" del reference: card del giorno, problema del mattino, regola che viene da un fatto vero, registro delle risorse, protocollo notturno, minuto preciso, twist su nero e domanda.

Il motore della serie: **ogni giorno la nebbia attacca una regola diversa.**
- Day 1: la #4, la voce.
- Day 2: la #1, la finestra e la luce.
- Day 3: la #2, una cassa con la batteria.
- Day 4 (31/10): la #3, la password detta ad alta voce. Chiude sulla #4.

Così l'"appello delle regole" ha un senso e le 4 regole restano 4.

## 1. Perché è adatto a noi (e cosa paga del Day 1)

| Cosa piantato nel Day 1 | Dove | Come lo paga il Day 2 |
|---|---|---|
| Il voto BLUE KITE / NOT TONIGHT, "Day 2 remembers what you typed." | `LAUNCH.md:163-168` | L'hook è il voto vero: "Most of you...". Lo scelto non è imposto dal narratore, l'ha scelto lo spettatore (lente immedesimazione §7.A) |
| La cassa staccata che si accende da sola nell'endcard | `dont_answer.py:634-641`, `pov_stories.py:171-172` | Diventa l'"allarme" fisso delle 11:57 PM, il nostro equivalente di Pixel |
| "If you can see out... it can see in." (regola #1) | `pov_stories.py:67` | Torna parola per parola come argomento CONTRO nel dilemma |
| Lo stile di scrittura della mamma: "if you hear me outside... that's not me." (con l'apostrofo) | `pov_stories.py:36` | I messaggi del Day 2 scrivono "dont", "ur", "2x": un indizio per chi mette in pausa |
| Il blackout delle 10:40 PM e "READ 11:51 PM" | `pov_stories.py:116-124` | Il telefono era carico fino alle 10:40 PM, quindi il Day 2 parte alto (84%). Le torri vanno a batteria per ore (fact-check), quindi la mattina c'è ancora una tacca |
| Ellie con il telefono della mamma, con la cosa dietro di lei | `pov_stories.py:154-166` | All'alba l'impermeabile giallo è vuoto sul tuo portico. Chi scrive da quel numero? |
| "IT REPEATS WHAT IT HEARS" | `pov_stories.py:93` | Il twist su nero: "It copies voices... not light." |

## 2. Meccaniche del reference e come le trasformiamo

| Reference (t) | Meccanica | Day 2 (t) | Trasformazione |
|---|---|---|---|
| 0.2-6.6 "Most people think the top floor is the SAFEST... it's a TRAP." | Credenza comune ribaltata, più una promessa | 0.1-6.6 | Il ribaltamento è il voto reale. Così evitiamo il loro difetto: dicono "top floor", ma la finestra di Maya è al 10° piano su 12 già dal fotogramma 0.2 |
| 7.1-11.5 card "DAY 1" e "6:42 AM" detto (la pillola si riempie a 8.5) | Etichetta di serie | 6.6-10.8 | "DAY 2 · 6:41 AM". Il 6:41 è nostro (il primo orologio del Day 1, `pov_stories.py:27`). Aggiungiamo l'appello delle 4 regole |
| 13.1-17.3 "no power means no WATER" (pompe) | Un fatto tecnico vero che fa partire tutto | 14.6-22.0 | Niente corrente, niente torri, niente messaggi: "Cell towers run on batteries too. Hours, not days." |
| 18.0-21.0 countdown 02:57 → 02:39, che sparisce a 21.1 senza chiudersi | Scadenza | 14.6-27.6 | Le tacche del segnale scendono e il conto **si chiude**: NO SERVICE a ~27 s |
| 21.1-29.0 "But old pipes are LOUD" | La soluzione crea il problema | 27.6-40.2 | Spegnere il telefono (la soluzione) vuol dire non ricevere niente fino a mezzanotte (il costo, pagato a 60.8). Il vicino salva il frigo con il generatore: luce e rumore |
| 40.0-43.5: l'etichetta "6TH FLOOR" è disegnata prima che arrivi il pallino (41.0) | La mappa annuncia la destinazione | 32.5-40.2 | Un bersaglio tratteggiato compare sulla casa d'angolo prima che gli anelli della nebbia la raggiungano |
| 48.5-52.0 card "SUPPLIES — DAY 1" (149 L a 49.5 su "forty nine", ≈37 a 51.5) | Registro con i contatori agganciati alla voce | 40.2-44.6 | "HOUSE LOG · DAY 2" (§5) |
| 52.0-58.6 finestre coperte e candela "over a kilometer" | Protocollo notturno con un fatto | 44.6-52.0 | "After dark: blankets up. Flashlight at the floor." e la candela "more than a mile" |
| 58.8-62.7 "11:47 PM" rosso, Pixel si blocca (60.8) | Minuto preciso con allarme | 52.0-56.8 | "11:57 PM" rosso, la cassa staccata si accende |
| 62.85/63.03/63.21 tre colpi con flash, prima di "THREE KNOCKS" (63.4) | Il suono arriva prima della parola | 60.8-62.4 | Tre ping del telefono e tre lampi dello schermo, prima di "Three texts" |
| 64.6 "ZOMBIES DON'T" → 65.5 "KNOCK." rosso sul colpo più forte, con 0,1 s di muto prima | Twist su nero | 68.4-71.6 | "It copies voices..." → "...not light." |
| 67.0-67.9 "PART 2 / WHO IS AT THE DOOR?" (0,9 s, domanda aperta) | Aggancio di serie | 74.8-79.4 | Domanda sì/no ed endcard di 2,0 s |

Cosa **non** importiamo:
- il "top floor" incoerente;
- il conto alla rovescia che non arriva a zero;
- la barra blu già piena all'85% quando il numero dice 0 L (48.5);
- "≈ 0" (49.5-50.4);
- EIGHTY blu sopra la vasca blu (43.8-47.4);
- WATER in rosso dentro "water heater" (47.5);
- la card finale da 0,9 s;
- gli orari 6:42 e 7:15. Sono i loro, e per coincidenza stanno anche nel nostro HUD del Day 1 (`pov_stories.py:38,50`): nel Day 2 non vanno né detti né mostrati in grande.

## 3. Beat per beat (~79 s, ~76 s con il narratore a speed ~1.28)

I tempi sono stime: ~2,85 parole/s di voce, "..." = 0,3 s come oggi (`rules.py:171`). Il critico ha misurato che le pause del reference sono di 0,30-0,40 s, quindi **non le allunghiamo**. Il respiro lo mettiamo *dopo* la parola che cambia lo stato, con `hold`.

[A] = vince BLUE KITE, [B] = vince NOT TONIGHT (§4).

| # | t (s) | Voce (EN) | Cosa si vede / HUD / card | Audio | Funzione |
|---|---|---|---|---|---|
| 1 | 0.1-4.3 | [A] "Most of you answered the voice in the fog... So did you." [B] "Most of you kept rule number four... So did you." | `front_walk`, stessa inquadratura che chiudeva il Day 1. Ellie nel fascio, la cosa dietro. HUD: DAY 2 · 12:00 AM · PHONE 84% · WORDS SAID OUT LOUD 0 | Bed della nebbia. "fog" e "voice" entro 3 s | HOOK: il voto come credenza ribaltata |
| 2 | 4.3-6.6 | [A] "You said the password. Out loud." [B] "She cried into the fog until 12:03." | [A] su "Out loud" la riga glitcha da 0 a **2** (rosso); Ellie corre verso la finestra e la cosa pure; la coperta cade, nero. [B] il fascio resta vuoto | [A] sub n.1 su "loud" ed eco lontana di "Blue kite." con la voce del narratore e il filtro `far`: la **tua** voce | Conseguenza del voto |
| 3 | 6.6-10.8 | "Day two. 6:41 AM. Four rules... one already broken." | Card `day` sulla finestra coperta del soggiorno, con lo spiraglio grigio dell'alba: pillola "DON'T ANSWER", "DAY 2" grande, la pillola dell'ora si riempie su "6:41". Subito dopo l'appello: 4 cartellini, #3 FAMILY PASSWORD con il timbro rosso COMPROMISED su "broken", **#4 censurata a barre** come nel Day 1. In scena, senza nominarli: la torcia sul davanzale e la cassa con il LED spento | Sigla di 1 s, sempre la stessa | Slot fisso: giorno, ora, regole |
| 4 | 10.8-14.6 | "Through the blanket... her raincoat is on your porch. Empty." | `window_view` dallo spiraglio: l'impermeabile giallo vuoto sul gradino (l'unico colore saturo) | [B] sub n.1 su "Empty" | Un loop che resta aperto: dov'è Ellie? |
| 5 | 14.6-22.0 | "One bar left. Cell towers run on batteries too. Hours, not days. No towers... no texts. Your only silent voice." | Lock screen con la barra di stato: 1 tacca, 79%. Poi la mappa `house_ext` all'alba: pin "YOU · 41 LINDEN ST" e la luce di una torre sull'orizzonte che lampeggia | | PROBLEMA del mattino con un fatto vero (la regola nasce dal problema) |
| 6 | 22.0-27.6 | "9:12 AM. One last alert: do not reply to the missing. Then... no service." | Banner "ALERT UPDATE #2 / DO NOT REPLY TO THE MISSING." (il tipo `banner` c'è già, `pov_stories.py:93`). Su "service" lo stato diventa NO SERVICE e la riga HUD SIGNAL passa a rosso | Sub n.2 sul banner | Il conto si chiude. È l'istruzione ufficiale che tornerà come prova CONTRO |
| 7 | 27.6-32.5 | "So you switch it off. Every percent... is a word you can still type." | Lo schermo si spegne nella mano. HUD: PHONE OFF · 73% | **Il mix tace su "off"**, come il reference su SILENCE (36.45-37.85) | COMPETENZA con un costo nascosto: batteria = voce |
| 8 | 32.5-40.2 | "Two doors down, a man starts a generator. A closed fridge keeps food safe... four hours. By sunset... it stops." | Mappa di pomeriggio: la casa d'angolo con le finestre accese e il generatore **all'aperto** che emette anelli. **Il bersaglio tratteggiato rosso compare prima** (~33 s), poi gli anelli della nebbia si spostano verso di lui. Su "stops" luci spente (riuso di `lamps_die_at`). HUD 2:30 PM → 6:14 PM | Ronzio del generatore che si ferma di colpo. Sub n.3 su "stops" | ERRORE IN TERZA PERSONA ("lo farei anch'io") e sollievo ambiguo |
| 9 | 40.2-44.6 | [A] "Seventy-three percent. Two words out loud... two too many." [B] "Seventy-three percent. Words out loud... zero." | Card `ledger` centrata, didascalia sotto (§5). I numeri si fermano sulla sillaba detta. Hold 0,9 s per chi mette in pausa | Nessun colpo: è il respiro | REGISTRO al 51-56% (il loro a 71%) |
| 10 | 44.6-52.0 | "After dark: blankets up. Flashlight at the floor. A single candle flame can be seen from more than a mile away." | Soggiorno di notte: sistemi la coperta, il fascio della torcia punta in basso, tre icone barrate (finestra accesa, schermo, bocca). Poi la mappa notturna: strada nera e un cerchio tratteggiato "1+ MILE" attorno alla tua finestra | | PROTOCOLLO NOTTURNO e un fatto vero (prepara il costo finale) |
| 11 | 52.0-56.8 | [A] "11:57 PM. The dead speaker lights up. Outside... your voice." [B] "...Outside... Mom's voice." | L'orologio dell'HUD diventa **rosso**. **Il LED si accende prima della parola**, e nell'inquadratura prima del taglio "guarda" verso la finestra (il raccordo di sguardo di Pixel, 60.8 → taglio a 62.8) | Il bed scende. [A] dalla nebbia "Blue kite." con la tua voce. [B] "Sweetie? Open up." (`af_heart`, `far`) | MINUTO PRECISO con allarme |
| 12 | 56.8-60.8 | "Rule number four..." / "You already know rule number four." | `cut="flash"`, l'allerta con il glitch, poi la card #4 censurata che si rivela: "DON'T ANSWER ANY VOICE / EVEN ONE YOU KNOW." Uguale al Day 1 | Sub n.4 (boom automatico della card) | PAYOFF DEL BRAND. Qui la #4 regge: non rispondi alla voce, nemmeno alla tua |
| 13 | 60.8-68.4 | "You turn it on. One bar." (3 ping) "Three texts from Mom." "Flash your light twice... so I know it's you." | Chat MOM, tre fumetti che arrivano insieme: "its mom" (9:14 AM), "cant find the house" (6:02 PM), "dont talk. flash ur light 2x so i know its u" (11:56 PM). HUD PHONE 72%, una tacca che lampeggia e muore | **Tre ping e tre lampi dello schermo a 60.9/61.1/61.3, prima della didascalia** | La minaccia cambia canale: la voce non ha funzionato, adesso il testo |
| 14 | 68.4-71.6 | "It copies voices..." / "...not light." | Nero. 0,5 s di quasi silenzio, poi la riga bianca "IT COPIES VOICES." Poi **0,12 s di muto totale**, e "NOT LIGHT." rossa e più grande compare nello stesso fotogramma del boom sull'ultima consonante (la ricetta misurata dal critico su 65.12-65.50) | Sub n.5 | TWIST su nero, che qui spinge verso il SÌ |
| 15 | 71.6-74.8 | "But if you can see out... it can see in." | Torna la mappa notturna: il cerchio "1+ MILE" si riaccende, gli anelli della nebbia si girano verso la tua casa. Facoltativo: un inserto di 0,4 s della mano di Ellie con il telefono della mamma (`ellie_phone`, già pronto) | | Argomento CONTRO: torna la frase della regola #1 del Day 1 |
| 16 | 74.8-77.4 | "So... do you flash it?" | `front_walk`, la stessa inquadratura dell'apertura 24 ore dopo (fermalibri). Coperta sollevata appena, torcia verso il pavimento, in fondo al vialetto **un bagliore piccolo di schermo** nella nebbia. Easter egg: un **secondo bagliore** per 5 fotogrammi sul bordo. Card "DO YOU FLASH IT?" / "TYPE IT. DON'T SAY IT." | | DILEMMA sì/no |
| 17 | 77.4-79.4 | (nessuna voce) | Endcard di **2,0 s**: DAY 2 11:59 PM che glitcha a 0,3 s in DAY 3 12:00 AM, "FOLLOW · STAY DARK" | Il LED della cassa si accende e **l'eco rallentata di "You already know rule number four."** è l'ultima cosa che si sente | Aggancio di serie e outro del brand |

Parole: circa 185, quindi ~2,6 parole/s sui ~72 s di voce, contro le 2,42 del Day 1. Numeri pronunciati: circa 15 (12:03, 6:41, four rules, one bar, hours, 9:12, seventy-three, two/zero, four hours, a mile, 11:57, four, one bar, three texts, twice). Il reference ne dice circa 14-16.

**Colpi di sub: 5**, sempre su un cambio di stato: voto o impermeabile, allerta, generatore, regola #4, "light". **Lampi: solo i tre ping**, come il reference che li tiene per i colpi (62.9-63.2), più il flash di brand a #12.

**Tagli se serve stare sotto i 75 s:**
- #8 "A closed fridge keeps food safe... four hours." (−2,4 s, ma si perde un fatto TIL);
- #10 accorciato a "After dark: blankets up." (−1,2 s);
- speed del narratore 1.28.

## 4. Le varianti del voto (da renderizzare tutte e due mercoledì)

Cambiano solo 4 punti: il testo di #1 e #2, il valore di WORDS SAID OUT LOUD (HUD e ledger) e la voce a #11. Il resto è identico.

- **[A] BLUE KITE.** Hai detto "Blue kite." ad alta voce, quindi la nebbia ha la password **con la tua voce**. Alle 11:57 la usa all'esterno. La #4, "EVEN ONE YOU KNOW", copre anche la tua voce. Il messaggio "so i know its u" diventa coerente: se è la mamma vera, ha sentito "te" fuori e sa che non eri tu. Il prezzo del voto si vede: WORDS = 2 in rosso, e nel video **non c'è verde**.
- **[B] NOT TONIGHT.** Il brand viene nominato nei primi 2 s. WORDS = 0 in **verde**, l'unico verde dell'episodio, come premio per chi ha rispettato la regola (il reference usa il verde una sola volta, 50.5-52.0). Alle 11:57 fuori c'è la voce della mamma mentre lei ti scrive: è il paradosso dell'hook del Day 1 (`pov_stories.py:26`) ribaltato.
- **[C] Pareggio o pochi voti.** "Half of you answered the voice in the fog... half didn't." + il testo di [B] con WORDS = 0. "Most of you" deve essere vero. Su un account nuovo i numeri possono essere piccoli: si decide sul conteggio reale.

## 5. Il registro: "HOUSE LOG · DAY 2" (40.2-44.6)

La risorsa che conta per noi non è l'acqua ma il **telefono**. La regola è "Text it. Never say it." (`pov_stories.py:87`), quindi la batteria è la tua voce silenziosa.

Lo stile è il nostro: card scura in monospace come l'HUD, barre sottili colorate. Niente carta crema su legno. La card sta **al centro** (come la loro a 49.0-52.0, correzione del critico) con la didascalia sotto.

| Riga | Valore | Colore | Barra | Detto? | Ruolo |
|---|---|---|---|---|---|
| PHONE | 79 → **73%** | bianco (rosso sotto 20) | su 100, si muove **insieme** al numero | sì, si ferma su "three" | La risorsa principale |
| FLASHLIGHT | ≈ 6 H | ambra | fissa | **no** | Seme per Day 3/4 (la luce finisce). Il ≈ indica una stima in-world |
| TAP WATER | ON | blu | nessuna, solo lo stato | **no** | Seme per Day 3: "TAP WATER: OFF" → lo scaldabagno |
| WORDS SAID OUT LOUD | **2** [A] rosso / **0** [B] verde | — | nessuna | sì, si ferma su "two" o "zero" | La risorsa al contrario: è la riga che non deve muoversi. Nel finale del 31/10 è la domanda |

**Il percorso dei numeri** (valori in-world, scelti per essere plausibili e coerenti):
- 84% alle 12:00 AM: il telefono era in carica fino al blackout delle 10:40 PM;
- 79% alle 6:41 AM: notte con segnale debole;
- 73% alle 9:13 AM;
- spento tutto il giorno;
- 72% alle 11:58 PM.

Non diciamo mai a voce un tasso di consumo come se fosse un fatto. Partire basso (il 41% del reference) senza spiegarlo sarebbe un errore di continuità.

**Regole di animazione**, prese dalla card del reference corretta dove sbagliava:
- ingresso con una scala breve;
- il numero sale o scende in 0,6-1,0 s rallentando, e si ferma sulla sillaba accentata (`word()`, `rules.py:270`);
- la barra si muove con il numero;
- ≈ solo sulle stime, mai "≈ 0";
- almeno 4 s a schermo;
- 2 righe dette e 2 lasciate a chi mette in pausa, come FOOD e PHONE del reference (49.0-52.0).

**Come cresce nella serie.** La card del Day N si apre con i valori del Day N−1 e li fa cambiare davanti allo spettatore.
- **Day 3 (lun 26/10):** TAP WATER passa a OFF, ed entra lo scaldabagno con il fatto verificato "forty gallons of drinkable water", con la procedura sicura del fact-check (corrente spenta, valvola dell'acqua fredda chiusa).
- **Day 4 (sab 31/10):** PHONE verso lo 0% proprio quando serve. WORDS SAID OUT LOUD è la domanda finale.

## 6. Gli slot fissi (il template DAY N che nasce qui)

Fissi nella forma, con almeno un valore nuovo a ogni giorno:
1. Hook = esito del voto ("Most of you...");
2. card DAY N con "6:41 AM" detto;
3. appello delle 4 regole (la #4 sempre censurata, una regola cambia stato);
4. problema del mattino con un fatto vero e un contatore che **si chiude**;
5. ALERT UPDATE #N su una riga;
6. errore di un vicino sulla mappa `house_ext`, con la destinazione segnata prima;
7. HOUSE LOG · DAY N;
8. "After dark:" con le icone barrate;
9. 11:57 PM in rosso e il LED della cassa;
10. regola #4 identica al Day 1;
11. twist su nero di 2 righe;
12. "So... do you ___?" + "TYPE IT. DON'T SAY IT.";
13. endcard di 2 s con l'eco della frase del brand.

Gli slot 2, 3, 5, 7, 8, 9, 10, 12 e 13 fanno circa il 45-50% del video, come nel reference (circa 31 s su 68).

**Il compagno.** Per giovedì niente animale: costa sprite e pose, e nel Day 1 non c'era. Il ruolo di Pixel lo fa la cassa staccata. Il LED segnala solo **che qualcosa è vicino, mai se è vero o falso**, altrimenti il dilemma muore. Se si vuole un'ancora emotiva vera, nel Day 3 può entrare il cane di Ellie, mostrato in silenzio e nominato solo nella crisi (come Pixel, che vediamo dalle 7.2 ma è nominato solo a 60.5).

## 7. I momenti "lo faresti?"

I commenti indicati sono **previsioni**, non dati.

| t (s) | Scelta | Tecnica | Commento previsto |
|---|---|---|---|
| 0.1-6.6 | Il voto: l'hai fatto davvero | Errore del pubblico, non imposto | "I TYPED it, I didn't SAY it", "told you" |
| 27.6-32.5 | Spegneresti l'unico filo con tua madre? | Competenza con un costo | "airplane mode is enough", "I'd keep it on for mom" |
| 32.5-40.2 | Accenderesti il generatore per salvare il frigo? | Errore in terza persona (come il vicino delle 7:15 nel Day 1) | "TIL four hours", "rip corner guy" |
| 44.6-52.0 | Accenderesti una candela? | Fatto vero con un numero prudente | "TIL a mile", "phone screens too" |
| 60.8-68.4 | Leggi "dont", "ur", "2x" | Indizio da pausa (la mamma vera scrive "that's") | "mom doesn't text like that" |
| 74.8-77.4 | Lampeggi due volte? | Dilemma tra due regole | "rule 4 is only voices" contro "RULE ONE" |

Perché il dilemma è bilanciato:
- **A favore** (è lei): sa che non puoi parlare ("dont talk"); chiede l'unico segnale che la nebbia non sa copiare (#14); in [A] ha sentito "te" fuori; in [B] scrive mentre "lei" chiama da fuori, come nel Day 1, quando era vero il messaggio.
- **Contro:**
  - l'allerta delle 9:12 ("do not reply to the missing");
  - la regola #1 ("it can see in"): con la coperta non sa quale finestra è la tua, e il lampo glielo dice;
  - una luce si vede da più di un miglio;
  - lo stile di scrittura;
  - il telefono della mamma era in mano a Ellie;
  - l'ora dei messaggi: il primo arriva alle 9:14, due minuti dopo l'allerta, e l'ultimo alle 11:56, un minuto prima.

## 8. I fatti reali (solo quelli sostenuti dal fact-check)

| Frase | Base | Esito del fact-check |
|---|---|---|
| "Cell towers run on batteries too. Hours, not days." | Batterie da qualche ora (fino a ~8 h nei siti grandi), solo alcuni generatori da 24-72 h; in California 72 h solo nelle zone Tier 2/3 | È la frase proposta dal fact-check |
| "A closed fridge keeps food safe... four hours." | USDA / FoodSafety.gov | Supportato (nota su FOOD) |
| "A single candle flame can be seen from more than a mile away." | Krisciunas e Carona 2015, ~2,6 km / 1,6 mi in condizioni ideali | Vero, ed è proprio la frase proposta |
| "Flashlight at the floor." | FEMA / NFPA: torce, non candele | Supportato |
| La tacca che torna per un secondo | Alcuni siti hanno generatori da 24-72 h | Supportato |

Due cose sono **da verificare**, perché non stanno nel fact-check (non sono numeri):
- la consegna "store-and-forward" dei messaggi accodati che arrivano tutti insieme;
- che un telefono spento conservi la carica.

**Da non dire:**
- "30 miles" per la candela (mito falso);
- "lo schermo è più luminoso di una candela" (non verificato);
- "apri il frigo, è la cosa più luminosa della strada" (proposto dalla lente immedesimazione): **sbagliato**, senza corrente la luce del frigo non si accende;
- la raccomandazione FBI sulla password di famiglia (PSA I-120324-PSA) prima di aver letto l'originale su ic3.gov;
- 6:42 e 7:15.

## 9. Cliffhanger, dilemma e testi

**Commento fissato:**
```
Rule #4 is about voices. This is a light.
Answer her with light: FLASH TWICE
Keep every window dark: STAY DARK
Day 3 remembers what you typed.
```

**Risposte in personaggio:**
- A FLASH TWICE: "Two flashes. A mile is a long way to be seen from."
- A STAY DARK: "You already know rule number four. Rule one, too."
- A "light isn't a voice": "Read the 9:12 alert again."
- A chi nota "ur/2x": "Keep noticing."

**Caption TikTok:**
```
DON'T ANSWER · Day 2
The towers are dead. Mom texts anyway: dont talk. flash ur light 2x.
So... do you flash it? Type it. Don't say it.
```

**Titolo Shorts:** "Mom texts: 'flash your light twice.' Do you? (DON'T ANSWER · Day 2)"

I fatti verificati (torri, frigo, candela, oscuramenti della Seconda guerra mondiale per "COVER EVERY WINDOW") vanno in una risposta fissata con le fonti: sono quello che fa salvare il video.

## 10. Come stanno dentro la regola #4 e l'outro

- La beat #4 (56.8-60.8) è identica al Day 1 (`pov_stories.py:137-144`) ed è il perno: la #4 **regge**, quindi la minaccia è costretta a passare a un canale che la #4 non copre. Il dilemma nasce dalla #4, non la sostituisce.
- `LAUNCH.md` chiede che l'outro sia detto sempre parola per parola. Nel Day 1 cadeva 26 s prima della fine. Qui la frase è detta a 58.5 s (al 74% del video) e torna come **ultima cosa udibile** nell'endcard, rallentata e uscita dalla cassa staccata. È lo stesso meccanismo `echo_last` del Day 1, ma su questa frase (`echo_word`).

## 11. Note oneste

- Lo schema del finale (qualcuno che conosci ti chiede di rompere una regola a mezzanotte) è parente stretto del Day 1. Cambiare regola e canale (testo e luce invece della voce) basta per un episodio, ma il Day 3 deve cambiare forma.
- Il lavoro sul motore (§engine_needs) è circa 1-1,5 giorni. Se non ci sta, il fallback per giovedì è: niente card `day`, `roll` e `ledger`, e le stesse informazioni nelle righe dell'HUD, che sanno già cambiare testo su una parola con il glitch (`rules.py:308-322`).
- Non posso ascoltare l'audio: la "tua voce" nella nebbia [A], il muto da 0,12 s e la speed 1.28 vanno giudicati in cuffia.
- Il controllo delle 48 ore (`LAUNCH.md:206`) può anticipare il Day 2 a mercoledì sera: in quel caso il conteggio dei voti va chiuso mercoledì pomeriggio.

## ENGINE
- Parametro di variante `vote` ("kite" | "dark" | "split") nella nuova storia `dont_answer_day2()` in shorts/pov_stories.py: cambia i testi dei beat 1-2, il valore di WORDS SAID OUT LOUD in HUD e ledger e la voce lontana al beat 11. Si renderizzano A e B mercoledì e si pubblica quella che vince
- Nuova card `day` in Renderer._card (shorts/rules.py:334): pillola rossa "DON'T ANSWER", "DAY 2" in Bebas grande, pillola dell'orario che si riempie su "@6:41"
- Nuova card `roll`: 4 cartellini RULE #1-#4 con uno stato per regola (ok, oppure timbro rosso COMPROMISED su una "@parola"); la #4 resta sempre censurata a barre come in _rule (rules.py:426-432)
- Nuova card `ledger` ("HOUSE LOG · DAY 2"): righe con etichetta, da, a, unità, massimo, colore, '@parola' e ≈ facoltativo. Numero e barra si muovono insieme con ease-out e si fermano sulla sillaba detta (riuso di kinetic.rolling_number). Card centrata, didascalia sotto, monospace come l'HUD, minimo 4 s
- Nuova card `black_reveal`: riga 1 bianca sulla voce; riga 2 rossa più grande che compare nello stesso fotogramma del boom, agganciata a '@parola'
- Beat.mute=(at | '@parola', durata) in rules_audio.build: azzera musica e tappeto con fade di 30 ms (oggi il drone resta a ~0,55). Serve per 0,12 s prima di "light", 0,5 s prima della card su nero e per il duck su "off"
- Barra di stato del telefono in pov_gfx.lock_screen e chat_screen (pov_gfx.py:353, 417): tacche del segnale, "No Service", una tacca che lampeggia, batteria in %. Timestamp sotto i fumetti e tre fumetti in arrivo dalla mamma insieme
- house_ext (dont_answer.py:205): casa d'angolo con finestre accese e generatore all'aperto che emette sound_rings; bersaglio tratteggiato che compare prima; anelli della nebbia che si spostano verso un punto (oggi ring_at è fisso); torre cellulare sull'orizzonte con la luce che si spegne; cerchio tratteggiato "1+ MILE" di notte
- window_view con il parametro "porch": impermeabile giallo vuoto sul gradino, visto dallo spiraglio della coperta all'alba
- HUD: colore dell'orologio impostabile per beat (rosso alle 11:57 PM; oggi è fisso WHITE in rules.py:301). Le righe PHONE, SIGNAL e WORDS usano lo swap '@parola' con glitch che esiste già (rules.py:308-322)
- Endcard: hold 2,0 s, glitch a 0,3 s, etichetta configurabile (oggi è fissa a "FOLLOW FOR {next_day}", rules.py:528), eco rallentata di "You already know rule number four." dalla cassa (echo_word in rules_audio) come ultimo suono
- front_walk: parametro per un bagliore di schermo in fondo al vialetto e un secondo bagliore per 5 fotogrammi (easter egg); stessa inquadratura all'apertura e alla domanda finale
- Facoltativi: colori semantici delle didascalie per beat (Beat.hot) al posto del karaoke lime (rules.py:456-481); icone barrate no_icon (finestra accesa, schermo, bocca); speed del narratore da 1.22 a ~1.28; target di loudness -14 LUFS

## RISKS
- Il finale somiglia al Day 1 (qualcuno che conosci ti chiede a mezzanotte di rompere una regola). Spostare l'attacco sulla regola #1 e sul canale testo più luce lo distingue, ma il Day 3 deve cambiare forma
- La regola #4 non decide il dilemma (decide la #1): alcuni possono leggerlo come una #4 indebolita. Il beat #4 resta identico e fa da perno, ma è un rischio per il brand
- "Most of you" deve essere vero: su un account nuovo pochi voti o un pareggio richiedono la variante C, e il conteggio va chiuso prima del render finale (mercoledì se il Day 2 viene anticipato)
- Tempi stretti: servono ~1-1,5 giorni di motore prima di giovedì alle 22:30. Il fallback è usare le righe dell'HUD al posto delle card day, roll e ledger
- Somiglianza visibile con il reference (card del giorno, registro, minuto preciso, suono prima della parola, twist su nero): rischio che sembri una copia. Lo si riduce con lo stile visivo nostro (HUD monospace scuro, niente carta su legno), con i nostri orari (6:41, 11:57) e senza mai 6:42 o 7:15 detti o mostrati in grande
- Fatti: "Hours, not days" vale per molte torri ma non per tutte (alcune hanno generatori da 24-72 h). La consegna "store-and-forward" e il telefono spento che tiene la carica non sono nel fact-check e vanno verificati. La candela "more than a mile" è al limite alto se misurata a livello del suolo
- Non posso ascoltare l'audio: la tua voce nella nebbia (narratore più filtro far), il muto da 0,12 s e la speed 1.28 vanno controllati in cuffia
- Durata stimata ~79 s, sopra i 75 di target: c'è una lista di tagli pronta (frase del frigo, protocollo notturno corto, speed del narratore)
- Il generatore va disegnato all'aperto, mai in garage (monossido di carbonio). Niente consigli che possano fare danni nella vita reale
- Le "terze vie" nei commenti (rispondere con un SMS, illuminare verso il pavimento) possono confondere il conteggio sì/no: il commento fissato deve lasciare solo due risposte, FLASH TWICE e STAY DARK