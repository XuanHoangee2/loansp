def calculate_dti(
    income: int, monthly_debt: int, loan_amount: int, loan_year: int
) -> dict:
    """
    Tính Debt-to-Income ratio (DTI).

    Args:
        income: Thu nhập hàng tháng (VNĐ).
        monthly_debt: Nợ trả hàng tháng hiện tại (VNĐ).
        loan_amount: Số tiền vay dự kiến (VNĐ).
        loan_year: Thời hạn vay (năm).

    Returns:
        dict: {"dti": float, "status": str, "max_allowed": float}
    """
    if income <= 0:
        return {
            "dti": 0.0,
            "status": "invalid",
            "max_allowed": 0.4,
            "error": "Income must be > 0",
        }
    if loan_year <= 0:
        return {
            "dti": 0.0,
            "status": "invalid",
            "max_allowed": 0.4,
            "error": "Loan year must be > 0",
        }

    monthly_income = income
    monthly_payment = loan_amount / (loan_year * 12)
    total_monthly_debt = monthly_debt + monthly_payment
    dti = total_monthly_debt / monthly_income

    max_allowed = 0.4
    if dti <= max_allowed:
        status = "eligible"
    elif dti <= 0.5:
        status = "review"
    else:
        status = "rejected"

    return {"dti": round(dti, 4), "status": status, "max_allowed": max_allowed}
