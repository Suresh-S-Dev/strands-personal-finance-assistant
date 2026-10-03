from strands import Agent

from guardrails.tool_guardrails import LargeExpenseGuardrail
from hooks.logging_hooks import LoggingHooks
from hooks.security_hooks import SecurityHooks
from hooks.tool_call_counter import ToolCallCounterHook
from models.model_config import DEFAULT_MODEL
from tools.category_tools import categorize_expense
from tools.transaction_tools import add_transaction

SYSTEM_PROMPT = """You are the Expense Logging Agent.

For each expense: call categorize_expense, then add_transaction, then confirm
what you saved.

If an expense is unusually large, add_transaction will be rejected unless you
pass confirmed=True — ask the user to confirm the amount first, and only call
add_transaction again with confirmed=True after they say yes.

If categorize_expense returns "Uncategorized", ask the user — never guess.
If the amount is missing, ask for it — never invent one.
You do not answer spending/budget/bill questions.
"""

expense_logging_agent = Agent(
    model=DEFAULT_MODEL,
    name="expense_logging_agent",
    system_prompt=SYSTEM_PROMPT,
    tools=[categorize_expense, add_transaction],
    hooks=[LoggingHooks(), SecurityHooks(), LargeExpenseGuardrail(), ToolCallCounterHook()],
    callback_handler=None,
)
