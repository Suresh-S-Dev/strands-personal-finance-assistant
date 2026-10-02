from datetime import date
from strands import tool

@tool
def get_today() -> str:
    """Get today's actual date, to resolve relative time references like 'this month' or 'today'.

    Returns:
        Today's date (YYYY-MM-DD) and the current month (YYYY-MM).
    """
    today = date.today()
    return f"Today's date is {today.isoformat()}. Current month is {today.strftime('%Y-%m')}."