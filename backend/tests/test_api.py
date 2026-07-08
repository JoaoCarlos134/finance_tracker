from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _ingest_fixture(client, filename="sample_statement.csv"):
    csv_bytes = (FIXTURES_DIR / filename).read_bytes()
    res = client.post(
        "/ingest/csv",
        files={"file": (filename, csv_bytes, "text/csv")},
    )
    assert res.status_code == 200
    return res.json()


def test_ingest_sample_xp_like_statement(client):
    body = _ingest_fixture(client)
    assert body["rows_inserted"] == 7
    assert body["rows_skipped"] == 0

    transactions = client.get("/transactions").json()
    assert len(transactions) == 7
    salary = next(t for t in transactions if t["description"] == "Salario")
    assert salary["amount"] == "5000.00"  # money crosses JSON as exact strings


def test_ingestion_applies_category_rules(client):
    _ingest_fixture(client)
    transactions = client.get("/transactions").json()
    by_description = {t["description"]: t for t in transactions}

    assert by_description["Supermercado Extra"]["category"] == "Groceries"
    assert by_description["Supermercado Extra"]["category_source"] == "rule"
    assert by_description["Salario"]["category"] == "Income"
    assert by_description["Uber"]["category"] == "Transport"


def test_list_transactions_empty(client):
    res = client.get("/transactions")
    assert res.status_code == 200
    assert res.json() == []


def test_list_transactions_pagination(client):
    _ingest_fixture(client)

    first_page = client.get("/transactions", params={"limit": 3, "offset": 0}).json()
    second_page = client.get("/transactions", params={"limit": 3, "offset": 3}).json()

    assert len(first_page) == 3
    assert len(second_page) == 3
    assert {t["id"] for t in first_page}.isdisjoint({t["id"] for t in second_page})


def test_patch_category_marks_user_source(client):
    _ingest_fixture(client)
    tx = client.get("/transactions").json()[0]

    res = client.patch(f"/transactions/{tx['id']}", json={"category": "Custom"})
    assert res.status_code == 200
    assert res.json()["category"] == "Custom"
    assert res.json()["category_source"] == "user"


def test_patch_missing_transaction_returns_404(client):
    res = client.patch("/transactions/9999", json={"category": "X"})
    assert res.status_code == 404


def test_patch_category_to_null_clears_user_source(client):
    _ingest_fixture(client)
    tx = client.get("/transactions").json()[0]
    client.patch(f"/transactions/{tx['id']}", json={"category": "Custom"})

    res = client.patch(f"/transactions/{tx['id']}", json={"category": None})
    assert res.json()["category"] is None
    assert res.json()["category_source"] is None


def test_list_categories(client):
    res = client.get("/categories")
    assert res.status_code == 200
    categories = res.json()
    assert "Groceries" in categories
    assert "Income" in categories


def test_categorize_run_preserves_user_labels(client):
    _ingest_fixture(client)
    transactions = client.get("/transactions").json()
    uber = next(t for t in transactions if t["description"] == "Uber")

    client.patch(f"/transactions/{uber['id']}", json={"category": "Business travel"})
    run = client.post("/categorize/run").json()

    assert run["examined"] == 6  # the user-labeled row is excluded
    relabeled = next(
        t for t in client.get("/transactions").json() if t["id"] == uber["id"]
    )
    assert relabeled["category"] == "Business travel"
    assert relabeled["category_source"] == "user"


def test_analytics_summary_sums_exactly(client):
    _ingest_fixture(client)
    body = client.get("/analytics/summary").json()

    # fixture: +45.32 +5000.00 +1200.00 = 6245.32 income;
    # -354.90 -128.50 -32.15 -55.90 = -571.45 spending
    assert body["income"] == "6245.32"
    assert body["spending"] == "-571.45"
    assert body["balance"] == "5673.87"
    assert body["transaction_count"] == 7


def test_ingesting_bank_and_card_statements_avoids_double_counting(client):
    # sample_bank_extract.csv has "PAGAMENTO DE FATURA;-R$ 130,00" and
    # sample_fatura.csv has the matching "Pagamento de fatura;R$ -130,00" —
    # the same real payment. It must only be counted once.
    _ingest_fixture(client, "sample_bank_extract.csv")
    _ingest_fixture(client, "sample_fatura.csv")

    transactions = client.get("/transactions").json()
    assert len(transactions) == 6  # 4 bank rows + 3 card rows - 1 dropped payment row
    # only the bank's own withdrawal row survives; the card side's copy is dropped
    payment_rows = [t for t in transactions if t["description"].lower() == "pagamento de fatura"]
    assert len(payment_rows) == 1
    assert payment_rows[0]["raw_source_file"] == "sample_bank_extract.csv"

    body = client.get("/analytics/summary").json()
    # bank: -240 + 2538.83 - 700 - 130 = 1468.83
    # card (payment dropped, purchases flipped negative): -45.00 - 955.00
    assert body["balance"] == "468.83"


def test_analytics_monthly_groups_by_month(client):
    _ingest_fixture(client)
    body = client.get("/analytics/monthly").json()

    assert len(body) == 1  # fixture is all January 2026
    assert body[0]["month"] == "2026-01"
    assert body[0]["net"] == "5673.87"


def test_analytics_by_category_groups_totals(client):
    _ingest_fixture(client)
    body = client.get("/analytics/by-category").json()
    categories = {row["category"]: row for row in body}

    assert categories["Groceries"]["total"] == "-354.90"
    assert categories["Income"]["total"] == "5000.00"
    assert sum(row["count"] for row in body) == 7


def test_ingest_rejects_non_csv_file(client):
    res = client.post(
        "/ingest/csv",
        files={"file": ("statement.txt", b"hello", "text/plain")},
    )
    assert res.status_code == 400
