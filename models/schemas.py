from typing import Literal
from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    """The classification decision for an incoming user request."""

    request_type: Literal["log_expense", "spending_question", "bill_question", "out_of_scope"] = Field(
        description="Which category this request falls into"
    )
    confidence: float = Field(description="Confidence from 0.0 to 1.0")
    reasoning: str = Field(description="One short sentence explaining the decision")
