import csv
import io
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

# Candidate header names per field. "estabelecimento" covers credit card
# invoices (Fatura*.csv), which have no "descricao" column of their own.
COLUMN_CANDIDATES: dict[str, list[str]] = {
    "date": ["date", "data", "data lancamento", "data do lancamento"],
    "description": [
        "description",
        "descricao",
        "historico",
        "descrição",
        "histórico",
        "estabelecimento",
    ],
    "amount": ["amount", "valor", "valor (r$)", "valor liquido"],
}

# Presence of either column identifies a credit card invoice (Fatura*.csv)
# rather than a bank account extract: purchases are positive there (the
# opposite of the bank extract's convention), and its "Pagamento de fatura"
# rows duplicate a payment already recorded on the bank side.
CREDIT_CARD_MARKER_COLUMNS = ["portador", "parcela"]
PAGAMENTO_FATURA = "pagamento de fatura"

DATE_FORMATS = ["%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%m/%d/%Y"]


def _normalize(header: str) -> str:
    return header.strip().lower()


def _normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.strip().lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _find_column(normalized_map: dict[str, str], field: str) -> str | None:
    for candidate in COLUMN_CANDIDATES[field]:
        if candidate in normalized_map:
            return normalized_map[candidate]
    return None


def _parse_date(raw: str) -> date:
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {raw!r}")


def _parse_amount(raw: str) -> Decimal:
    # Strip the "R$" marker and *all* whitespace, not just leading/trailing:
    # the bank extract writes negative amounts as "-R$ 2.400,00", which
    # leaves a stray space ("- 2.400,00") once "R$" is removed.
    raw = "".join(raw.replace("R$", "").split())
    try:
        return Decimal(raw)
    except InvalidOperation:
        pass
    # Brazilian format: "." as thousands separator, "," as decimal separator
    br_normalized = raw.replace(".", "").replace(",", ".")
    try:
        return Decimal(br_normalized)
    except InvalidOperation as exc:
        raise ValueError(f"Unrecognized amount format: {raw!r}") from exc


class ParsedRow:
    def __init__(self, date_: date, description: str, amount: Decimal, account_type: str):
        self.date = date_
        self.description = description
        self.amount = amount
        self.account_type = account_type


def parse_transactions_csv(raw_bytes: bytes) -> tuple[list[ParsedRow], list[str]]:
    """Parse a bank extract or credit card invoice CSV into rows.

    Column matching is generic/best-effort (see COLUMN_CANDIDATES) to cover
    both statement types on one code path.
    """
    text = raw_bytes.decode("utf-8-sig", errors="replace")
    # Brazilian exports commonly use ";" as the delimiter, since "," is the
    # decimal separator there. Sniff instead of assuming a fixed delimiter.
    try:
        dialect = csv.Sniffer().sniff(text[:2048], delimiters=",;")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)

    if not reader.fieldnames:
        return [], ["CSV file has no header row"]

    fieldnames = list(reader.fieldnames)
    normalized_map = {_normalize(h): h for h in fieldnames}
    is_credit_card = any(col in normalized_map for col in CREDIT_CARD_MARKER_COLUMNS)
    account_type = "credit_card" if is_credit_card else "bank"

    date_col = _find_column(normalized_map, "date")
    desc_col = _find_column(normalized_map, "description")
    amount_col = _find_column(normalized_map, "amount")
    parcela_col = normalized_map.get("parcela")

    missing = [
        name
        for name, col in [("date", date_col), ("description", desc_col), ("amount", amount_col)]
        if col is None
    ]
    if missing:
        return [], [
            f"Could not find column(s) for: {', '.join(missing)}. "
            f"Found headers: {fieldnames}"
        ]

    rows: list[ParsedRow] = []
    errors: list[str] = []
    for i, row in enumerate(reader, start=2):  # start=2: header is row 1
        try:
            description = row[desc_col].strip()

            # This exact payment is already recorded as a withdrawal in the
            # bank extract; keeping it here too would double-count it.
            if is_credit_card and _normalize_text(description) == PAGAMENTO_FATURA:
                continue

            parsed_date = _parse_date(row[date_col])
            parsed_amount = _parse_amount(row[amount_col])

            if is_credit_card:
                # Invoice purchases are positive in the file; our convention
                # is negative = money spent, so flip them.
                parsed_amount = -parsed_amount
                if parcela_col:
                    parcela = row.get(parcela_col, "").strip()
                    if parcela and parcela != "-":
                        description = f"{description} ({parcela})"

            rows.append(ParsedRow(parsed_date, description, parsed_amount, account_type))
        except (ValueError, KeyError) as exc:
            errors.append(f"Row {i}: {exc}")

    return rows, errors
