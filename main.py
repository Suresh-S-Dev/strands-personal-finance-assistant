from agents.bill_tracking_agent import bill_tracking_agent
from agents.expense_logging_agent import expense_logging_agent
from classifier.hybrid_classifier import classify
from guardrails.input_guardrails import check_input
from guardrails.output_guardrails import check_output
from hooks.logging_hooks import log_result_metrics
from orchestrator.spending_review_graph import spending_review_graph


def run_spending_review(message: str) -> str:
    graph_result = spending_review_graph(message)
    log_result_metrics("spending_review_graph", graph_result)
    analysis_text = str(graph_result.results["analyze"].result)
    if "alert" in graph_result.results:
        alert_text = str(graph_result.results["alert"].result)
        return f"{analysis_text}\n\n{alert_text}"
    return analysis_text


def handle_request(message: str) -> str:
    input_check = check_input(message)
    message = input_check["sanitized_message"]
    if input_check["flags"]:
        print(f"[guardrail] input flags: {input_check['flags']}")

    result = classify(message)
    print(f"[classifier] type={result.request_type} confidence={result.confidence} ({result.reasoning})")

    if result.request_type == "out_of_scope":
        raw_response = "I can help you log expenses, check your spending/budget, and track bills — but I can't help with that."
    elif result.request_type == "log_expense":
        agent_result = expense_logging_agent(message)
        log_result_metrics("expense_logging_agent", agent_result)
        raw_response = str(agent_result)
    elif result.request_type == "bill_question":
        agent_result = bill_tracking_agent(message)
        log_result_metrics("bill_tracking_agent", agent_result)
        raw_response = str(agent_result)
    elif result.request_type == "spending_question":
        raw_response = run_spending_review(message)
    else:
        raise ValueError(f"Unhandled request_type: {result.request_type}")

    return check_output(raw_response)


if __name__ == "__main__":
    print(handle_request("How much have I spent on Dining/Coffee this month?"))
    print("---")
    print(handle_request("How much have I spent on Groceries this month?"))
