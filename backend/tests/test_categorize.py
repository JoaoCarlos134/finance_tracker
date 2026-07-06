from app.services.categorize import suggest_category


def test_matches_brazilian_merchants():
    assert suggest_category("Supermercado Extra") == "Groceries"
    assert suggest_category("Restaurante Fasano") == "Dining"
    assert suggest_category("Uber *Trip") == "Transport"
    assert suggest_category("Netflix.com") == "Subscriptions"
    assert suggest_category("Salario") == "Income"
    assert suggest_category("Rendimento CDB") == "Investments"
    assert suggest_category("Transferencia recebida") == "Transfers"


def test_matching_is_case_and_accent_insensitive():
    assert suggest_category("SALÁRIO MENSAL") == "Income"
    assert suggest_category("Condomínio Ed. Central") == "Housing"
    assert suggest_category("FARMÁCIA SÃO JOÃO") == "Health"


def test_unknown_description_returns_none():
    assert suggest_category("Estabelecimento desconhecido XYZ") is None
    assert suggest_category("") is None


def test_specific_categories_win_over_generic():
    # "Rendimento" (Investments) must win even though a transfer description
    # could also contain generic transfer words later in the rule table.
    assert suggest_category("Rendimento transferido via PIX") == "Investments"
