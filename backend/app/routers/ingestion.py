from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction
from app.schemas import IngestResult
from app.services.categorize import suggest_category
from app.services.ingest import parse_transactions_csv

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/csv", response_model=IngestResult)
async def ingest_csv(file: UploadFile, db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")

    raw_bytes = await file.read()
    rows, errors = parse_transactions_csv(raw_bytes)

    if not rows and errors:
        raise HTTPException(status_code=422, detail=errors)

    # A duplicate is a (date, description, amount, account_type) signature
    # that's already in the DB — the concrete case this guards against is
    # re-uploading the same file (or the same folder twice), which used to
    # silently double every total. Checked against previously-committed rows
    # AND against rows already added earlier in this same file, so a file
    # that itself repeats a line only inserts it once. Trade-off: two
    # genuinely distinct real transactions that happen to share the exact
    # same date/description/amount (e.g. two identical same-day purchases)
    # collapse into one — accepted, since the motivating bug (accidental
    # re-upload) is far more common than that coincidence in practice.
    seen = {
        (tx.date, tx.description, tx.amount, tx.account_type)
        for tx in db.query(
            Transaction.date, Transaction.description, Transaction.amount, Transaction.account_type
        )
    }

    inserted = 0
    duplicates = 0
    for row in rows:
        signature = (row.date, row.description, row.amount, row.account_type)
        if signature in seen:
            duplicates += 1
            continue
        category = suggest_category(row.description)
        db.add(
            Transaction(
                date=row.date,
                description=row.description,
                amount=row.amount,
                category=category,
                category_source="rule" if category else None,
                raw_source_file=file.filename,
                account_type=row.account_type,
            )
        )
        seen.add(signature)
        inserted += 1
    db.commit()

    return IngestResult(
        filename=file.filename,
        rows_parsed=len(rows) + len(errors),
        rows_inserted=inserted,
        rows_duplicate=duplicates,
        rows_skipped=len(errors),
        errors=errors,
    )
