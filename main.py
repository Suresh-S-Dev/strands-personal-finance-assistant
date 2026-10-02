from agents.expense_logging_agent import expense_logging_agent
from agents.budget_analysis_agent import budget_analysis_agent
from agents.bill_tracking_agent import bill_tracking_agent

if __name__ == "__main__":
    print(expense_logging_agent("I spent $12.50 on coffee at Blue Bottle today."))
    print("---")
    print(expense_logging_agent("I spent $45 on groceries at Trader Joe's yesterday."))
    print("---")
    print(budget_analysis_agent("How much have I spent on Dining/Coffee this month?"))
    print("---")
    print(bill_tracking_agent("Do I have any recurring bills yet?"))