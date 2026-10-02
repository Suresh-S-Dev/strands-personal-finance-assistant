import sqlite3
from datetime import date
from strands import tool

DB_PATH = "pfa_transactions.db"


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            merchant TEXT NOT NULL,
            category TEXT NOT NULL,
            txn_date TEXT NOT NULL
        )
        """
    )
    return conn


@tool
def add_transaction(amount: float, merchant: str, category: str, txn_date: str = "") -> str:
    """Save a new expense transaction.

    Args:
        amount: Dollar amount spent (positive number).
        merchant: Where the money was spent.
        category: Expense category — call categorize_expense first if unsure.
        txn_date: ISO date (YYYY-MM-DD). Defaults to today if left blank.

    Returns:
        A confirmation string including the new transaction's id.
    """
    txn_date = txn_date or date.today().isoformat()
    conn = _get_connection()
    cursor = conn.execute(
        "INSERT INTO transactions (amount, merchant, category, txn_date) VALUES (?, ?, ?, ?)",
        (amount, merchant, category, txn_date),
    )
    conn.commit()
    txn_id = cursor.lastrowid
    conn.close()
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
    conn = _get_connection()
    query = "SELECT amount, merchant, category, txn_date FROM transactions WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if month:
        query += " AND txn_date LIKE ?"
        params.append(f"{month}%")
    rows = conn.execute(query, params).fetchall()
    conn.close()

    if not rows:
        return "No matching transactions found."

    total = sum(r[0] for r in rows)
    lines = [f"${r[0]:.2f} at {r[1]} ({r[2]}) on {r[3]}" for r in rows]
    return "\n".join(lines) + f"\n\nTotal: ${total:.2f}"