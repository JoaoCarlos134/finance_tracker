# Finance Tracker

![CI](https://github.com/JoaoCarlos134/finance_tracker/actions/workflows/ci.yml/badge.svg)

Personal finance tracker built as a portfolio project. Ingests manually
exported CSV statements from XP Investimentos — both checking-account
extracts and credit card invoices — stores them in a database, categorizes
them with keyword rules, and serves analytics to a React dashboard.

**Stack:** FastAPI + SQLAlchemy + SQLite (backend), React + Vite (frontend).

Money is handled as `Decimal` end-to-end on the server (stored as integer
cents, serialized as exact decimal strings) — floats never enter the
accounting path. Rule-based categorization runs at ingestion; manual
corrections are tracked separately (`category_source`) so they can later
train an ML categorizer without being overwritten.

## API

| Endpoint | Description |
|---|---|
| `POST /ingest/csv` | Upload a CSV statement (parsed, categorized, stored) |
| `GET /transactions?limit=&offset=` | Paginated transaction list |
| `PATCH /transactions/{id}` | Correct a category (marks it user-labeled) |
| `POST /categorize/run` | Re-apply rules to all non-user-labeled rows |
| `GET /categories` | Known category names, for populating the correction dropdown |
| `GET /analytics/summary` | Balance, income, spending, count (SQL aggregation) |
| `GET /analytics/monthly` | Per-month income/spending/net |
| `GET /analytics/by-category` | Totals and counts per category |

## Project layout

```
backend/            FastAPI app
  app/
    main.py          App entrypoint, CORS, router registration
    models.py         SQLAlchemy Transaction model
    schemas.py         Pydantic request/response models
    services/
      ingest.py          Generic CSV column-matching + parsing logic
    routers/
      transactions.py    GET /transactions
      ingestion.py        POST /ingest/csv
  tests/             pytest suite (unit tests + API tests + a sample fixture)
frontend/            Vite + React app
  src/
    App.jsx            Page assembly + data fetching/state
    api.js               fetch wrappers for the backend API
    components/
      TopNav.jsx           Nav bar
      SummaryCard.jsx        Balance/income/spending card
      TransactionsCard.jsx     Transaction list (default/loading/error/empty)
    utils/summary.js      Balance/income/spending + month-over-month math
    styles/theme.css       Design system tokens (color, type, spacing)
data/raw/             Drop your exported brokerage CSVs here (gitignored)
```

## Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. A SQLite file `finance_tracker.db`
is created automatically in `backend/` on first run (it's gitignored).

Interactive API docs: `http://localhost:8000/docs`

### Running tests

```bash
cd backend
venv\Scripts\activate
pytest -v
```

Covers CSV parsing (English and Brazilian `;`-delimited formats, missing
columns, unparseable rows) and the API endpoints end-to-end against an
in-memory SQLite database.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5178`. In dev, requests to `/api/*` are
proxied by Vite to the backend at `http://localhost:8000` (see
`vite.config.js`), so no CORS setup is needed; set `VITE_API_URL` when the
API lives on another origin.

**Windows shortcut:** double-click `run.bat` at the repo root — it starts
both servers in their own windows and opens the dashboard in your browser.

## Using it

1. Start the backend and frontend (above, or via `run.bat`).
2. Drop a CSV export from XP into `data/raw/` (optional — you can upload from
   anywhere on disk via the browser file picker).
3. Open the frontend URL Vite prints (`5178` by default), use the file picker
   to upload the CSV.
4. The parsed rows appear in the transactions table below.

No real export yet? Upload `backend/tests/fixtures/sample_statement.csv`,
`sample_bank_extract.csv`, or `sample_fatura.csv` instead — synthetic data in
the real XP formats (see below) so you can exercise the whole
upload → DB → UI flow before a real file is available.

## Design system

The UI follows a visual system ("Finance Dashboard System") imported from a
Claude Design project: dominant ink-navy (`#12202E`) with a copper accent
(`#C9752F`), Space Grotesk for headings, IBM Plex Sans for body text, and
Archivo with tabular numerals for all monetary/date figures — see
`frontend/src/styles/theme.css` for the full token set. The app keeps the
"Finance Tracker" name rather than the design mockup's placeholder brand
("Ledger"). Balance/income/spending come from `GET /analytics/summary`
(SQL aggregation on the backend); the month-over-month trend indicator only
appears once at least two months of data exist, rather than fabricating a
number from a single month.

## CSV format notes

`backend/app/services/ingest.py` handles two real XP export formats on one
code path, auto-detected from the header columns (not the filename):

- **Checking account extract** (`extrato_de_*.csv`): `Data;Hora;Descricao;
  Valor;Saldo`, semicolon-delimited, 2-digit years (`06/07/26`), amounts
  like `-R$ 2.400,00`. Negative = money out, positive = money in.
- **Credit card invoice** (`Fatura*.csv`): `Data;Estabelecimento;Portador;
  Valor;Parcela`, 4-digit years, amounts like `R$ 130,00` — but purchases
  are *positive* in the file and only the "Pagamento de fatura" row is
  negative, the opposite of the extract's convention. The parser flips
  purchase signs to match, and **drops "Pagamento de fatura" rows entirely**
  — that payment is already recorded as a withdrawal in the checking
  extract, so keeping both would double-count it. Installment info
  ("Parcela") is appended to the description, e.g. `HUGO BOSS DO BRA
  (1 de 10)`.

Column matching is otherwise generic/best-effort (case-insensitive
candidate list in `COLUMN_CANDIDATES`), with delimiter sniffing (`,` or `;`)
and Brazilian number/date fallbacks. If a real export doesn't match, add its
header names to `COLUMN_CANDIDATES` or share a sample.

Re-uploading a CSV (or one with overlapping rows) currently inserts
duplicates — there's no dedup logic for repeat uploads yet (the bank/card
cross-file dedup above is a different, narrower thing: it only drops the
one row type that's guaranteed to be a duplicate by construction).
