from sqlalchemy import Column, Date, Integer, String

from app.database import Base
from app.db_types import MoneyCents


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    description = Column(String, nullable=False)
    amount = Column(MoneyCents, nullable=False)
    # nullable: rows the rule engine can't match stay uncategorized until
    # the user labels them or the future ML step fills them in
    category = Column(String, nullable=True)
    # 'rule' (keyword engine) or 'user' (manual correction). User labels are
    # never overwritten by re-running the rules — they become training data.
    category_source = Column(String, nullable=True)
    raw_source_file = Column(String, nullable=False)
    # 'bank' or 'credit_card', set from the statement type detected at parse
    # time (app/services/ingest.py). Nullable so rows ingested before this
    # column existed don't break; new rows always get one of the two values.
    account_type = Column(String, nullable=True, index=True)
