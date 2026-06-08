def estimate_payment(
    loan_amount: int, loan_year: int, interest_rate: float = 6.5
) -> dict:
    """
    Tính số tiền trả hàng tháng (PMT) theo lãi suất cố định.

    Args:
        loan_amount: Số tiền vay (VNĐ).
        loan_year: Thời hạn vay (năm).
        interest_rate: Lãi suất %/năm (mặc định 6.5).

    Returns:
        dict: {"monthly_payment": int, "total_interest": int, "schedule": list}
    """
    if loan_amount <= 0 or loan_year <= 0:
        return {
            "monthly_payment": 0,
            "total_interest": 0,
            "schedule": [],
            "error": "Invalid input",
        }

    n = loan_year * 12
    r = interest_rate / 100 / 12

    if r == 0:
        monthly_payment = loan_amount / n
    else:
        monthly_payment = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    total_payment = monthly_payment * n
    total_interest = total_payment - loan_amount

    return {
        "monthly_payment": int(monthly_payment),
        "total_interest": int(total_interest),
        "schedule": [
            {
                "month": i + 1,
                "payment": int(monthly_payment),
                "principal": int(loan_amount / n),
                "interest": int(monthly_payment - loan_amount / n),
            }
            for i in range(min(n, 12))
        ],
    }
