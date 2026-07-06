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

    # Duplicates are allowed for now: every parsed row is inserted as-is.
    for row in rows:
        category = suggest_category(row.description)
        db.add(
            Transaction(
                date=row.date,
                description=row.description,
                amount=row.amount,
                category=category,
                category_source="rule" if category else None,
                raw_source_file=file.filename,
            )
        )
    db.commit()

    return IngestResult(
        filename=file.filename,
        rows_parsed=len(rows) + len(errors),
        rows_inserted=len(rows),
        rows_skipped=len(errors),
        errors=errors,
    )
