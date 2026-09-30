# Pubblicazione automatica su YouTube

Con questa configurazione la Routine giornaliera genera il video, lo carica sul canale e lo programma alle 13:00 di New York (19:00 in Italia). Titolo, descrizione, hashtag, tag e impostazioni sono già pronti.

Il limite da conoscere prima di partire: finché il tuo progetto Google Cloud non passa l'**audit delle YouTube API**, YouTube blocca come privato ogni video caricato via API, e quel video non si può più rendere pubblico. Per questo la pubblicazione automatica si accende solo dopo l'approvazione (passo 7). Fino ad allora la Routine ti manda il video sul telefono con la scheda di pubblicazione pronta da copiare.

## 1. Progetto Google Cloud

1. Vai su [console.cloud.google.com](https://console.cloud.google.com) con l'account Google del canale e crea un progetto (per esempio `claude-code-shorts`).
2. In *API e servizi → Libreria* cerca **YouTube Data API v3** e premi **Abilita**.

## 2. Schermata di consenso OAuth

1. *API e servizi → Schermata di consenso OAuth* (o *Google Auth Platform*): tipo di utente **Esterno**. Metti nome app, la tua email come supporto e contatto, poi salva.
2. Nella sezione *Pubblico* aggiungi la tua email come utente di test, poi premi **Pubblica app**, così lo stato diventa *In produzione*.
   - Va fatto perché in stato *Test* il token scade dopo 7 giorni e l'automazione si fermerebbe.
   - Per uso personale non serve la verifica dell'app: durante l'accesso vedrai l'avviso "app non verificata", premi *Avanzate → Vai all'app*.

## 3. Client OAuth

*API e servizi → Credenziali → Crea credenziali → ID client OAuth*, tipo **App desktop**. Ti dà un **Client ID** e un **Client secret**.

## 4. Refresh token (una volta, sul tuo computer)

Con Python installato, dalla cartella del repo:

```bash
python youtube_auth.py --client-id IL_TUO_CLIENT_ID --client-secret IL_TUO_CLIENT_SECRET
```

Si apre il browser: accedi con l'account del canale (se il canale è un brand account, sceglilo) e accetta. Nel terminale compare il **refresh token**.

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
python publish.py out/daily/<file>.mp4 --dry-run
```

Mostra esattamente cosa verrebbe inviato a YouTube, senza caricare niente.

## 7. Audit, poi accensione

1. Compila il [modulo di audit delle YouTube API](https://support.google.com/youtube/contact/yt_api_form). Descrivi il progetto per quello che è: uno strumento personale che carica e programma sul tuo canale uno Short al giorno generato dal tuo codice. Il processo è spiegato nella [guida di Google agli audit](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits).
2. Quando arriva l'approvazione, aggiungi la variabile d'ambiente **`YT_AUTO_PUBLISH=1`**.

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
