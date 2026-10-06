from strands import Agent

from hooks.logging_hooks import LoggingHooks
from hooks.tool_call_counter import ToolCallCounterHook
from mcp_integration.calendar_mcp_client import calendar_mcp_client
from models.model_config import DEFAULT_MODEL
from prompts import load_prompt
from tools.bill_tools import detect_recurring_bills

SYSTEM_PROMPT = load_prompt("bill_tracking")

bill_tracking_agent = Agent(
    model=DEFAULT_MODEL,
    name="bill_tracking_agent",
    system_prompt=SYSTEM_PROMPT,
    tools=[detect_recurring_bills, calendar_mcp_client],
    hooks=[LoggingHooks(), ToolCallCounterHook()],
    callback_handler=None,
)
