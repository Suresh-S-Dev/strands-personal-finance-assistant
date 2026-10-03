from strands import Agent

from hooks.logging_hooks import LoggingHooks
from hooks.tool_call_counter import ToolCallCounterHook
from models.model_config import DEFAULT_MODEL

SYSTEM_PROMPT = """You are the Budget Alert Agent.

You're shown a budget status report indicating the user has gone over budget in
some category. Write one short, friendly, non-judgmental sentence encouraging
them to take a look. No guilt-tripping, no financial advice — just a gentle nudge.
"""

budget_alert_agent = Agent(
    model=DEFAULT_MODEL,
    name="budget_alert_agent",
    system_prompt=SYSTEM_PROMPT,
    hooks=[LoggingHooks(), ToolCallCounterHook()],
    callback_handler=None,
)