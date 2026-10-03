import re

from hooks.logging_hooks import _log_event

BANNED_ADVICE_PATTERNS = [
    r"\byou should invest\b",
    r"\bI recommend (buying|selling) (stock|crypto|bitcoin)\b",
]


def check_output(response_text: str) -> str:
    """Final backstop before a response reaches the user. The system prompts
    already forbid investment/tax advice — this is a second, code-level
    check in case that instruction gets bypassed somehow.
    """
    if any(re.search(p, response_text, re.IGNORECASE) for p in BANNED_ADVICE_PATTERNS):
        _log_event("guardrail_violation", guardrail="check_output")
        return "I can help with spending and budgeting, but I'm not able to give investment or tax advice."
    return response_text
