from classifier.rule_classifier import rule_classify
from classifier.llm_classifier import llm_classify
from models.schemas import ClassificationResult


def classify(message: str) -> ClassificationResult:
    """Classify a user message: fast rules first, LLM fallback only when ambiguous."""
    rule_result = rule_classify(message)
    if rule_result is not None:
        return ClassificationResult(**rule_result)
    return llm_classify(message)