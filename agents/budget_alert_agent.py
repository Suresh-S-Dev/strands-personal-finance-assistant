from strands import Agent

from hooks.logging_hooks import LoggingHooks
from hooks.tool_call_counter import ToolCallCounterHook
from models.model_config import DEFAULT_MODEL
from prompts import load_prompt

SYSTEM_PROMPT = load_prompt("budget_alert")

budget_alert_agent = Agent(
    model=DEFAULT_MODEL,
    name="budget_alert_agent",
    system_prompt=SYSTEM_PROMPT,
    hooks=[LoggingHooks(), ToolCallCounterHook()],
    callback_handler=None,
)