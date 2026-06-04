from typing import Optional

from pydantic import BaseModel


class ActiveTask(BaseModel):

    task: str

    status: str = "waiting"

    missing_fields: list[str] = []


class CustomerProfile(BaseModel):

    income: Optional[int] = None

    monthly_debt: Optional[int] = None

    asset_value: Optional[int] = None

    loan_amount: Optional[int] = None

    loan_year: Optional[int] = None

    loan_purpose: Optional[str] = None

    language: str = "vi"