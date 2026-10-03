import sqlite3
from datetime import date

from strands import tool

from memory.retry import retry_with_backoff
from memory.transaction_store import get_connection


@retry_with_backoff(max_attempts=3, exceptions=(sqlite3.OperationalError,))
def _write_transaction(amount, merchant, category, txn_date):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO transactions (amount, merchant, category, txn_date) VALUES (?, ?, ?, ?)",
            (amount, merchant, category, txn_date),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


@tool
def add_transaction(amount: float, merchant: str, category: str, txn_date: str = "", confirmed: bool = False) -> str:
    """Save a new expense transaction.

    Args:
        amount: Dollar amount spent (positive number).
        merchant: Where the money was spent.
        category: Expense category — call categorize_expense first if unsure.
        txn_date: ISO date (YYYY-MM-DD). Defaults to today if left blank.
        confirmed: Set True only after the user has explicitly confirmed a
            large amount. Required above the configured confirmation
            threshold — see LargeExpenseGuardrail; calls without it above
            the threshold will be rejected before this function even runs.

    Returns:
        A confirmation string including the new transaction's id.
    """
    txn_date = txn_date or date.today().isoformat()
    txn_id = _write_transaction(amount, merchant, category, txn_date)
    return f"Saved transaction #{txn_id}: ${amount:.2f} at {merchant} ({category}) on {txn_date}"


@tool
def query_transactions(category: str = "", month: str = "") -> str:
    """Look up past transactions, optionally filtered.

    Args:
        category: Exact category to filter to. Empty string = all categories.
        month: Month to filter to, as YYYY-MM. Empty string = all time.

    Returns:
        A formatted list of matching transactions plus their total.
    """
    conn = get_connection()
    try:
        query = "SELECT amount, merchant, category, txn_date FROM transactions WHERE 1=1"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if month:
            query += " AND txn_date LIKE ?"
            params.append(f"{month}%")
        rows = conn.execute(query, params).fetchall()
    finally:
        conn.close()

    if not rows:
        return "No matching transactions found."

    total = sum(r[0] for r in rows)
    lines = [f"${r[0]:.2f} at {r[1]} ({r[2]}) on {r[3]}" for r in rows]
    return "\n".join(lines) + f"\n\nTotal: ${total:.2f}"
