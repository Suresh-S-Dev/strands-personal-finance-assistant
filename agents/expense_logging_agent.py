from strands import Agent

from guardrails.tool_guardrails import LargeExpenseGuardrail
from hooks.logging_hooks import LoggingHooks
from hooks.security_hooks import SecurityHooks
from hooks.tool_call_counter import ToolCallCounterHook
from models.model_config import DEFAULT_MODEL
from prompts import load_prompt
from tools.category_tools import categorize_expense
from tools.transaction_tools import add_transaction

SYSTEM_PROMPT = load_prompt("expense_logging")

expense_logging_agent = Agent(
    model=DEFAULT_MODEL,
    name="expense_logging_agent",
    system_prompt=SYSTEM_PROMPT,
    tools=[categorize_expense, add_transaction],
    hooks=[LoggingHooks(), SecurityHooks(), LargeExpenseGuardrail(), ToolCallCounterHook()],
    callback_handler=None,
)
