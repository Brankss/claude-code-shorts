# Pubblicazione automatica su YouTube

Con questa configurazione la Routine giornaliera genera il video, lo carica sul canale e lo programma alle 13:00 di New York (19:00 in Italia). Titolo, descrizione, hashtag, tag e impostazioni sono già pronti.

Il limite da conoscere prima di partire: finché il tuo progetto Google Cloud non passa l'**audit delle YouTube API**, YouTube blocca come privato ogni video caricato via API, e quel video non si può più rendere pubblico. Per questo la pubblicazione automatica si accende solo dopo l'approvazione (passo 7). Fino ad allora la Routine ti manda il video sul telefono con la scheda di pubblicazione pronta da copiare.

## 1. Progetto Google Cloud

**Progetto nuovo**: vai su [console.cloud.google.com](https://console.cloud.google.com), crea un progetto (per esempio `claude-code-shorts`), poi in *API e servizi → Libreria* abilita **YouTube Data API v3**.

**Progetto che hai già**: va benissimo, basta che abbia la YouTube Data API v3 abilitata. Se c'è anche la YouTube Analytics API, ancora meglio: serve per i report sulle statistiche. Due controlli in più:
- **È un progetto vecchio o già approvato?** I progetti creati prima del 28 luglio 2020, e quelli che hanno già passato l'audit, non hanno il blocco sui video privati. In quel caso il passo 7 forse non serve: lo verifichi con la prova del passo 6.
- **Quota condivisa**: la quota giornaliera (10.000 unità di default) è in comune con l'altra app del progetto. Controlla in *API e servizi → YouTube Data API v3 → Quote* che ne avanzi.

Il progetto può essere di qualsiasi tuo account Google. Conta solo con quale account fai l'accesso al passo 4.

## 2. Schermata di consenso OAuth

1. *API e servizi → Schermata di consenso OAuth* (o *Google Auth Platform*): tipo di utente **Esterno**. Metti nome app, la tua email come supporto e contatto, poi salva. In un progetto esistente è già configurata: controlla solo il punto 2.
2. Lo **stato di pubblicazione** deve essere **In produzione**. Se è *Test*, premi **Pubblica app**.
   - Va fatto perché in stato *Test* il token scade dopo 7 giorni e l'automazione si fermerebbe.
   - Per uso personale non serve la verifica dell'app: durante l'accesso vedrai l'avviso "app non verificata", premi *Avanzate → Vai all'app*.
3. In *Accesso ai dati* (o *Ambiti*) aggiungi gli ambiti che chiede `youtube_auth.py`:
   - `.../auth/youtube.upload`
   - `.../auth/youtube.readonly`
   - `.../auth/yt-analytics.readonly`

## 3. Client OAuth

*API e servizi → Credenziali → Crea credenziali → ID client OAuth*, tipo **App desktop**. Ti dà un **Client ID** e un **Client secret**.

In un progetto esistente puoi anche creare solo questo client nuovo, senza toccare il resto: ci vuole un minuto e non disturba l'altra app.

Se invece vuoi riusare un client che hai già, guarda il tipo:
- **App desktop**: va bene così com'è.
- **Applicazione web**: aggiungi `http://127.0.0.1:8765` tra gli *URI di reindirizzamento autorizzati* e al passo 4 aggiungi `--port 8765`.

## 4. Refresh token (una volta, sul tuo computer)

Con Python installato, dalla cartella del repo:

```bash
python youtube_auth.py --client-id IL_TUO_CLIENT_ID --client-secret IL_TUO_CLIENT_SECRET
# con un client "Applicazione web":
python youtube_auth.py --client-id ... --client-secret ... --port 8765
```

Si apre il browser.
1. Accedi con l'account Google che **gestisce il canale**.
2. Quando Google ti chiede quale account o canale usare, **scegli il canale Softloop** (il brand account), non il tuo profilo personale. È questo il passaggio che collega il token al canale giusto.
3. Accetta i permessi: caricare video e leggere le statistiche.

Nel terminale compare il **refresh token**.

## 5. Variabili d'ambiente

Nell'app Claude apri le impostazioni dell'ambiente cloud (menu dell'ambiente nella barra del titolo della sessione, poi *Edit*) e aggiungi queste variabili d'ambiente:

| Variabile | Valore |
|---|---|
| `YT_CLIENT_ID` | il Client ID del passo 3 |
| `YT_CLIENT_SECRET` | il Client secret del passo 3 |
| `YT_REFRESH_TOKEN` | il token del passo 4 |

Non incollarli mai in chat. Le sessioni nuove, compresa la Routine, li leggono da lì.

Opzionali:
- `YT_PUBLISH_TIME`: orario di pubblicazione (default `13:00`)
- `YT_PUBLISH_TZ`: fuso dell'orario (default `America/New_York`)

## 6. Prova

```bash
python publish.py out/daily/<file>.mp4 --dry-run   # cosa verrebbe inviato, senza caricare niente
python publish.py out/daily/<file>.mp4 --test      # carica davvero, ma privato e non programmato
```

Il `--test` ti dice due cose:
- **Il collegamento funziona**: il video compare nel canale giusto, con titolo `[TEST] ...`.
- **Se il progetto è sbloccato**: apri il video in YouTube Studio. Se la visibilità risulta *Bloccato*, serve l'audit (passo 7). Se puoi cambiarla in *Pubblico*, il progetto è già a posto e puoi saltare dritto all'accensione. Poi cancella il video di prova.

Puoi anche chiedere a Claude, in una sessione nuova (le variabili si leggono solo dalle sessioni aperte dopo averle salvate), di lanciare la prova per te.

## 7. Audit, poi accensione

Se la prova del passo 6 ha dato *Bloccato*:

1. Compila il [modulo di audit delle YouTube API](https://support.google.com/youtube/contact/yt_api_form). Descrivi il progetto per quello che è: uno strumento personale che carica e programma sul tuo canale uno Short al giorno generato dal tuo codice. Il processo è spiegato nella [guida di Google agli audit](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits).
2. Quando arriva l'approvazione, oppure subito se la prova non era bloccata, aggiungi la variabile d'ambiente **`YT_AUTO_PUBLISH=1`**.

Da lì la Routine carica e programma ogni video da sola, poi ti manda il link e l'orario sul telefono. Se un video non ti convince, hai tempo fino all'orario di uscita per cancellarlo da YouTube Studio.

## Impostazioni applicate a ogni video

| Campo | Valore |
|---|---|
| Visibilità | Privato, programmato alle 13:00 di New York, poi pubblico |
| Pubblico | Non destinato ai bambini |
| Contenuti alterati o sintetici | No (animazione astratta, niente di realistico) |
| Categoria | Intrattenimento |
| Lingua | Inglese |
| Licenza | Licenza YouTube standard, incorporamento consentito |
| Notifica agli iscritti | Sì |

Titoli, descrizioni, hashtag e tag di ogni format stanno in `shorts/publishing.py`.
