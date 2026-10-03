from datetime import date, timedelta

from mcp_integration import reminder_server


def test_create_and_list_upcoming_reminders(monkeypatch, tmp_path):
    monkeypatch.setattr(reminder_server, "REMINDERS_PATH", str(tmp_path / "reminders.json"))
    future = (date.today() + timedelta(days=30)).isoformat()
    past = (date.today() - timedelta(days=30)).isoformat()

    created = reminder_server.create_reminder("Electricity bill due", future, note="auto-pay off")
    reminder_server.create_reminder("Old bill", past)
    assert "Reminder #1" in created

    upcoming = reminder_server.list_upcoming_reminders()
    assert "Electricity bill due" in upcoming
    assert "Old bill" not in upcoming
