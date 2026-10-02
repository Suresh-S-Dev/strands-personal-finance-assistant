from strands import Agent
from models.model_config import DEFAULT_MODEL
from tools.bill_tools import detect_recurring_bills

SYSTEM_PROMPT = """You are the Bill Tracking Agent.

Help the user understand recurring bills based on transaction history. Call
detect_recurring_bills — never state a due date or pattern the data doesn't support.

You do not log new expenses and you do not answer general budget questions.
You never set up automatic payments — you only inform and remind.
"""

bill_tracking_agent = Agent(
    model=DEFAULT_MODEL,
    system_prompt=SYSTEM_PROMPT,
    tools=[detect_recurring_bills],
)