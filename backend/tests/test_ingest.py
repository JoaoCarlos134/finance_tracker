from datetime import date
from decimal import Decimal

from app.services.ingest import parse_transactions_csv


def test_parses_english_headers():
    csv_bytes = (
        b"date,description,amount\n"
        b"2026-01-15,Coffee shop,-12.50\n"
        b"2026-01-16,Salary,2500.00\n"
    )
    rows, errors = parse_transactions_csv(csv_bytes)

    assert errors == []
    assert len(rows) == 2
    assert rows[0].date == date(2026, 1, 15)
    assert rows[0].description == "Coffee shop"
    assert rows[0].amount == Decimal("-12.50")
    assert rows[1].amount == Decimal("2500.00")


def test_parses_brazilian_semicolon_delimited_format():
    # Brazilian exports commonly use ";" as the delimiter, since "," is the
    # decimal separator there and would otherwise collide with it.
    csv_bytes = (
        "Data;Descricao;Valor\n"
        "15/01/2026;Compra no mercado;-1.234,56\n"
        "16/01/2026;Salario;2.500,00\n"
    ).encode("utf-8-sig")
    rows, errors = parse_transactions_csv(csv_bytes)

    assert errors == []
    assert len(rows) == 2
    assert rows[0].date == date(2026, 1, 15)
    assert rows[0].amount == Decimal("-1234.56")
    assert rows[1].amount == Decimal("2500.00")


def test_amounts_are_exact_decimals_not_floats():
    # 0.1 + 0.2 style float artifacts must never enter the pipeline
    csv_bytes = b"date,description,amount\n2026-01-15,Test,0.10\n2026-01-15,Test,0.20\n"
    rows, errors = parse_transactions_csv(csv_bytes)

    assert errors == []
    assert sum(r.amount for r in rows) == Decimal("0.30")
    assert all(isinstance(r.amount, Decimal) for r in rows)


def test_missing_required_columns_reports_error():
    csv_bytes = b"foo,bar\n1,2\n"
    rows, errors = parse_transactions_csv(csv_bytes)

    assert rows == []
    assert len(errors) == 1
    assert "Could not find column" in errors[0]


def test_unparseable_row_is_skipped_with_error():
    csv_bytes = (
        b"date,description,amount\n"
        b"2026-01-15,Good row,10.00\n"
        b"not-a-date,Bad row,5.00\n"
    )
    rows, errors = parse_transactions_csv(csv_bytes)

    assert len(rows) == 1
    assert len(errors) == 1
    assert "Row 3" in errors[0]


def test_unparseable_amount_is_skipped_with_error():
    csv_bytes = (
        b"date,description,amount\n"
        b"2026-01-15,Good row,10.00\n"
        b"2026-01-16,Bad amount,abc\n"
    )
    rows, errors = parse_transactions_csv(csv_bytes)

    assert len(rows) == 1
    assert len(errors) == 1
    assert "Row 3" in errors[0]
