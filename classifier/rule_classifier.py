import re

LOG_EXPENSE_PATTERNS = [r"\bspent\b", r"\bpaid\b", r"\bbought\b", r"\blog\b.*expense"]
BILL_QUESTION_PATTERNS = [r"\bbill\b", r"\bdue\b", r"\brecurring\b", r"\bremind\b"]
SPENDING_QUESTION_PATTERNS = [r"how much", r"\bspending\b", r"\bbudget\b", r"left in"]


def rule_classify(message: str) -> dict | None:
    """Try to classify using fast, free keyword rules.

    Returns a classification dict if a rule confidently matches, or None if the
    message is ambiguous and should be escalated to the LLM classifier. Order
    matters here: check bill-related keywords before generic spending keywords,
    since a message like "is my electric bill too much?" contains both.
    """
    text = message.lower()

    if any(re.search(p, text) for p in LOG_EXPENSE_PATTERNS):
        return {"request_type": "log_expense", "confidence": 0.95, "reasoning": "matched a logging keyword"}
    if any(re.search(p, text) for p in BILL_QUESTION_PATTERNS):
        return {"request_type": "bill_question", "confidence": 0.9, "reasoning": "matched a bill keyword"}
    if any(re.search(p, text) for p in SPENDING_QUESTION_PATTERNS):
        return {"request_type": "spending_question", "confidence": 0.9, "reasoning": "matched a spending keyword"}
    return None  # ambiguous — let the LLM classifier decide