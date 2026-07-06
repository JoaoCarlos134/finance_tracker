# Finance Tracker

Personal finance tracker built as a portfolio project. Ingests manually
exported CSV statements (currently targeting XP Investimentos exports),
stores them in a database, and displays them in a web UI.

**Stack:** FastAPI + SQLAlchemy + SQLite (backend), React + Vite (frontend).

This is currently a skeleton: upload a CSV, see the parsed rows land in the
database, and see them listed in the browser. Categorization/ML logic is not
built yet — the `category` field exists but is left `null` at ingestion time.

## Project layout

```
backend/            FastAPI app
  app/
    main.py          App entrypoint, CORS, router registration
    models.py         SQLAlchemy Transaction model
    schemas.py         Pydantic request/response models
    csv_parser.py        Generic CSV column-matching + parsing logic
    routers/
      transactions.py    GET /transactions
      ingestion.py        POST /ingest/csv
frontend/            Vite + React app
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

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173` and expects the backend to be
running at `http://localhost:8000` (see `frontend/src/api.js`).

> Note: `npm install` was not run as part of scaffolding this project — this
> environment hit a corporate SSL-inspection proxy error
> (`SELF_SIGNED_CERT_IN_CHAIN`) when trying to reach the npm registry. Run
> `npm install` yourself in an environment where your npm client trusts your
> network's CA (this is likely already configured for your normal workflow).

## Using it

1. Start the backend and frontend (above).
2. Drop a CSV export from your brokerage into `data/raw/` (optional — you can
   upload from anywhere on disk via the browser file picker).
3. Open `http://localhost:5173`, use the file picker to upload the CSV.
4. The parsed rows appear in the transactions table below.

## CSV format notes

The exact column layout of XP Investimentos exports isn't pinned down yet,
so `backend/app/csv_parser.py` does best-effort, case-insensitive matching
against a list of candidate header names for `date`, `description`, and
`amount` (see `COLUMN_CANDIDATES`). It also falls back to Brazilian number
formatting (`1.234,56`) and `dd/mm/yyyy` dates if the direct parse fails.

If your real export doesn't match, either:
- add its actual header names to `COLUMN_CANDIDATES`, or
- share a sample export so the parser can be tightened to the real schema.

Re-uploading a CSV (or one with overlapping rows) currently inserts
duplicates — there's no dedup logic yet. This can be added once we know
what a genuine duplicate looks like in a real export.
