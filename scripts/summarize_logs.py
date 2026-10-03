"""Print a one-line summary of structured PFA logs.

This is a minimal stand-in for a production dashboard: total invocations,
tool calls, guardrail violations, and average invocation duration.
"""
import json
import os
import sys

DEFAULT_LOG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "pfa.log")


def summarize(path: str) -> str:
    invocations = 0
    tool_calls = 0
    violations = 0
    durations = []

    with open(path) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            event = record.get("event")
            if event == "invocation_end":
                invocations += 1
                if "duration_seconds" in record:
                    durations.append(record["duration_seconds"])
            elif event == "tool_start":
                tool_calls += 1
            elif event == "guardrail_violation":
                violations += 1

    average = sum(durations) / len(durations) if durations else 0.0
    return (
        f"{invocations} invocations, {tool_calls} tool calls, "
        f"{violations} guardrail violations, average duration {average:.2f}s"
    )


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LOG
    print(summarize(path))


if __name__ == "__main__":
    main()
