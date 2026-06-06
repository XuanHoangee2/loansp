from enum import Enum
from typing import List

from pydantic import BaseModel


class Intent(str, Enum):
    LOAN_RECOMMENDATION = "loan_recommendation"
    LOAN_ANALYSIS = "loan_analysis"
    FAQ = "faq"
    GENERAL = "general"


class IntentResult(BaseModel):
    intent: Intent
    confidence: float = 1.0


class TaskType(str, Enum):
    RECOMMEND_LOAN = "recommend_loan"
    CALCULATE_DTI = "calculate_dti"
    CALCULATE_LTV = "calculate_ltv"
    ESTIMATE_PAYMENT = "estimate_payment"
    FAQ_SEARCH = "faq_search"
    GENERAL_RESPONSE = "general_response"


class PlannedTask(BaseModel):
    task: TaskType
    reason: str


class PlanResult(BaseModel):
    intent: Intent
    tasks: List[PlannedTask] = []
