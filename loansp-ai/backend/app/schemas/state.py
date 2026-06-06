from typing import TypedDict


class LoanState(TypedDict):
    user_message: str

    extracted_info: dict | None

    loan_products: list | None

    plan: dict | None

    final_response: str | None
