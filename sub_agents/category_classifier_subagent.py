from strands import Agent, tool
from models.model_config import DEFAULT_MODEL

SYSTEM_PROMPT = """You are a Category Classification Specialist.

Given a merchant name, description, and amount, decide the single best category from:
Dining/Coffee, Dining/Restaurants, Groceries, Utilities, Housing, Electronics,
Shopping, Transportation, Entertainment, Healthcare, Other.

Respond with ONLY the category name — no explanation, no punctuation. If you
genuinely cannot tell, respond with "Other".
"""

_classifier_agent = Agent(model=DEFAULT_MODEL, system_prompt=SYSTEM_PROMPT)


@tool
def classify_ambiguous_category(merchant: str, description: str = "", amount: float = 0.0) -> str:
    """Use a classification specialist to categorize an expense the simple
    keyword lookup (categorize_expense) couldn't handle.

    Args:
        merchant: Merchant name.
        description: Optional extra context about the purchase.
        amount: Dollar amount — occasionally useful context (e.g. a $4 vs. $400 Amazon order).

    Returns:
        A single category name.
    """
    prompt = f"Merchant: {merchant}\nDescription: {description}\nAmount: ${amount:.2f}"
    result = _classifier_agent(prompt)
    return str(result).strip()