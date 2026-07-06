from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer

# Serialized as a fixed two-decimal string ("-1234.56") so exact values cross
# the JSON boundary; clients coerce for display math only.
Money = Annotated[Decimal, PlainSerializer(lambda v: f"{v:.2f}", return_type=str)]


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    description: str
    amount: Money
    category: str | None
    category_source: str | None
    raw_source_file: str


class CategoryUpdate(BaseModel):
    category: str | None


class IngestResult(BaseModel):
    filename: str
    rows_parsed: int
    rows_inserted: int
    rows_skipped: int
    errors: list[str]


class CategorizeRunResult(BaseModel):
    examined: int
    updated: int


class AnalyticsSummary(BaseModel):
    balance: Money
    income: Money
    spending: Money
    transaction_count: int


class MonthlyPoint(BaseModel):
    month: str  # "YYYY-MM"
    income: Money
    spending: Money
    net: Money


class CategoryPoint(BaseModel):
    category: str
    total: Money
    count: int
