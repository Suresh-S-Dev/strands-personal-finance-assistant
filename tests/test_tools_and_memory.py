from datetime import date

from tools.budget_tools import calculate_budget_remaining, get_budget_status
from tools.category_tools import categorize_expense
from tools.transaction_tools import add_transaction, query_transactions


def test_categorize_expense_matches_keyword_and_falls_back():
    assert categorize_expense("Blue Bottle") == "Dining/Coffee"
    assert categorize_expense("unknown shop") == "Uncategorized"


def test_budget_status_under_and_over(monkeypatch, tmp_path):
    monkeypatch.setattr("memory.transaction_store.DB_PATH", str(tmp_path / "txns.db"))
    month = date.today().strftime("%Y-%m")

    add_transaction(12.5, "Blue Bottle", "Dining/Coffee", f"{month}-02")
    under = get_budget_status("Dining/Coffee", month)
    assert under["over_budget"] is False
    assert "remaining" in calculate_budget_remaining("Dining/Coffee", month)
    assert "OVER budget" not in calculate_budget_remaining("Dining/Coffee", month)

    add_transaction(420, "Trader Joe's", "Groceries", f"{month}-03")
    over = get_budget_status("Groceries", month)
    assert over["over_budget"] is True
    assert "OVER budget" in calculate_budget_remaining("Groceries", month)


def test_query_transactions_empty_database(monkeypatch, tmp_path):
    monkeypatch.setattr("memory.transaction_store.DB_PATH", str(tmp_path / "empty.db"))
    assert query_transactions() == "No matching transactions found."


def test_user_profile_persists(monkeypatch, tmp_path):
    profile_path = tmp_path / "user_profile.json"
    monkeypatch.setattr("memory.user_profile_store.PROFILE_PATH", str(profile_path))
    from memory.user_profile_store import get_profile, update_profile

    assert get_profile()["home_currency"] == "USD"
    update_profile(home_currency="EUR")
    assert get_profile()["home_currency"] == "EUR"
