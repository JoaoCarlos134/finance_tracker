from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction
from app.schemas import CategoryUpdate, TransactionOut

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return (
        db.query(Transaction)
        # secondary id ordering keeps same-day rows stable across pages
        .order_by(desc(Transaction.date), desc(Transaction.id))
        .limit(limit)
        .offset(offset)
        .all()
    )


@router.patch("/{transaction_id}", response_model=TransactionOut)
def update_category(
    transaction_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
):
    tx = db.get(Transaction, transaction_id)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.category = payload.category
    tx.category_source = "user" if payload.category is not None else None
    db.commit()
    db.refresh(tx)
    return tx
