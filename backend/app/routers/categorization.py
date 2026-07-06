from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction
from app.schemas import CategorizeRunResult
from app.services.categorize import suggest_category

router = APIRouter(prefix="/categorize", tags=["categorization"])


@router.post("/run", response_model=CategorizeRunResult)
def run_categorization(db: Session = Depends(get_db)):
    """Re-apply the keyword rules to every row the user hasn't labeled.

    User-corrected rows (category_source == 'user') are never touched — those
    labels are the future training data and must survive rule changes.
    """
    candidates = (
        db.query(Transaction)
        .filter(or_(Transaction.category_source.is_(None), Transaction.category_source == "rule"))
        .all()
    )

    updated = 0
    for tx in candidates:
        suggestion = suggest_category(tx.description)
        new_source = "rule" if suggestion else None
        if tx.category != suggestion or tx.category_source != new_source:
            tx.category = suggestion
            tx.category_source = new_source
            updated += 1
    db.commit()

    return CategorizeRunResult(examined=len(candidates), updated=updated)
