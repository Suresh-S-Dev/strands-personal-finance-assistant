from strands import tool

# Simple keyword rules for now — Phase 4 will replace ambiguous cases
# with a real Category Classifier sub-agent instead of hardcoded keywords.
CATEGORY_KEYWORDS = {
    "coffee": "Dining/Coffee",
    "starbucks": "Dining/Coffee",
    "blue bottle": "Dining/Coffee",
    "restaurant": "Dining/Restaurants",
    "grocery": "Groceries",
    "groceries": "Groceries",
    "trader joe": "Groceries",
    "electric": "Utilities",
    "rent": "Housing",
    "laptop": "Electronics",
    "amazon": "Shopping",
}


@tool
def categorize_expense(merchant: str, description: str = "") -> str:
    """Categorize an expense based on merchant name and/or description.

    Args:
        merchant: The merchant or vendor name (e.g. "Blue Bottle", "Trader Joe's").
        description: Optional extra context about the purchase.

    Returns:
        A category string, e.g. "Dining/Coffee" or "Groceries". Returns
        "Uncategorized" if no keyword matches, so the agent knows to ask the user.
    """
    text = f"{merchant} {description}".lower()
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in text:
            return category
    return "Uncategorized"