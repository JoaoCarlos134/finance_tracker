from datetime import date

from pydantic import BaseModel, ConfigDict


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    description: str
    amount: float
    category: str | None
    raw_source_file: str


class IngestResult(BaseModel):
    filename: str
    rows_parsed: int
    rows_inserted: int
    rows_skipped: int
    errors: list[str]
