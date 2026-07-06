from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction
from app.schemas import AnalyticsSummary, CategoryPoint, MonthlyPoint

router = APIRouter(prefix="/analytics", tags=["analytics"])

ZERO = Decimal("0")

# sum/coalesce inherit the column's MoneyCents type, so results come back as
# Decimal already — no float ever enters the aggregation path.
_income_expr = func.coalesce(
    func.sum(case((Transaction.amount > 0, Transaction.amount), else_=ZERO)), ZERO
)
_spending_expr = func.coalesce(
    func.sum(case((Transaction.amount < 0, Transaction.amount), else_=ZERO)), ZERO
)


@router.get("/summary", response_model=AnalyticsSummary)
def summary(db: Session = Depends(get_db)):
    balance, income, spending, count = db.query(
        func.coalesce(func.sum(Transaction.amount), ZERO),
        _income_expr,
        _spending_expr,
        func.count(Transaction.id),
    ).one()
    return AnalyticsSummary(
        balance=balance, income=income, spending=spending, transaction_count=count
    )


@router.get("/monthly", response_model=list[MonthlyPoint])
def monthly(db: Session = Depends(get_db)):
    # strftime is SQLite-specific; swap for to_char/date_trunc in the
    # Postgres migration (Phase 6).
    month = func.strftime("%Y-%m", Transaction.date).label("month")
    rows = (
        db.query(
            month,
            _income_expr.label("income"),
            _spending_expr.label("spending"),
            func.coalesce(func.sum(Transaction.amount), ZERO).label("net"),
        )
        .group_by(month)
        .order_by(month)
        .all()
    )
    return [
        MonthlyPoint(month=r.month, income=r.income, spending=r.spending, net=r.net) for r in rows
    ]


@router.get("/by-category", response_model=list[CategoryPoint])
def by_category(db: Session = Depends(get_db)):
    category = func.coalesce(Transaction.category, "Uncategorized").label("category")
    total = func.coalesce(func.sum(Transaction.amount), ZERO).label("total")
    rows = (
        db.query(category, total, func.count(Transaction.id).label("count"))
        .group_by(category)
        .order_by(total)
        .all()
    )
    return [CategoryPoint(category=r.category, total=r.total, count=r.count) for r in rows]
