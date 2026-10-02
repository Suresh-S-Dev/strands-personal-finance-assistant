from strands import tool
from config.settings import BUDGET_LIMITS
from tools.transaction_tools import _get_connection


@tool
def calculate_budget_remaining(category: str, month: str) -> str:
    """Calculate remaining budget in a category for a given month.

    Args:
        category: Expense category to check (must match a category used when logging).
        month: Month to check, formatted YYYY-MM.

    Returns:
        Budget limit, amount spent, and amount remaining (or over-budget amount).
        Returns a message if no budget limit is configured for that category.
    """
    limit = BUDGET_LIMITS.get(category)
    if limit is None:
        return f"No budget limit is configured for category '{category}'."

    conn = _get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE category = ? AND txn_date LIKE ?",
        (category, f"{month}%"),
    ).fetchone()
    conn.close()
    spent = row[0]
    remaining = limit - spent

    if remaining >= 0:
        return f"{category}: ${spent:.2f} spent of ${limit:.2f} budget — ${remaining:.2f} remaining."
    return f"{category}: ${spent:.2f} spent of ${limit:.2f} budget — ${-remaining:.2f} OVER budget."