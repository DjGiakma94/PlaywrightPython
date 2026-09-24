# Playwright Login and Ranking Tests

Suite di test end-to-end e API per l'applicazione Dart BU Blue, realizzata con
Python, pytest e Playwright. I test verificano il login, le classifiche
visualizzate nella UI, gli endpoint HTTP e la coerenza tra UI e database
Supabase.

## Contenuti

- [Prerequisiti](#prerequisiti)
- [Installazione](#installazione)
- [Configurazione](#configurazione)
- [Struttura del progetto](#struttura-del-progetto)
- [Tipi di test](#tipi-di-test)
- [Esecuzione](#esecuzione)
- [Troubleshooting](#troubleshooting)

## Prerequisiti

- Python 3.10 o superiore
- PowerShell su Windows oppure una shell equivalente
- Accesso alla web app di test
- Accesso al progetto Supabase se si eseguono i test UI-database
- Chromium installato tramite Playwright

## Installazione

Dalla directory workspace:

```powershell
cd ".\playwright_login"
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Se il virtual environment non e attivo:

```powershell
..\.venv\Scripts\Activate.ps1
```

In alternativa, dalla directory workspace senza attivare l'ambiente:

```powershell
python -m pip install -r .\playwright_login\requirements.txt
```

## Configurazione

Creare `playwright_login/.env` in locale. Il file non deve essere committato.

```env
PLAYWRIGHT_USERNAME=testuser@example.com
PLAYWRIGHT_PASSWORD=testpass
PLAYWRIGHT_DISPLAY_NAME=DAVIDE
PLAYWRIGHT_HEADLESS=1
PLAYWRIGHT_TIMEOUT=30000
DATABASE_POOLER_URL=postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
```

### Variabili applicative

| Variabile | Uso | Obbligatoria |
| --- | --- | --- |
| `PLAYWRIGHT_USERNAME` | Utente usato dal test di login | No, ha un default |
| `PLAYWRIGHT_PASSWORD` | Password usata dal test di login | No, ha un default |
| `PLAYWRIGHT_DISPLAY_NAME` | Nome atteso dopo il login | No, ha un default |
| `PLAYWRIGHT_HEADLESS` | `1` headless, `0` headed | No |
| `PLAYWRIGHT_TIMEOUT` | Timeout applicativo in millisecondi | No |

### Variabili database

| Variabile | Uso | Obbligatoria |
| --- | --- | --- |
| `DATABASE_POOLER_URL` | Connection string Supabase Session Pooler | Una delle due |
| `DATABASE_URL` | Fallback per la connection string diretta | Una delle due |

La fixture usa prima `DATABASE_POOLER_URL` e poi `DATABASE_URL`. La Session
Pooler e consigliata quando la connessione diretta richiede IPv6 o non viene
risolta dalla rete locale.

Non pubblicare mai password, connection string o chiavi Supabase. Se la
password contiene caratteri speciali, deve essere URL-encoded nella stringa
di connessione.

## Struttura del progetto

```text
playwright_login/
├── config/
│   └── settings.py             # Caricamento .env e configurazione
├── database/
│   ├── __init__.py
│   ├── giocatori.py            # DDL e query della tabella giocatori
│   ├── classifica.py           # DDL e query della classifica principale
│   └── mesi.py                 # DDL e query della classifica mensile
├── fixtures/
│   ├── api.py                  # Fixture API Playwright
│   ├── browser.py              # Fixture browser Playwright
│   └── database.py             # Fixture connessione PostgreSQL
├── pages/
│   └── login_page.py           # Wrapper del Page Object
├── src/pages/
│   └── login_page.py           # Page Object principale
├── tests/
│   ├── test_login.py           # Test login e form
│   ├── test_api.py             # Test degli endpoint HTTP
│   ├── test_monthly_ranking.py # Test UI della classifica mensile
│   └── test_database_ui.py     # Confronti UI e database
├── conftest.py                 # Registrazione fixture pytest
├── requirements.txt            # Dipendenze Python
└── README.md
```

## Tipi di test

### Test API

File: `tests/test_api.py`

La fixture `api_request` crea un `APIRequestContext` Playwright con base URL
`https://dart-blu.onrender.com`. I test eseguono richieste HTTP indipendenti
dal browser:

1. `GET /api/getRankings` deve rispondere con status 2xx.
2. Il body deve essere una lista non vuota di giocatori.
3. Ogni giocatore deve contenere i campi obbligatori dell'API.
4. Gli identificativi `id_player` devono essere univoci.
5. `GET /api/refreshMonthlyPoints` deve rispondere con status 2xx.
6. Il body deve contenere `{"message": "OK"}`.

Questi test validano il contratto HTTP e JSON senza dipendere dal rendering
della pagina.

### Test UI

File: `tests/test_login.py` e `tests/test_monthly_ranking.py`.

La fixture `browser` avvia Chromium. Ogni test crea una pagina indipendente,
istanza `LoginPage`, apre l'URL e chiude la pagina al termine.

Il Page Object contiene:

- locator dei campi di login e del pulsante di invio;
- locator del bottone `CLASSIFICA MENSILE`;
- attese per la tabella principale e per la tabella nel modal mensile;
- metodi per estrarre nomi e righe della classifica.

I test verificano il comportamento osservabile dell'applicazione, senza
usare selettori CSS interni non necessari.

### Test UI-database

File: `tests/test_database_ui.py`.

Questi test usano contemporaneamente:

- `browser` per leggere i valori renderizzati nella UI;
- `db_connection` per leggere Supabase tramite `psycopg`;
- le funzioni nei moduli `database/` per mantenere DDL e SQL fuori dai test.

Il test della classifica principale:

1. Apre la pagina e legge le righe della tabella principale.
2. Esegue `fetch_main_ranking(connection)`.
3. Confronta l'insieme dei nomi UI con quello del database.
4. Confronta per ogni giocatore partite giocate, primo, secondo, terzo e podi.
5. Normalizza maiuscole, spazi e valori numerici prima del confronto.

Il test della classifica mensile:

1. Apre la pagina.
2. Clicca `CLASSIFICA MENSILE`.
3. Attende la tabella caricata nel contenitore `#monthlyBody`.
4. Esegue `fetch_monthly_ranking(connection)` sulla tabella `mesi`.
5. Confronta i nomi UI con quelli del database.
6. Confronta i dodici valori da gennaio a dicembre.
7. Converte i valori `NULL` del database in `0`, perché la UI li visualizza
   come zero.

## DDL e moduli database

Ogni file in `database/` contiene il DDL di riferimento nella costante `DDL`
e la funzione che esegue la query di lettura:

| Modulo | Tabella | Funzione |
| --- | --- | --- |
| `database/giocatori.py` | `giocatori` | `fetch_players()` |
| `database/classifica.py` | `classifica` | `fetch_main_ranking()` |
| `database/mesi.py` | `mesi` | `fetch_monthly_ranking()` |

I DDL documentano lo schema atteso e non vengono eseguiti automaticamente dai
test. Le tabelle devono quindi esistere gia nel progetto Supabase.

## Esecuzione

Dalla directory `playwright_login`:

```powershell
# Tutta la suite
python -m pytest -q

# Test login
python -m pytest -q tests/test_login.py

# Test API
python -m pytest -q tests/test_api.py

# Test classifica UI
python -m pytest -q tests/test_monthly_ranking.py

# Test confronto UI-database
python -m pytest -q tests/test_database_ui.py

# Suite con browser visibile
python -m pytest -q --headed
```

Dalla directory workspace, grazie a `pytest.ini`, e possibile anche eseguire:

```powershell
python -m pytest -q
```

## Troubleshooting

### Errore DNS o connessione Supabase

Se compare un errore come `failed to resolve host`, controllare:

1. che `DATABASE_POOLER_URL` sia presente in `playwright_login/.env`;
2. che la stringa sia copiata da Supabase alla voce **Connect > Session Pooler**;
3. che password e caratteri speciali siano URL-encoded;
4. che la rete locale consenta la connessione alla porta `5432`.

### Colonna o tabella non trovata

Le query si basano sullo schema attuale:

- `classifica`: `id_giocatore`, `partite_giocate`, `primo`, `secondo`, `terzo`;
- `giocatori`: `id`, `nome`;
- `mesi`: `id_giocatore` e colonne da `gennaio` a `dicembre`.

Se lo schema Supabase cambia, aggiornare prima il DDL e la funzione nel modulo
database corrispondente, poi rieseguire i test UI-database.

### Test UI instabile o timeout

Verificare che l'applicazione sia raggiungibile e usare `--headed` per osservare
il browser. Gli wait del Page Object attendono i contenuti reali delle tabelle,
non solo il caricamento della rete.

## Best practice adottate

- Page Object Model per i test UI.
- Fixture dedicate per browser, API e database.
- SQL e DDL separati dai test.
- Test isolati e selezionabili per file.
- Nessuna credenziale nel codice sorgente.
- Confronti normalizzati per nomi, numeri e valori `NULL`.
- Validazione del contratto API prima dei confronti UI-database.

## Riferimenti

- [Playwright Python](https://playwright.dev/python/)
- [pytest](https://docs.pytest.org/)
- [psycopg](https://www.psycopg.org/psycopg3/docs/)
- [Supabase Database](https://supabase.com/docs/guides/database)
