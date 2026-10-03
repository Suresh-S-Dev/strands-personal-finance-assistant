"""
A minimal local MCP server simulating calendar/reminder functionality.
In production this would be a real Calendar MCP server (Google Calendar,
Outlook, etc.) — this version stores reminders in a local JSON file so the
whole project runs without any external account or API key.

mcp 2.x renamed FastMCP to MCPServer. The tool decorator and stdio run loop
are otherwise the same shape the agent client expects.
"""
import json
import os
from datetime import date

from mcp.server.mcpserver import MCPServer

REMINDERS_PATH = os.path.join(os.path.dirname(__file__), "reminders.json")
mcp = MCPServer("PFA Reminders")


def _load():
    if not os.path.exists(REMINDERS_PATH):
        return []
    with open(REMINDERS_PATH) as f:
        return json.load(f)


def _save(reminders):
    with open(REMINDERS_PATH, "w") as f:
        json.dump(reminders, f, indent=2)


@mcp.tool()
def create_reminder(title: str, due_date: str, note: str = "") -> str:
    """Create a reminder for a bill or event.

    Args:
        title: Short title, e.g. "Electricity bill due".
        due_date: ISO date (YYYY-MM-DD) the reminder is for.
        note: Optional extra detail.

    Returns:
        Confirmation string with the reminder's id.
    """
    reminders = _load()
    reminder_id = len(reminders) + 1
    reminders.append({"id": reminder_id, "title": title, "due_date": due_date, "note": note})
    _save(reminders)
    return f"Reminder #{reminder_id} created: '{title}' due {due_date}."


@mcp.tool()
def list_upcoming_reminders() -> str:
    """List all reminders due today or in the future.

    Returns:
        A formatted list of upcoming reminders, or a message if none exist.
    """
    reminders = _load()
    today = date.today().isoformat()
    upcoming = [r for r in reminders if r["due_date"] >= today]
    if not upcoming:
        return "No upcoming reminders."
    return "\n".join(f"#{r['id']}: {r['title']} — due {r['due_date']}" for r in upcoming)


if __name__ == "__main__":
    mcp.run(transport="stdio")
