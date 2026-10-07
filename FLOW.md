# Request flow

Every message ends up in `handle_request` in `main.py`. The CLI and the API are only two ways to get there.

```mermaid
flowchart TD
    cli["python main.py"] --> handle["handle_request"]
    api["POST /chat in api.py"] --> handle

    handle --> input["check_input"]
    input --> flags{"Flags set?"}
    flags -->|yes| logFlag["Print the flags. Message still continues."]
    flags -->|no| classify
    logFlag --> classify["classify"]

    classify --> rules{"rule_classify matched?"}
    rules -->|yes| route{"request_type"}
    rules -->|no| llm["llm_classify"]
    llm -->|StructuredOutputException| refuse
    llm -->|classified| route

    route -->|out_of_scope| refuse["Fixed refusal. No agent runs."]
    route -->|log_expense| expense["expense_logging_agent"]
    route -->|bill_question| bills["bill_tracking_agent"]
    route -->|spending_question| review["run_spending_review"]

    expense --> metrics1["log_result_metrics"]
    bills --> metrics2["log_result_metrics"]
    review --> output
    metrics1 --> output["check_output"]
    metrics2 --> output
    refuse --> output
    output --> reply["Return the reply"]
```

`python main.py` calls `handle_request` twice, once for Dining/Coffee this month and once for Groceries this month. `api.py` sends whatever is in the JSON `message` field through the same function and returns `{"response": ...}`.

## 1. Input check

`guardrails/input_guardrails.py` does not stop the request.

- Phrases such as "ignore previous instructions" add the flag `possible_prompt_injection`.
- A 12–19 digit number is replaced with `[REDACTED]` and flagged as `possible_account_number`.
- The sanitized text is what the classifier and agents see.

## 2. Classifier

`classifier/hybrid_classifier.py` tries keyword rules first. The LLM runs only when no rule matches.

```mermaid
flowchart TD
    msg["Sanitized message"] --> log{"spent, paid, bought, or log expense?"}
    log -->|yes| logType["log_expense"]
    log -->|no| bill{"bill, due, recurring, or remind?"}
    bill -->|yes| billType["bill_question"]
    bill -->|no| spend{"how much, spending, budget, or left in?"}
    spend -->|yes| spendType["spending_question"]
    spend -->|no| llm["llm_classifier"]
    llm --> oneOf["One of the four types"]
    llm -->|classification fails| closed["out_of_scope"]
```

Rule order is the order in `classifier/rule_classifier.py`: logging keywords win over bill keywords, and bill keywords win over spending keywords. The LLM classifier reads `prompts/llm_classifier.txt`. If structured output fails, it returns `out_of_scope` and does not guess an agent that can write data.

## 3. Expense logging

`agents/expense_logging_agent.py` loads `prompts/expense_logging.txt`.

```mermaid
flowchart TD
    agent["expense_logging_agent"] --> cat["categorize_expense"]
    cat --> add["add_transaction"]
    add --> amount{"Amount over 200 and not confirmed?"}
    amount -->|yes| ask["LargeExpenseGuardrail refuses the write"]
    amount -->|no| ceiling{"Amount over 50000?"}
    ceiling -->|yes| block["SecurityHooks blocks the write"]
    ceiling -->|no| save["SQLite transactions table"]
    ask --> confirm["User says yes, then add_transaction with confirmed=True"]
    confirm --> ceiling
```

`categorize_expense` uses keyword lookup. If it returns `Uncategorized`, the prompt tells the agent to ask the user. The confirmation line is `CONFIRMATION_THRESHOLD` in `config/thresholds.py`. The $50,000 ceiling is `SecurityHooks.HARD_CEILING`.

## 4. Bill tracking

`agents/bill_tracking_agent.py` loads `prompts/bill_tracking.txt`.

```mermaid
flowchart TD
    agent["bill_tracking_agent"] --> which{"What did the user ask?"}
    which -->|recurring bills| detect["detect_recurring_bills"]
    which -->|set or list a reminder| mcp["calendar MCP client"]
    detect --> history["Read transactions"]
    mcp --> server["reminder_server.py over stdio"]
    server --> file["mcp_integration/reminders.json"]
    server -->|server down| plain["Tell the user the reminder system is unreachable"]
```

The client is created with `continue_on_error=True`, so a dead reminder server does not crash the rest of the request.

## 5. Spending review

`run_spending_review` in `main.py` runs `orchestrator/spending_review_graph.py`.

```mermaid
flowchart TD
    entry["spending_review_graph"] --> analyze["analyze: budget_analysis_agent"]
    analyze --> math{"is_over_budget?"}
    math -->|yes| alert["alert: budget_alert_agent"]
    math -->|no| done["Return the analysis only"]
    alert --> both["Return analysis, then the alert"]
```

`is_over_budget` does not read the analysis sentence. It calls `get_budget_status` for the month and categories found in the user message, using the limits in `config/settings.py`. The alert node runs only when that math says a matched category is over budget. If the message names no category, every limit in `BUDGET_LIMITS` is checked.

The analysis agent loads `prompts/budget_analysis.txt` and can call:

| Tool | Role |
| --- | --- |
| `get_today` | Real date for "this month", "today", or "last month" |
| `query_transactions` | Past spending from SQLite |
| `calculate_budget_remaining` | Remaining budget for a category and month |
| `classify_ambiguous_category` | Category specialist, `prompts/category_classifier.txt` |
| `detect_spending_trend` | Month totals computed in code, then `prompts/trend_anomaly.txt` for the wording |

It also keeps the last 10 messages in memory for that process. That window is not the SQLite database.

The alert agent loads `prompts/budget_alert.txt` and has no tools. It writes one short nudge.

## 6. Output check

`guardrails/output_guardrails.py` runs on every branch, including the refusal. If the reply matches the investment-advice patterns, the user gets a fixed spending-and-budget message instead.

Logs for invocations, tool calls, and guardrail violations go to `logs/pfa.log`. `scripts/summarize_logs.py` prints a one-line summary of that file.
