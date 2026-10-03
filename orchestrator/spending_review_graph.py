import re
from datetime import date

from strands.multiagent import GraphBuilder

from agents.budget_alert_agent import budget_alert_agent
from agents.budget_analysis_agent import budget_analysis_agent
from config.settings import BUDGET_LIMITS
from tools.budget_tools import get_budget_status
from tools.category_tools import CATEGORY_KEYWORDS


def _month_from_task(task: str) -> str:
    match = re.search(r"\b(20\d{2}-\d{2})\b", task)
    if match:
        return match.group(1)
    today = date.today()
    if "last month" in task.lower():
        year, month = today.year, today.month - 1
        if month == 0:
            year, month = year - 1, 12
        return f"{year:04d}-{month:02d}"
    return today.strftime("%Y-%m")


def _categories_from_task(task: str) -> list[str]:
    text = task.lower()
    matched = [category for category in BUDGET_LIMITS if category.lower() in text]
    if matched:
        return matched
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in text and category in BUDGET_LIMITS and category not in matched:
            matched.append(category)
    if matched:
        return matched
    for category in BUDGET_LIMITS:
        parts = [part for part in category.lower().split("/") if len(part) >= 4]
        if any(part in text for part in parts):
            matched.append(category)
    return matched


def is_over_budget(state) -> bool:
    """Conditional edge: route to the alert agent only when budget math says so.

    This calls the same deterministic status the budget tool uses. It does not
    inspect the analysis agent's natural-language reply, which can be rephrased
    without changing the underlying numbers.
    """
    task = str(getattr(state, "task", "") or "")
    month = _month_from_task(task)
    categories = _categories_from_task(task) or list(BUDGET_LIMITS)
    return any(
        (status := get_budget_status(category, month)) is not None and status["over_budget"]
        for category in categories
    )


def build_spending_review_graph():
    builder = GraphBuilder()
    builder.add_node(budget_analysis_agent, "analyze")
    builder.add_node(budget_alert_agent, "alert")
    builder.add_edge("analyze", "alert", condition=is_over_budget)
    builder.set_entry_point("analyze")
    builder.set_max_node_executions(4)
    builder.set_execution_timeout(180)
    return builder.build()


spending_review_graph = build_spending_review_graph()
