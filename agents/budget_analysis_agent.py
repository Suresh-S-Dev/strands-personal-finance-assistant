from strands import Agent
from models.model_config import DEFAULT_MODEL
from tools.transaction_tools import query_transactions
from tools.budget_tools import calculate_budget_remaining

SYSTEM_PROMPT = """You are the Budget & Spending Analysis Agent.

Answer questions about past spending and budget status using real data only —
call query_transactions and/or calculate_budget_remaining for every number you state.
Never estimate a dollar figure yourself.

You do not log new expenses and you do not answer bill-due-date questions —
those belong to other agents. You never give investment, tax, or debt advice.
"""

budget_analysis_agent = Agent(
    model=DEFAULT_MODEL,
    system_prompt=SYSTEM_PROMPT,
    tools=[query_transactions, calculate_budget_remaining],
)