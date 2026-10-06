from strands import Agent, tool
from models.model_config import DEFAULT_MODEL
from prompts import load_prompt

SYSTEM_PROMPT = load_prompt("category_classifier")

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