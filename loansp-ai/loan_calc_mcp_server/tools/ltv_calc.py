def calculate_ltv(loan_amount: int, asset_value: int) -> dict:
    """
    Tính Loan-to-Value ratio (LTV).

    Args:
        loan_amount: Số tiền vay (VNĐ).
        asset_value: Giá trị tài sản đảm bảo (VNĐ).

    Returns:
        dict: {"ltv": float, "status": str, "max_allowed": float}
    """
    if asset_value <= 0:
        return {
            "ltv": 0.0,
            "status": "invalid",
            "max_allowed": 0.8,
            "error": "Asset value must be > 0",
        }

    ltv = loan_amount / asset_value
    max_allowed = 0.8
    if ltv <= max_allowed:
        status = "eligible"
    elif ltv <= 0.9:
        status = "review"
    else:
        status = "rejected"

    return {"ltv": round(ltv, 4), "status": status, "max_allowed": max_allowed}
