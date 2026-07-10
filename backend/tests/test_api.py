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
    # bank: -240 + 2538.83 - 700 = 1598.83 (the -130 "Credit Card Payment" row
    # is excluded from totals — see test below)
    # card (payment dropped, purchases flipped negative): -45.00 - 955.00
    assert body["balance"] == "598.83"


def test_credit_card_payment_excluded_from_spending_totals(client):
    # The bank withdrawal that pays the card bill settles debt already
    # recognized via the itemized card purchases — counting both would
    # double-count the same spending. Confirmed with the user before
    # implementing (see roadmap.txt decisions log, 2026-07-08).
    _ingest_fixture(client, "sample_bank_extract.csv")
    _ingest_fixture(client, "sample_fatura.csv")

    transactions = client.get("/transactions").json()
    payment = next(t for t in transactions if t["description"].lower() == "pagamento de fatura")
    assert payment["category"] == "Credit Card Payment"  # still visible in the raw ledger

    by_category = client.get("/analytics/by-category").json()
    assert "Credit Card Payment" not in {row["category"] for row in by_category}

    monthly = client.get("/analytics/monthly").json()
    total_net = sum(float(m["net"]) for m in monthly)
    assert round(total_net, 2) == 598.83


def test_account_type_persisted_and_filterable(client):
    _ingest_fixture(client, "sample_bank_extract.csv")
    _ingest_fixture(client, "sample_fatura.csv")

    transactions = client.get("/transactions").json()
    by_source = {t["raw_source_file"]: t["account_type"] for t in transactions}
    assert by_source["sample_bank_extract.csv"] == "bank"
    assert by_source["sample_fatura.csv"] == "credit_card"

    bank_only = client.get("/transactions", params={"account_type": "bank"}).json()
    card_only = client.get("/transactions", params={"account_type": "credit_card"}).json()
    assert len(bank_only) == 4
    assert len(card_only) == 2
    assert all(t["account_type"] == "bank" for t in bank_only)
    assert all(t["account_type"] == "credit_card" for t in card_only)

    bank_summary = client.get("/analytics/summary", params={"account_type": "bank"}).json()
    assert bank_summary["balance"] == "1598.83"


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


def test_reuploading_the_same_file_is_deduplicated(client):
    # Regression: re-uploading a file (e.g. clicking "Upload folder" twice,
    # or re-selecting an already-ingested statement) used to silently
    # double every total. Found by inspecting real data: BTBGOLDEN had 4
    # rows in the DB for only 2 distinct dates.
    first = _ingest_fixture(client)
    assert first["rows_inserted"] == 7
    assert first["rows_duplicate"] == 0

    second = _ingest_fixture(client)
    assert second["rows_inserted"] == 0
    assert second["rows_duplicate"] == 7

    transactions = client.get("/transactions").json()
    assert len(transactions) == 7  # not 14


def test_duplicate_rows_within_the_same_file_are_collapsed_once(client):
    # A CSV that repeats a line only inserts it once, not zero and not two.
    csv_bytes = (
        b"Data;Descricao;Valor\r\n"
        b"05/01/2026;Cafeteria Local;-15,00\r\n"
        b"05/01/2026;Cafeteria Local;-15,00\r\n"
    )
    res = client.post(
        "/ingest/csv",
        files={"file": ("repeated_line.csv", csv_bytes, "text/csv")},
    )
    body = res.json()
    assert body["rows_inserted"] == 1
    assert body["rows_duplicate"] == 1

    transactions = client.get("/transactions").json()
    assert len(transactions) == 1


def test_different_account_types_are_not_treated_as_duplicates(client):
    # Same date/description/amount can legitimately appear once on the bank
    # side and once on the card side without being the same transaction -
    # account_type is part of the dedup signature specifically for this.
    # sample_bank_extract.csv has "06/07/26;...;Pix enviado para Fulano de
    # Tal;-R$ 240,00;...". This is the same date/description/amount as a
    # card statement (positive in-file, flips to -240.00 on parse).
    _ingest_fixture(client, "sample_bank_extract.csv")

    card_csv = (
        b"Data;Estabelecimento;Portador;Valor;Parcela\r\n"
        b"06/07/2026;Pix enviado para Fulano de Tal;JOAO JUNIOR;R$ 240,00;-\r\n"
    )
    res = client.post(
        "/ingest/csv",
        files={"file": ("card_lookalike.csv", card_csv, "text/csv")},
    )
    body = res.json()
    assert body["rows_duplicate"] == 0
    assert body["rows_inserted"] == 1

    account_types = {t["account_type"] for t in client.get("/transactions").json()}
    assert account_types == {"bank", "credit_card"}
