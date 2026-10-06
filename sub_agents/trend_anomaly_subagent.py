from strands import Agent, tool
from models.model_config import DEFAULT_MODEL
from memory.transaction_store import get_connection
from prompts import load_prompt

SYSTEM_PROMPT = load_prompt("trend_anomaly")

_trend_agent = Agent(model=DEFAULT_MODEL, system_prompt=SYSTEM_PROMPT)


@tool
def detect_spending_trend(category: str) -> str:
    """Analyze whether a category's most recent month of spending looks anomalous.

    Args:
        category: The expense category to analyze.

    Returns:
        A short narrative on whether a meaningful spending trend/anomaly exists.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT txn_date, amount FROM transactions WHERE category = ? ORDER BY txn_date",
        (category,),
    ).fetchall()
    conn.close()

    if not rows:
        return f"No transactions found for category '{category}'."

    monthly_totals = {}
    for txn_date, amount in rows:
        month = txn_date[:7]  # YYYY-MM
        monthly_totals[month] = monthly_totals.get(month, 0) + amount

    if len(monthly_totals) < 2:
        return f"Not enough months of history for '{category}' to detect a trend yet."

    # Facts computed deterministically — only the INTERPRETATION is delegated to the LLM.
    summary = "\n".join(f"{m}: ${t:.2f}" for m, t in sorted(monthly_totals.items()))
    result = _trend_agent(f"Monthly totals for category '{category}':\n{summary}")
    return str(result)