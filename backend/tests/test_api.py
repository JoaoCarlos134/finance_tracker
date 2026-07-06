from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_ingest_sample_xp_like_statement(client):
    csv_bytes = (FIXTURES_DIR / "sample_statement.csv").read_bytes()
    res = client.post(
        "/ingest/csv",
        files={"file": ("sample_statement.csv", csv_bytes, "text/csv")},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["rows_inserted"] == 7
    assert body["rows_skipped"] == 0

    res = client.get("/transactions")
    transactions = res.json()
    assert len(transactions) == 7
    salary = next(t for t in transactions if t["description"] == "Salario")
    assert salary["amount"] == 5000.00


def test_list_transactions_empty(client):
    res = client.get("/transactions")
    assert res.status_code == 200
    assert res.json() == []


def test_ingest_csv_then_list(client):
    csv_content = (
        b"date,description,amount\n"
        b"2026-01-15,Coffee shop,-12.50\n"
        b"2026-01-16,Salary,2500.00\n"
    )
    res = client.post(
        "/ingest/csv",
        files={"file": ("statement.csv", csv_content, "text/csv")},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["rows_inserted"] == 2
    assert body["rows_skipped"] == 0

    res = client.get("/transactions")
    assert res.status_code == 200
    transactions = res.json()
    assert len(transactions) == 2
    assert transactions[0]["raw_source_file"] == "statement.csv"
    assert transactions[0]["category"] is None


def test_ingest_rejects_non_csv_file(client):
    res = client.post(
        "/ingest/csv",
        files={"file": ("statement.txt", b"hello", "text/plain")},
    )
    assert res.status_code == 400
