import csv
import io
from datetime import date, datetime

# Candidate header names per field, since the exact XP export schema isn't
# pinned down yet. Add real column names here once a live export is available.
COLUMN_CANDIDATES: dict[str, list[str]] = {
    "date": ["date", "data", "data lancamento", "data do lancamento"],
    "description": ["description", "descricao", "historico", "descrição", "histórico"],
    "amount": ["amount", "valor", "valor (r$)", "valor liquido"],
}

DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]


def _normalize(header: str) -> str:
    return header.strip().lower()


def _find_column(fieldnames: list[str], field: str) -> str | None:
    candidates = COLUMN_CANDIDATES[field]
    normalized = {_normalize(h): h for h in fieldnames}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    return None


def _parse_date(raw: str) -> date:
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {raw!r}")


def _parse_amount(raw: str) -> float:
    raw = raw.strip().replace("R$", "").strip()
    try:
        return float(raw)
    except ValueError:
        pass
    # Brazilian format: "." as thousands separator, "," as decimal separator
    br_normalized = raw.replace(".", "").replace(",", ".")
    return float(br_normalized)


class ParsedRow:
    def __init__(self, date_: date, description: str, amount: float):
        self.date = date_
        self.description = description
        self.amount = amount


def parse_transactions_csv(raw_bytes: bytes) -> tuple[list[ParsedRow], list[str]]:
    """Parse a brokerage CSV export into rows, returning (rows, error_messages).

    Column matching is generic/best-effort (see COLUMN_CANDIDATES) since the
    exact XP export schema hasn't been pinned down yet.
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
    date_col = _find_column(fieldnames, "date")
    desc_col = _find_column(fieldnames, "description")
    amount_col = _find_column(fieldnames, "amount")

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
            parsed_date = _parse_date(row[date_col])
            parsed_amount = _parse_amount(row[amount_col])
            description = row[desc_col].strip()
            rows.append(ParsedRow(parsed_date, description, parsed_amount))
        except (ValueError, KeyError) as exc:
            errors.append(f"Row {i}: {exc}")

    return rows, errors
