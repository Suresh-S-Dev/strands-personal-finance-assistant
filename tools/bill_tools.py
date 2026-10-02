from collections import defaultdict
from strands import tool
from tools.transaction_tools import _get_connection


@tool
def detect_recurring_bills(name: str = "") -> str:
    """Detect recurring monthly bills from transaction history.

    Args:
        name: Optional merchant or category name to filter to (e.g. "electric").
              Empty string checks all transactions.

    Returns:
        Detected recurring merchants with occurrence count, average amount, and dates.
        Returns a message if nothing recurring is found yet.
    """
    conn = _get_connection()
    query = "SELECT amount, merchant, category, txn_date FROM transactions WHERE 1=1"
    params = []
    if name:
        query += " AND (LOWER(merchant) LIKE ? OR LOWER(category) LIKE ?)"
        params.extend([f"%{name.lower()}%", f"%{name.lower()}%"])
    rows = conn.execute(query, params).fetchall()
    conn.close()

    grouped = defaultdict(list)
    for amount, merchant, category, txn_date in rows:
        grouped[merchant].append((amount, txn_date))

    recurring = {m: v for m, v in grouped.items() if len(v) >= 2}
    if not recurring:
        return "No recurring pattern found yet — need at least two occurrences for the same merchant."

    lines = []
    for merchant, entries in recurring.items():
        avg = sum(e[0] for e in entries) / len(entries)
        dates = ", ".join(e[1] for e in entries)
        lines.append(f"{merchant}: appears {len(entries)}x (avg ${avg:.2f}), dates: {dates}")
    return "\n".join(lines)