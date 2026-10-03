from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry

from hooks.logging_hooks import _log_event


def _amount(tool_input: dict) -> float:
    try:
        return float(tool_input.get("amount", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


class SecurityHooks(HookProvider):
    """A last-resort sanity ceiling, independent of any business-level
    confirmation logic (that's the large-expense guardrail's job). This
    should never normally fire — it's a backstop against something going
    very wrong upstream.
    """

    HARD_CEILING = 50_000

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        registry.add_callback(BeforeToolCallEvent, self.check_tool_call)

    def check_tool_call(self, event: BeforeToolCallEvent) -> None:
        if event.tool_use["name"] != "add_transaction":
            return
        tool_input = event.tool_use.get("input") or {}
        if not isinstance(tool_input, dict):
            return
        amount = _amount(tool_input)
        if amount > self.HARD_CEILING:
            _log_event("guardrail_violation", guardrail="SecurityHooks", amount=amount)
            event.cancel_tool = (
                f"Blocked: ${amount:,.2f} exceeds the hard safety ceiling of ${self.HARD_CEILING:,.2f}."
            )
