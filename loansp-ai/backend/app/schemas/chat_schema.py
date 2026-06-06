from typing import Optional, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    thread_id: str
    processing_time: Optional[float] = None


class LoanUserInfo(BaseModel):
    """
    Structured information collected from the customer
    for loan recommendation.
    """

    language: Optional[Literal["vi", "en"]] = Field(
        default=None,
        description=(
            "Detected language of the latest user message. "
            "Use 'vi' for Vietnamese and 'en' for English. "
            "For mixed-language messages, choose the dominant language."
        ),
    )

    income: Optional[int] = Field(
        default=None,
        description=(
            "User's regular monthly income in VND integer. "
            "Extract only when the user explicitly provides an amount. "
            "Vietnamese units: triệu = 1.000.000, tỷ = 1.000.000.000, nghìn/k = 1.000. "
            "Examples: '15 triệu' → 15000000, '20 triệu/tháng' → 20000000, '500 triệu' → 500000000."
        ),
    )

    asset_value: Optional[int] = Field(
        default=None,
        description=(
            "Total value of collateral or owned assets mentioned by the user, "
            "such as houses, land, apartments, vehicles, savings deposits, "
            "or other valuable assets, converted to VND."
        ),
    )

    loan_purpose: Optional[Literal["mua_nha", "mua_xe", "tieu_dung", "kinh_doanh"]] = (
        Field(
            default=None,
            description=(
                "Purpose of the loan. "
                "Must be classified into exactly one category: "
                "'mua_nha' (home purchase), "
                "'mua_xe' (vehicle purchase), "
                "'tieu_dung' (personal consumption), "
                "'kinh_doanh' (business purposes)."
            ),
        )
    )

    loan_amount: Optional[int] = Field(
        default=None,
        description=("Desired loan amount requested by the user, converted to VND."),
    )

    loan_year: Optional[int] = Field(
        default=None,
        description=(
            "Desired loan term in years. "
            "Extract only if explicitly mentioned. "
            "Examples: "
            "'5 years' -> 5, "
            "'10-year mortgage' -> 10, "
            "'vay trong 15 năm' -> 15."
        ),
    )


class ClassifierLoan(BaseModel):
    intent: bool


class Plan(BaseModel):
    tool: str
    reason: str
