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


def test_matches_real_credit_card_merchant_patterns():
    # Real invoice merchant strings are terse POS names, not full words —
    # these were added after checking actual statement data.
    assert suggest_category("BARBEARIASHELBY") == "Personal Care"
    assert suggest_category("CLAUDE.AI SUBSCRIPTION") == "Subscriptions"
    assert suggest_category("DL*GOOGLE YOUTUB") == "Subscriptions"
    assert suggest_category("EBANX*CRUNCHYROLL") == "Subscriptions"
    assert suggest_category("HUGO BOSS DO BRA (1 de 10)") == "Shopping"
    assert suggest_category("PARKSHOPPING BARIGUI") == "Shopping"
    assert suggest_category("TACIANE LANCHES") == "Dining"
    assert suggest_category("PAGAMENTO DE FATURA") == "Credit Card Payment"
    assert suggest_category("Pagamento para LIDER CORPORATE TUR E EVENTOS") == "Travel"


def test_barbershop_does_not_collide_with_bar_or_transfer_keywords():
    # "barbearia" contains "bar" as a substring — must not fall through to a
    # hypothetical generic "bar" keyword or any other category.
    assert suggest_category("BARBEARIASHELBY") == "Personal Care"


def test_investment_transfer_does_not_collide_with_tim_keyword():
    # Regression: "investimento" contains "tim" as a substring, which used
    # to misfire the "tim" (TIM carrier) Utilities keyword and silently
    # recategorized every investment-account transfer as a phone bill —
    # found by running the real dataset through /analytics/by-category.
    assert suggest_category("Transferência enviada para a conta investimento") == "Transfers"
    assert suggest_category("Transferência recebida da conta investimento") == "Transfers"
