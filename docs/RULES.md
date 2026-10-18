# Rules: storie POV di sopravvivenza (stile "14 Floors Up")

Il format `rules` rifà in codice la grammatica dei video tipo "14 FLOORS UP": una storia in seconda persona ("Imagine you..."), una minaccia che non viene mai nominata, quattro regole numerate, l'orologio che avanza durante il giorno, un personaggio che chiede qualcosa e una domanda finale al pubblico, seguita dal cartello "DAY 2". Tutto è disegnato in 2D con lo stickman. La voce narrante si genera in locale.

```bash
python make.py --format rules --episode 1 --out out/rules_001.mp4
python make.py --format rules --episode 1 --stills 0.5,10,40 --out out/prev    # solo frame PNG
```

## 1. Anatomia del video di riferimento (91 s)

Trascrizione ricostruita dalle didascalie, circa 230 parole (2,6 parole al secondo con le pause):

> Imagine you wake up on the fourteenth floor... and the whole city is screaming. Your phone won't stop buzzing. *[allerta rossa: SHELTER IN PLACE. DO NOT OPEN YOUR DOOR]* ...for anyone. You look outside. Fourteen floors down, people are running. And some of them... are chasing the others. Rule number one: do not go outside. Everyone who runs into the street... becomes part of the crowd. Rule number two: fill your bathtub. Right now. In a few hours, the water stops. Rule number three: block the door. Couch. Bookshelf. Anything heavy. By sunset, the screaming has stopped. Somehow... that's worse. Then the power dies. The whole city goes dark. And in the dark... someone knocks on your door. *[MR. HARLOW · THROUGH THE DOOR]* Hello? It's Mister Harlow, from across the hall. Please... let me in. They're in the stairwell. You check the peephole. It's him. But he's holding his arm... and his sleeve is soaked red. Rule number four... You already know rule number four. *[Harlow]* Please. I'm not bitten. I swear. Behind him, at the end of the hallway... something starts crawling toward your door. So... do you open it?

| Tempo | Cosa succede | Perché funziona |
|---|---|---|
| 0-4 s | "Imagine you wake up on the fourteenth floor..." sopra lo stickman che si sveglia, poi il grattacielo con l'etichetta "YOU · FLOOR 14" | La seconda persona ti mette dentro subito. Un dettaglio preciso (il 14° piano) e uno sensoriale (la città che urla) |
| 4-5 s | Titolo della serie "14 FLOORS UP" sopra la città in fiamme | È il marchio: ogni episodio lo ripete |
| 6-13 s | Lock screen con le notifiche (City News, Jake, Mom con 6 chiamate perse), poi l'allerta rossa a tutto schermo | Un'interfaccia che tutti conoscono. L'istruzione dell'allerta diventerà la regola #4 |
| 14-30 s | Finestra, poi la strada vista dall'alto: gente che corre, "alcuni inseguono gli altri" | La minaccia si vede ma non viene mai nominata (mai "zombie") |
| 22-42 s | Regole #1, #2 e #3: card rossa "RULE #n" con il testo condensato enorme e una frase di conseguenza | Struttura e progresso. Regole pratiche ("riempi la vasca, tra qualche ora l'acqua si ferma") fanno pensare "io lo farei" e quindi commentare |
| 42-52 s | L'orologio salta: 11:27, 5:18 PM, 7:49 PM. "Le urla si sono fermate. In qualche modo... è peggio." Poi salta la corrente | Escalation per sottrazione: tolgono suono, luce, sicurezza |
| 53-64 s | Buio, torcia, qualcuno bussa. Parla il vicino (voce diversa, cartellino "MR. HARLOW · THROUGH THE DOOR", parola evidenziata in arancione) | Un personaggio con un nome chiede una cosa sola |
| 65-71 s | Spioncino: è lui, ma la manica è rossa di sangue | Lo spettatore vede la prova che contraddice quello che dice |
| 72-76 s | "Rule number four... You already know rule number four." La card censurata si rivela: DON'T OPEN THE DOOR FOR ANYONE | Il callback all'allerta premia chi era attento |
| 77-85 s | "I'm not bitten. I swear." In fondo al corridoio qualcosa striscia verso la porta | Una seconda minaccia costringe a decidere adesso |
| 86-91 s | "So... do you open it?", poi "14 FLOORS UP / DAY 1 11:59 PM", che si guasta in "DAY 2 12:00 AM" rosso, e "FOLLOW FOR DAY 2" | Domanda sì/no: la gente risponde nei commenti. Il seguito è promesso |

