import json
import sqlite3
from datetime import date

from memory.retry import retry_with_backoff
from orchestrator.spending_review_graph import is_over_budget
from scripts.summarize_logs import summarize
from tools.transaction_tools import add_transaction


class _State:
    def __init__(self, task):
        self.task = task


def test_is_over_budget_uses_stored_totals_not_wording(monkeypatch, tmp_path):
    monkeypatch.setattr("memory.transaction_store.DB_PATH", str(tmp_path / "txns.db"))
    month = date.today().strftime("%Y-%m")
    add_transaction(12.5, "Blue Bottle", "Dining/Coffee", f"{month}-01")
    add_transaction(420, "Market", "Groceries", f"{month}-02")

    assert is_over_budget(_State("How much have I spent on Dining/Coffee this month?")) is False
    assert is_over_budget(_State("How much have I spent on coffee this month?")) is False
    assert is_over_budget(_State("How much have I spent on rent this month?")) is False
    assert is_over_budget(_State("How much have I spent on Groceries this month?")) is True
    assert is_over_budget(_State("How much have I spent this month?")) is True


def test_retry_eventually_succeeds_and_reraises():
    attempts = {"n": 0}

    @retry_with_backoff(max_attempts=3, base_delay=0, exceptions=(sqlite3.OperationalError,))
    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise sqlite3.OperationalError("database is locked")
        return "saved"

    assert flaky() == "saved"
    assert attempts["n"] == 3

    @retry_with_backoff(max_attempts=2, base_delay=0, exceptions=(sqlite3.OperationalError,))
    def always_locked():
        raise sqlite3.OperationalError("database is locked")

    try:
        always_locked()
    except sqlite3.OperationalError as exc:
        assert "locked" in str(exc)
    else:
        raise AssertionError("expected the final OperationalError to propagate")


def test_summarize_logs(tmp_path):
    path = tmp_path / "pfa.log"
    records = [
        {"event": "invocation_end", "duration_seconds": 1.0},
        {"event": "invocation_end", "duration_seconds": 3.0},
        {"event": "tool_start", "tool": "add_transaction"},
        {"event": "guardrail_violation", "guardrail": "LargeExpenseGuardrail"},
        "not json",
    ]
    path.write_text("\n".join(json.dumps(r) if isinstance(r, dict) else r for r in records) + "\n")
    summary = summarize(str(path))
    assert summary == "2 invocations, 1 tool calls, 1 guardrail violations, average duration 2.00s"
