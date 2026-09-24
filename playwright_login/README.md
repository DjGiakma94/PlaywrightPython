# Playwright Login Automation

Questo progetto dimostra una struttura professionale per test di automazione UI con Playwright e pytest, dedicata al login su una web app.

## Obiettivo

Verificare il flusso di login, controllare la visibilità del form e mantenere una struttura di progetto pulita, scalabile e facile da estendere.

## Requisiti

- Python 3.10+
- pip
- browser Chromium installato tramite Playwright

## Setup iniziale

```bash
cd playwright_login
pip install -r requirements.txt
python -m playwright install
```

## Struttura del progetto

```text
playwright_login/
├── .env                       # variabili locali non versionate
├── .gitignore                 # file da ignorare in Git
├── conftest.py                # fixture globali pytest
├── playwright.config.py       # configurazione Playwright
├── requirements.txt           # dipendenze del progetto
├── README.md                  # documentazione del progetto
├── config/
│   ├── __init__.py
│   └── settings.py            # lettura env vars e helper
├── data/
│   ├── __init__.py
│   └── users.py               # dati di default
├── fixtures/
│   ├── __init__.py
│   └── browser.py             # fixture browser
├── models/
│   ├── __init__.py
│   └── user.py                # modello dati
├── pages/
│   ├── __init__.py
│   └── login_page.py          # Page Object per il login
├── src/
│   ├── __init__.py
│   ├── login_page.py          # wrapper compatibile per import legacy
│   └── pages/
│       ├── __init__.py
│       └── login_page.py      # Page Object principale
├── tests/
│   └── test_login.py          # test di login
├── utils/
│   ├── __init__.py
│   └── test_data.py          # helper per dati di test
├── manual_login.py            # script manuale di login
├── legacy_settings.py         # compatibilità storica, da rimuovere in futuro
└── README.md                 # documentazione del progetto
```

## Convenzioni del progetto

- Il Page Object va dentro la cartella `pages/`.
- I fixture di pytest vanno dentro `fixtures/`.
- Le configurazioni e le variabili d'ambiente vanno dentro `config/`.
- I dati statici vanno dentro `data/`.
- I modelli di dominio vanno dentro `models/`.
- I test reali vanno dentro `tests/`.
- I file manuali di utilità vanno chiamati in modo esplicito (es. `manual_login.py`).
- I riferimenti legacy vanno eliminati quando non servono più; per compatibilità temporanea, si può lasciare un wrapper o file storico.
- File generati da runtime come `.pytest_cache`, `__pycache__`, `.venv` vanno ignorati da Git.

## Esecuzione dei test

### Modalità normale

```bash
python -m pytest -q
```

### Modalità headed (browser visibile)

```bash
python -m pytest -q --headed
```

### Esecuzione test specifico

```bash
python -m pytest -q tests/test_login.py
```

### Confronto UI e database

I test in `tests/test_database_ui.py` confrontano i valori delle classifiche
visualizzate con le tabelle Supabase `classifica`, `giocatori` e `punti`.
Richiedono una connection string nel file `.env`. È preferibile usare la
connection string **Session pooler** in `DATABASE_POOLER_URL`, perché la
connessione diretta Supabase può richiedere IPv6.

```bash
python -m pytest -q tests/test_database_ui.py
```

## Variabili d'ambiente

Le variabili supportate sono:

- `PLAYWRIGHT_USERNAME`
- `PLAYWRIGHT_PASSWORD`
- `PLAYWRIGHT_DISPLAY_NAME`
- `PLAYWRIGHT_HEADLESS`
- `PLAYWRIGHT_TIMEOUT`

Esempio Windows PowerShell:

```powershell
$env:PLAYWRIGHT_USERNAME = 'testuser@example.com'
$env:PLAYWRIGHT_PASSWORD = 'testpass'
$env:PLAYWRIGHT_DISPLAY_NAME = 'DAVIDE'
$env:PLAYWRIGHT_HEADLESS = '0'
$env:PLAYWRIGHT_TIMEOUT = '30000'
python -m pytest -q
```

## Note

- Il file `.env` va usato solo in locale.
- Non committare credenziali reali.
- Quando aggiungi nuovi test, mantieni una regola chiara: ogni test deve verificare un comportamento reale e osservabile dell'applicazione.

## Riferimenti

- [Playwright Python](https://playwright.dev/python/)
- [pytest](https://docs.pytest.org/)
- [Page Object Model](https://playwright.dev/python/docs/pom)