Stile grafico:
- **Illustrazione piatta 2D** con luce "cinematografica": lampade calde, bagliore arancione degli incendi, notte blu, neri profondi, grana e vignetta.
- **Stickman color crema** con contorno scuro e testa tonda senza faccia (sei tu). Gli altri personaggi hanno uno o due tratti: occhiali e baffi, una manica rossa.
- **HUD in alto a sinistra**: pallino rosso con "DAY 1", ora grande in monospace, luogo ("FLOOR 14").
- **Didascalie** di 1-3 parole in maiuscolo, bianche col contorno nero. La parola detta in quel momento è lime (arancione quando parla l'altro personaggio).
- **Card delle regole**: cartellino rosso "RULE #n" e testo condensato enorme (tipo Bebas Neue) con la sottolineatura rossa. Poi si rimpicciolisce e resta in alto.
- **Camera** sempre in movimento: push-in e pan lenti, un taglio a ogni frase.
- **Audio**: narratore maschile calmo e profondo, tappeto drone scuro con sub, effetti (vibrazione, tono d'allerta, colpi alla porta, blackout).

## 2. La formula

1. **"Imagine you..."** e un dettaglio concreto nella prima frase.
2. **Un'istruzione ufficiale** (allerta, annuncio, cartello) mostrata presto: tornerà come regola #4.
3. **La minaccia si vede ma non si nomina.**
4. **Quattro regole**, ognuna con una frase di conseguenza breve e brutale. Le prime tre sono pratiche e discutibili, la quarta è il callback.
5. **L'orologio salta** durante la giornata. L'escalation toglie qualcosa: suoni, luce, segnale, persone.
6. **Un personaggio con un nome** chiede una cosa (aprire, rispondere, uscire, mentire).
7. **La prova** che lo spettatore vede e il personaggio nega.
8. **Una seconda minaccia** che si avvicina: bisogna decidere ora.
9. **"So... do you ___?"** e il cartello "DAY 2".

## 3. Come funziona il motore

- `shorts/voice.py`: voce locale **Kokoro-82M** (Apache-2.0). I pesi si scaricano una volta dal registry npm (`kokoro-q8-shards` e `kokoro-local-runtime`) perché HuggingFace e GitHub non sono raggiungibili dal container. Gli hash sono verificati. Al modello aggiungiamo l'uscita delle durate per fonema, così ogni parola ha il suo tempo esatto e le didascalie karaoke sono sincronizzate senza un riconoscitore vocale. Le battute vanno in cache in `~/.cache/claude-code-shorts/lines`. Si può usare una voce sola o una miscela: il narratore è `am_michael*0.6+am_onyx*0.4`, che è più profondo di `am_michael` da solo.
- `shorts/rules.py`: la timeline la decide la voce. Ogni `Beat` è una battuta, divisa in pezzi a ogni "..." per avere pause vere. Il file contiene anche le didascalie, l'HUD con l'orologio che scorre, le card (regola, titolo, domanda), il cartellino del personaggio, il cartello finale con il glitch e le inquadrature: i beat consecutivi senza scena o camera nuova restano nella stessa inquadratura, così la camera continua senza salti.
- `shorts/stick.py`: lo stickman con le pose (in piedi, seduto a terra, mani sulle ginocchia, spingere, carponi, telefono in mano...), la camminata e il respiro.
- `shorts/pov_gfx.py`: la scenografia. Stanze, finestre con vista, porte con spioncino e luce sotto, librerie, divani, lampade, letti, skyline con luci e incendi, nebbia, pioggia, polvere, buio con le zone illuminate, fascio di torcia, telefono (lock screen, allerta, chat) e spioncino.
- `shorts/rules_audio.py`: tappeto drone in re minore con sub e battito che segue la tensione di ogni beat, ducking sotto la voce, effetti procedurali (il vero tono delle allerte d'emergenza a 853+960 Hz, vibrazione, colpi alla porta, sirena, blackout, glitch, din-don da altoparlante...) e un limiter che porta il volume medio a quello del riferimento (circa -17 dB RMS).
- Post-produzione: `POST_SOFT` in `formats.py`, con il bloom solo sulle luci vere, la vignetta e la grana.
