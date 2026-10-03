import os
import sqlite3

DB_PATH = os.environ.get("PFA_DB_PATH", "pfa_transactions.db")


def get_connection():
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
