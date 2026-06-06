from typing import Annotated
from typing import TypedDict

from langgraph.graph.message import add_messages


class LoanAgentState(TypedDict):
    session_id: str

    messages: Annotated[list, add_messages]

    customer_profile: dict

    active_task: dict | None

    intent: str | None

    plan: dict | None

    validation_result: dict | None

    execution_result: dict | None
