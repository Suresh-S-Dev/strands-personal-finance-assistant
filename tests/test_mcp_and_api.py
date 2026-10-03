import os
import sys

from fastapi.testclient import TestClient
from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient

from api import app

SERVER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "mcp_integration", "reminder_server.py")
)


def test_calendar_mcp_discovers_reminder_tools():
    client = MCPClient(
        lambda: stdio_client(StdioServerParameters(command=sys.executable, args=[SERVER_PATH]))
    )
    with client:
        names = sorted(tool.tool_name for tool in client.list_tools_sync())
    assert names == ["create_reminder", "list_upcoming_reminders"]


def test_chat_endpoint_returns_handle_request_response(monkeypatch):
    monkeypatch.setattr("api.handle_request", lambda message: f"echo:{message}")
    response = TestClient(app).post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json() == {"response": "echo:hello"}
