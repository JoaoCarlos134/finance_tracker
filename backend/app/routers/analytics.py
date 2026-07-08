from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction
from app.schemas import AnalyticsSummary, CategoryPoint, MonthlyPoint

router = APIRouter(prefix="/analytics", tags=["analytics"])

ZERO = Decimal("0")

# Bill payments settle debt already recognized via itemized card purchases
# elsewhere (see app/services/ingest.py) — counting both would double-count
# the same spending. Excluded from every aggregate below; still visible in
# the raw GET /transactions ledger for audit purposes.
NON_SPENDING_CATEGORIES = ("Credit Card Payment",)

# sum/coalesce inherit the column's MoneyCents type, so results come back as
# Decimal already — no float ever enters the aggregation path.
_income_expr = func.coalesce(
    func.sum(case((Transaction.amount > 0, Transaction.amount), else_=ZERO)), ZERO
)
_spending_expr = func.coalesce(
    func.sum(case((Transaction.amount < 0, Transaction.amount), else_=ZERO)), ZERO
)

AccountType = Query(None, pattern="^(bank|credit_card)$")


def _filtered_query(db: Session, account_type: str | None):
    # NOT IN excludes NULL categories entirely in SQL (NULL comparisons are
    # neither true nor false), which would silently drop every uncategorized
    # row from every aggregate — not just "Credit Card Payment" rows.
    query = db.query(Transaction).filter(
        or_(
            Transaction.category.is_(None),
            Transaction.category.notin_(NON_SPENDING_CATEGORIES),
        )
    )
    if account_type:
        query = query.filter(Transaction.account_type == account_type)
    return query


@router.get("/summary", response_model=AnalyticsSummary)
def summary(account_type: str | None = AccountType, db: Session = Depends(get_db)):
    balance, income, spending, count = (
        _filtered_query(db, account_type)
        .with_entities(
            func.coalesce(func.sum(Transaction.amount), ZERO),
            _income_expr,
            _spending_expr,
            func.count(Transaction.id),
        )
        .one()
    )
    return AnalyticsSummary(
        balance=balance, income=income, spending=spending, transaction_count=count
    )


@router.get("/monthly", response_model=list[MonthlyPoint])
def monthly(account_type: str | None = AccountType, db: Session = Depends(get_db)):
    # strftime is SQLite-specific; swap for to_char/date_trunc in the
    # Postgres migration (Phase 6).
    month = func.strftime("%Y-%m", Transaction.date).label("month")
    rows = (
        _filtered_query(db, account_type)
        .with_entities(
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
def by_category(account_type: str | None = AccountType, db: Session = Depends(get_db)):
    category = func.coalesce(Transaction.category, "Uncategorized").label("category")
    total = func.coalesce(func.sum(Transaction.amount), ZERO).label("total")
    rows = (
        _filtered_query(db, account_type)
        .with_entities(category, total, func.count(Transaction.id).label("count"))
        .group_by(category)
        .order_by(total)
        .all()
    )
    return [CategoryPoint(category=r.category, total=r.total, count=r.count) for r in rows]
