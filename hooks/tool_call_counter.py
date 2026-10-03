from strands.hooks import (
    AfterInvocationEvent,
    AfterToolCallEvent,
    BeforeInvocationEvent,
    HookProvider,
    HookRegistry,
)

from hooks.logging_hooks import _log_event, _request_state


class ToolCallCounterHook(HookProvider):
    """Counts tool calls in one invocation and records a one-line summary."""

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        registry.add_callback(BeforeInvocationEvent, self.on_invocation_start)
        registry.add_callback(AfterToolCallEvent, self.on_tool_end)
        registry.add_callback(AfterInvocationEvent, self.on_invocation_end)

    def on_invocation_start(self, event: BeforeInvocationEvent) -> None:
        _request_state(event)["tool_call_count"] = 0

    def on_tool_end(self, event: AfterToolCallEvent) -> None:
        state = _request_state(event)
        state["tool_call_count"] = state.get("tool_call_count", 0) + 1

    def on_invocation_end(self, event: AfterInvocationEvent) -> None:
        count = _request_state(event).get("tool_call_count", 0)
        _log_event(
            "tool_call_summary",
            agent=event.agent.name,
            tool_calls=count,
            summary=f"{count} tool calls in this invocation",
        )
