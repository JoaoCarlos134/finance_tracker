from decimal import Decimal

from sqlalchemy.types import Integer, TypeDecorator


class MoneyCents(TypeDecorator):
    """Monetary value stored as integer cents, exposed as Decimal.

    Integer storage keeps sums exact in SQLite (no native DECIMAL type) and
    ports unchanged to Postgres. Never store money as float: binary floats
    accumulate rounding errors under aggregation.
    """

    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return int(round(Decimal(str(value)) * 100))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Decimal(value) / 100
