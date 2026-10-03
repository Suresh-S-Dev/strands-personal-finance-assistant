import os
import sys

from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient

SERVER_PATH = os.path.join(os.path.dirname(__file__), "reminder_server.py")

# continue_on_error: a dead reminder server must not crash the rest of PFA.
# The bill agent is instructed to say the reminder system is unreachable
# instead of inventing a confirmation. A real hosted Calendar MCP server
# would swap this stdio client for streamable HTTP and read a bearer token
# from the environment, for example:
#   MCPClient(url=os.environ["CALENDAR_MCP_URL"],
#             headers={"Authorization": f"Bearer {os.environ['CALENDAR_MCP_TOKEN']}"})
calendar_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command=sys.executable,
            args=[SERVER_PATH],
        )
    ),
    continue_on_error=True,
)
