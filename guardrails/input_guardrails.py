import re

from hooks.logging_hooks import _log_event

INJECTION_PATTERNS = [
    r"ignore (all|your|previous) instructions",
    r"you are now",
    r"system prompt",
    r"disregard (the|your) (rules|guidelines)",
]
ACCOUNT_NUMBER_PATTERN = r"\b\d{12,19}\b"  # crude heuristic for card/account-like numbers


def check_input(message: str) -> dict:
    """Pre-screen a raw user message before it reaches the classifier.

    Flags suspicious content rather than hard-blocking most of it — a
    message merely containing a suspicious phrase isn't necessarily
    malicious, but it should get extra scrutiny downstream. The one thing
    we DO sanitize outright is anything resembling an account/card number,
    since this assistant never has a legitimate reason to need one.
    """
    flags = []
    sanitized = message

    if any(re.search(p, message, re.IGNORECASE) for p in INJECTION_PATTERNS):
        flags.append("possible_prompt_injection")

    if re.search(ACCOUNT_NUMBER_PATTERN, message):
        flags.append("possible_account_number")
        sanitized = re.sub(ACCOUNT_NUMBER_PATTERN, "[REDACTED]", sanitized)

    if flags:
        _log_event("guardrail_violation", guardrail="check_input", flags=flags)

    return {"flags": flags, "sanitized_message": sanitized}
