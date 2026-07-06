import unicodedata

# First match wins, so more specific categories come before generic ones
# (e.g. "rendimento" hits Investments before "transferencia" could match).
# Keywords are matched accent-insensitively against the lowercased description.
CATEGORY_RULES: dict[str, list[str]] = {
    "Income": ["salario", "pagamento recebido", "payroll", "pro-labore"],
    "Investments": [
        "rendimento",
        "cdb",
        "tesouro",
        "lci",
        "lca",
        "dividendo",
        "jcp",
        "aplicacao",
        "resgate",
        "fii",
    ],
    "Groceries": [
        "mercado",
        "supermercado",
        "atacadao",
        "carrefour",
        "pao de acucar",
        "hortifruti",
    ],
    "Dining": ["restaurante", "ifood", "lanchonete", "pizzaria", "padaria", "cafeteria"],
    "Transport": ["uber", "99app", "posto", "combustivel", "estacionamento", "pedagio"],
    "Utilities": ["copel", "sanepar", "energia", "agua", "internet", "vivo", "claro", "tim"],
    "Subscriptions": ["netflix", "spotify", "amazon prime", "disney", "youtube premium"],
    "Housing": ["aluguel", "condominio", "iptu"],
    "Health": ["farmacia", "drogaria", "hospital", "clinica", "laboratorio", "unimed"],
    "Transfers": ["transferencia", "ted ", "doc ", "pix"],
}


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def suggest_category(description: str) -> str | None:
    """Return the first rule category whose keywords match, or None."""
    normalized = _normalize(description)
    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in normalized for keyword in keywords):
            return category
    return None
