from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry

from config.thresholds import CONFIRMATION_THRESHOLD
from hooks.logging_hooks import _log_event


def _amount(tool_input: dict) -> float:
    try:
        return float(tool_input.get("amount", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _is_confirmed(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1"}
    return bool(value)


class LargeExpenseGuardrail(HookProvider):
    """Enforces confirmation for large expenses at the tool-invocation level —
    not just via prompting. Even if the model 'forgets' to ask, this refuses
    the write outright.
    """

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        registry.add_callback(BeforeToolCallEvent, self.check_confirmation)

    def check_confirmation(self, event: BeforeToolCallEvent) -> None:
        if event.cancel_tool:
            return
        if event.tool_use["name"] != "add_transaction":
            return
        tool_input = event.tool_use.get("input") or {}
        if not isinstance(tool_input, dict):
            return
        amount = _amount(tool_input)
        confirmed = _is_confirmed(tool_input.get("confirmed", False))
        if amount > CONFIRMATION_THRESHOLD and not confirmed:
            _log_event("guardrail_violation", guardrail="LargeExpenseGuardrail", amount=amount)
            event.cancel_tool = (
                f"This expense (${amount:.2f}) is above the ${CONFIRMATION_THRESHOLD} "
                "confirmation threshold. Ask the user to confirm, then call "
                "add_transaction again with confirmed=True."
            )
