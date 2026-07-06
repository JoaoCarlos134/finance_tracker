from sqlalchemy import Column, Date, Float, Integer, String

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    # nullable: categorization is done by a future ML step, not at ingestion time
    category = Column(String, nullable=True)
    raw_source_file = Column(String, nullable=False)
