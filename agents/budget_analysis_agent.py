from strands import Agent

from hooks.logging_hooks import LoggingHooks
from hooks.tool_call_counter import ToolCallCounterHook
from memory.session_memory import make_session_memory
from models.model_config import DEFAULT_MODEL
from prompts import load_prompt
from sub_agents.category_classifier_subagent import classify_ambiguous_category
from sub_agents.trend_anomaly_subagent import detect_spending_trend
from tools.budget_tools import calculate_budget_remaining
from tools.datetime_tools import get_today
from tools.transaction_tools import query_transactions

SYSTEM_PROMPT = load_prompt("budget_analysis")

budget_analysis_agent = Agent(
    model=DEFAULT_MODEL,
    name="budget_analysis_agent",
    system_prompt=SYSTEM_PROMPT,
    tools=[
        query_transactions,
        calculate_budget_remaining,
        classify_ambiguous_category,
        detect_spending_trend,
        get_today,
    ],
    conversation_manager=make_session_memory(window_size=10),
    hooks=[LoggingHooks(), ToolCallCounterHook()],
    callback_handler=None,
)
