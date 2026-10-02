from strands import Agent
from models.model_config import DEFAULT_MODEL
from tools.transaction_tools import query_transactions
from tools.budget_tools import calculate_budget_remaining
from sub_agents.category_classifier_subagent import classify_ambiguous_category
from sub_agents.trend_anomaly_subagent import detect_spending_trend
from tools.datetime_tools import get_today

SYSTEM_PROMPT = """You are the Budget & Spending Analysis Agent.

Whenever the user refers to a relative time period ("this month", "today", "last month"),
call get_today FIRST to find the real current date — never assume or guess what today's
date is from your own knowledge.

Answer questions about past spending and budget status using real data only —
call query_transactions and/or calculate_budget_remaining for every number you state.

For deeper questions, delegate rather than guessing yourself:
- If asked to figure out the right category for an ambiguous or uncategorized
  expense, call classify_ambiguous_category.
- If asked whether spending in a category looks unusual or trending up/down,
  call detect_spending_trend.

You do not log new expenses and you do not answer bill-due-date questions.
You never give investment, tax, or debt advice.
"""

budget_analysis_agent = Agent(
    model=DEFAULT_MODEL,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        query_transactions,
        calculate_budget_remaining,
        classify_ambiguous_category,
        detect_spending_trend,
        get_today,
    ],
    callback_handler=None,
)