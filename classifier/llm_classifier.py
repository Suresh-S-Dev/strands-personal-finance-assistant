from strands import Agent
from strands.types.exceptions import StructuredOutputException

from models.model_config import DEFAULT_MODEL
from models.schemas import ClassificationResult
from prompts import load_prompt

SYSTEM_PROMPT = load_prompt("llm_classifier")

_classifier_agent = Agent(
    model=DEFAULT_MODEL,
    name="llm_classifier",
    system_prompt=SYSTEM_PROMPT,
    callback_handler=None,
)


def llm_classify(message: str) -> ClassificationResult:
    """Classify an ambiguous message using the LLM — only called when rules can't confidently decide."""
    try:
        result = _classifier_agent(message, structured_output_model=ClassificationResult)
        return result.structured_output
    except StructuredOutputException:
        # Fail CLOSED: fall back to out_of_scope (does nothing risky) rather
        # than guessing a specific action-taking agent that might write bad data.
        return ClassificationResult(
            request_type="out_of_scope",
            confidence=0.0,
            reasoning="classification failed — falling back to a safe default",
        )
