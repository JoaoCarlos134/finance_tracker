import unicodedata

# First match wins, so more specific categories come before generic ones
# (e.g. "rendimento" hits Investments before "transferencia" could match).
# Keywords are matched accent-insensitively against the lowercased description.
# "Personal Care", "Shopping", "Travel" and "Credit Card Payment" were added
# after checking real statement data — merchant names there are terse POS
# strings (e.g. "DL*GOOGLE YOUTUB") that generic guesses didn't cover.
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
    "Credit Card Payment": ["pagamento de fatura"],
    "Groceries": [
        "mercado",
        "supermercado",
        "atacadao",
        "carrefour",
        "pao de acucar",
        "hortifruti",
        "alimentos",
    ],
    "Dining": [
        "restaurante",
        "ifood",
        "lanchonete",
        "pizzaria",
        "padaria",
        "cafeteria",
        "lanches",
        "trattori",
        "ristorante",
        "gastronomi",
        "poutz",
        "bonobo cafe",
        "casa verde deck bar",
        "dark sugar",
        "lindt",
        "frit batatas",
    ],
    "Transport": [
        "uber",
        "99app",
        "posto",
        "combustivel",
        "estacionamento",
        "pedagio",
        "allpark",
    ],
    "Utilities": ["copel", "sanepar", "energia", "agua", "internet", "vivo", "claro", "tim"],
    "Subscriptions": [
        "netflix",
        "spotify",
        "amazon prime",
        "disney",
        "youtube premium",
        "youtub",
        "crunchyroll",
        "claude.ai",
    ],
    "Housing": ["aluguel", "condominio", "iptu"],
    "Health": ["farmacia", "drogaria", "hospital", "clinica", "laboratorio", "unimed"],
    "Personal Care": ["barbearia", "salao de beleza", "estetica"],
    "Shopping": ["hugo boss", "centauro", "parkshopping", "shopping"],
    "Travel": ["lider corporate", "passagem aerea", "hotel", "airbnb", "decolar"],
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
