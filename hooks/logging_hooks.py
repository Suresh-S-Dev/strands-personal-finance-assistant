import json
import logging
import os
import time

from strands.hooks import (
    AfterInvocationEvent,
    AfterToolCallEvent,
    BeforeInvocationEvent,
    BeforeToolCallEvent,
    HookProvider,
    HookRegistry,
)

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "pfa.log")

logger = logging.getLogger("pfa")


def _configure_logger() -> None:
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter("%(message)s")

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


_configure_logger()


def _request_state(event) -> dict:
    """Per-invocation dict shared by Before/After events for one agent call.

    The current Strands SDK keeps this on ``invocation_state['request_state']``
    rather than a ``request_state`` attribute on the event itself.
    """
    invocation_state = event.invocation_state
    if invocation_state is None:
        return {}
    return invocation_state.setdefault("request_state", {})


def _log_event(event_type: str, **fields) -> None:
    record = {"event": event_type, "timestamp": time.time(), **fields}
    logger.info(json.dumps(record))


def log_result_metrics(agent_name: str, result) -> None:
    """Record token/latency metrics when the SDK exposes them.

    Checks ``metrics`` first, then ``accumulated_metrics`` (graph results).
    Missing attributes are logged as unavailable so an SDK change cannot
    crash the request.
    """
    metrics = getattr(result, "metrics", None)
    if metrics is None:
        metrics = getattr(result, "accumulated_metrics", None)
    if metrics is not None:
        _log_event("invocation_metrics", agent=agent_name, metrics=str(metrics))
    else:
        _log_event("invocation_metrics_unavailable", agent=agent_name)


class LoggingHooks(HookProvider):
    """Logs every agent invocation and every tool call as one JSON object."""

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        registry.add_callback(BeforeInvocationEvent, self.on_invocation_start)
        registry.add_callback(AfterInvocationEvent, self.on_invocation_end)
        registry.add_callback(BeforeToolCallEvent, self.on_tool_start)
        registry.add_callback(AfterToolCallEvent, self.on_tool_end)

    def on_invocation_start(self, event: BeforeInvocationEvent) -> None:
        _request_state(event)["start_time"] = time.time()
        _log_event("invocation_start", agent=event.agent.name)

    def on_invocation_end(self, event: AfterInvocationEvent) -> None:
        started = _request_state(event).get("start_time", time.time())
        duration = time.time() - started
        _log_event(
            "invocation_end",
            agent=event.agent.name,
            duration_seconds=round(duration, 3),
        )

    def on_tool_start(self, event: BeforeToolCallEvent) -> None:
        _log_event("tool_start", agent=event.agent.name, tool=event.tool_use["name"])

    def on_tool_end(self, event: AfterToolCallEvent) -> None:
        _log_event("tool_end", agent=event.agent.name, tool=event.tool_use["name"])
