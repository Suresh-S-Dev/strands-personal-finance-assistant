# Personal Finance Assistant

A small [Strands Agents](https://strandsagents.com) project that logs expenses, answers spending and budget questions, and tracks recurring bills. It does not give investment, tax, or debt advice.

Every message goes through the same path in `handle_request`:

1. **Input check** flags prompt-injection phrasing and redacts account-like numbers.
2. **Classifier** picks one request type. Keyword rules run first; the LLM classifier is used only when those rules do not match, and it fails closed to `out_of_scope`.
3. **Agent or graph** handles the request.
4. **Output check** replaces replies that look like investment advice.

| Request type | What happens |
| --- | --- |
| `log_expense` | Expense Logging Agent categorizes the purchase and writes it |
| `spending_question` | Spending review graph analyzes the month, then alerts only if the budget math says the category is over |
| `bill_question` | Bill Tracking Agent looks for recurring bills and can create or list reminders |
| `out_of_scope` | A short refusal. No agent runs |

## Setup

Python 3.13. The default model is a Bedrock model id in `models/model_config.py` (`nvidia.nemotron-nano-3-30b`), so agent calls need AWS credentials that can invoke that model.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Transactions are stored in SQLite (`pfa_transactions.db` by default). Set `PFA_DB_PATH` to use another file. Monthly limits live in `config/settings.py`. Expenses above $200 (`config/thresholds.py`) are refused until the user confirms them. Amounts above $50,000 are blocked even when confirmed.

## Run

CLI, using the two sample spending questions in `main.py`:

```bash
python main.py
```

HTTP API:

```bash
uvicorn api:app --reload
```

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "How much have I spent on Groceries this month?"}'
```

Docker serves the same API on port 8000:

```bash
docker build -t pfa .
docker run --rm -p 8000:8000 pfa
```

Pass AWS credentials into the container if the model call needs them.

Structured logs are written to `logs/pfa.log`. Summarize them with:

```bash
python scripts/summarize_logs.py
```

Tests:

```bash
pytest
```

## Layout

```
main.py                     request entry point
api.py                      POST /chat
classifier/                 keyword rules, then LLM fallback
agents/                     expense, budget analysis, budget alert, bills
orchestrator/               spending review graph (analyze, then alert if over budget)
sub_agents/                 ambiguous category classification and trend commentary
tools/                      transactions, budgets, categories, bills, today's date
guardrails/                 input, output, and large-expense confirmation
hooks/                      logging, tool-call counts, hard amount ceiling
memory/                     SQLite transactions, user profile, session window, retry
mcp_integration/            local reminder server and the client the bill agent uses
config/                     budget limits and the confirmation threshold
models/                     model id and the classification schema
prompts/                    system prompt text, one file per agent
```

Reminders are a local MCP server (`mcp_integration/reminder_server.py`) stored in `mcp_integration/reminders.json`. The bill agent talks to it over stdio. If that server is down, the agent is told to say the reminder system is unreachable rather than claim a reminder was created.

The budget analysis agent keeps a sliding window of the last 10 messages. That window is in-process only. Transactions and the user profile are the durable stores.
