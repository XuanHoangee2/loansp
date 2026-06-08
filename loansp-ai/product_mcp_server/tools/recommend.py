import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "products.json"


def _load_products():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _score_product(product, income, loan_amount, loan_year, loan_purpose, asset_value):
    """Score a product based on customer profile."""
    score = 0
    reasons = []

    # Purpose match
    if product["purpose"] == loan_purpose:
        score += 50
        reasons.append("PhÃ¹ há»£p má»¥c Ä‘Ã­ch vay")
    else:
        score -= 30

    # Income check
    if income >= product["min_income"]:
        score += 20
    else:
        score -= 40
        reasons.append(
            f"Thu nháº­p tháº¥p hÆ¡n yÃªu cáº§u tá»‘i thiá»ƒu {product['min_income']:,} VNÄ"
        )

    # Amount check
    if loan_amount <= product["max_amount"]:
        score += 15
    else:
        score -= 20
        reasons.append(
            f"Sá»‘ tiá»n vay vÆ°á»£t ngÆ°á»¡ng {product['max_amount']:,} VNÄ"
        )

    # Year check
    if loan_year <= product["max_year"]:
        score += 10
    else:
        score -= 10

    # LTV check (if asset_value provided)
    if asset_value and asset_value > 0:
        ltv = loan_amount / asset_value
        if ltv <= product["ltv_limit"]:
            score += 10
        else:
            score -= 15
            reasons.append(f"LTV vÆ°á»£t ngÆ°á»¡ng {product['ltv_limit'] * 100:.0f}%")

    # Interest rate preference (lower is better)
    score += max(0, 15 - product["interest_rate"])

    return score, reasons


def recommend_loan(
    income: int,
    loan_purpose: str,
    loan_amount: int,
    loan_year: int,
    asset_value: int = 0,
) -> dict:
    """
    Gá»£i Ã½ gÃ³i vay phÃ¹ há»£p dá»±a trÃªn há»“ sÆ¡ khÃ¡ch hÃ ng.

    Args:
        income: Thu nháº­p hÃ ng thÃ¡ng (VNÄ).
        loan_purpose: Má»¥c Ä‘Ã­ch vay (mua_nha | mua_xe | tieu_dung | kinh_doanh).
        loan_amount: Sá»‘ tiá»n vay dá»± kiáº¿n (VNÄ).
        loan_year: Thá»i háº¡n vay (nÄƒm).
        asset_value: GiÃ¡ trá»‹ tÃ i sáº£n Ä‘áº£m báº£o (VNÄ), optional.

    Returns:
        dict: {"products": list, "best_match": dict, "reasoning": str}
    """
    products = _load_products()
    scored = []

    for p in products:
        s, reasons = _score_product(
            p, income, loan_amount, loan_year, loan_purpose, asset_value
        )
        scored.append({"product": p, "score": s, "reasons": reasons})

    scored.sort(key=lambda x: x["score"], reverse=True)
    top_products = scored[:3]

    if not top_products:
        return {
            "products": [],
            "best_match": None,
            "reasoning": "Không tìm thấy gói vay phù hợp với hồ sơ hiện tại.",
        }

    best = top_products[0]["product"]
    reasoning = (
        f"Gói vay phù hợp nhất: {best['name']} tại {best['bank']} "
        f"với lãi suất {best['interest_rate']}%/năm, "
        f"hỗ trợ vay đến {best['max_amount']:,} VNĐ trong {best['max_year']} năm."
    )

    return {
        "products": [p["product"] for p in top_products],
        "best_match": best,
        "reasoning": reasoning,
    }

    best = top_products[0]["product"]
    reasoning = (
        f"GÃ³i vay phÃ¹ há»£p nháº¥t: {best['name']} táº¡i {best['bank']} "
        f"vá»›i lÃ£i suáº¥t {best['interest_rate']}%/nÄƒm, "
        f"há»— trá»£ vay Ä‘áº¿n {best['max_amount']:,} VNÄ trong {best['max_year']} nÄƒm."
    )

    return {
        "products": [p["product"] for p in top_products],
        "best_match": best,
        "reasoning": reasoning,
    }


def compare_products(product_ids: list, loan_amount: int, loan_year: int) -> dict:
    """
    So sÃ¡nh cÃ¡c gÃ³i vay cá»¥ thá»ƒ.

    Args:
        product_ids: Danh sÃ¡ch ID sáº£n pháº©m.
        loan_amount: Sá»‘ tiá»n vay (VNÄ).
        loan_year: Thá»i háº¡n vay (nÄƒm).

    Returns:
        dict: {"comparison": list, "recommendation": str}
    """
    products = _load_products()
    product_map = {p["id"]: p for p in products}

    comparison = []
    for pid in product_ids:
        p = product_map.get(pid)
        if not p:
            continue

        n = loan_year * 12
        r = p["interest_rate"] / 100 / 12
        if r == 0:
            monthly = loan_amount / n
        else:
            monthly = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

        total_interest = monthly * n - loan_amount
        comparison.append(
            {
                "id": p["id"],
                "bank": p["bank"],
                "name": p["name"],
                "rate": p["interest_rate"],
                "monthly_payment": int(monthly),
                "total_interest": int(total_interest),
                "max_amount": p["max_amount"],
                "max_year": p["max_year"],
            }
        )

    if not comparison:
        return {
            "comparison": [],
            "recommendation": "KhÃ´ng tÃ¬m tháº¥y sáº£n pháº©m Ä‘á»ƒ so sÃ¡nh.",
        }

    best = min(comparison, key=lambda x: x["total_interest"])
    recommendation = (
        f"GÃ³i vay tiáº¿t kiá»‡m nháº¥t: {best['name']} táº¡i {best['bank']} "
        f"vá»›i tá»•ng lÃ£i {best['total_interest']:,} VNÄ."
    )

    return {"comparison": comparison, "recommendation": recommendation}
