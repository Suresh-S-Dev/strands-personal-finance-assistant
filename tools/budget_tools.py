from strands import tool

from config.settings import BUDGET_LIMITS
from memory.transaction_store import get_connection


def get_budget_status(category: str, month: str) -> dict | None:
    """Deterministic budget math shared by the tool and the orchestrator.

    Returns spent, limit, remaining, and over_budget, or None when the
    category has no configured limit. Routing decisions should use this
    dict, not an agent's paraphrase of it.
    """
    limit = BUDGET_LIMITS.get(category)
    if limit is None:
        return None

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE category = ? AND txn_date LIKE ?",
            (category, f"{month}%"),
        ).fetchone()
    finally:
        conn.close()

    spent = row[0]
    remaining = limit - spent
    return {
        "category": category,
        "month": month,
        "limit": limit,
        "spent": spent,
        "remaining": remaining,
        "over_budget": remaining < 0,
    }


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
    status = get_budget_status(category, month)
    if status is None:
        return f"No budget limit is configured for category '{category}'."

    spent = status["spent"]
    limit = status["limit"]
    remaining = status["remaining"]
    if remaining >= 0:
        return f"{category}: ${spent:.2f} spent of ${limit:.2f} budget — ${remaining:.2f} remaining."
    return f"{category}: ${spent:.2f} spent of ${limit:.2f} budget — ${-remaining:.2f} OVER budget."
