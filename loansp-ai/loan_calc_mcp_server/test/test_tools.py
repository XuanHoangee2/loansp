from tools.dti_calc import calculate_dti
from tools.ltv_calc import calculate_ltv
from tools.payment_calc import estimate_payment


class TestCalculateDTI:
    def test_valid_dti_eligible(self):
        result = calculate_dti(
            income=30000000, monthly_debt=0, loan_amount=500000000, loan_year=20
        )
        assert result["status"] == "eligible"
        assert 0 < result["dti"] < 0.4
        assert result["max_allowed"] == 0.4

    def test_valid_dti_review(self):
        result = calculate_dti(
            income=10000000, monthly_debt=2000000, loan_amount=300000000, loan_year=10
        )
        assert result["status"] == "review"
        assert result["dti"] > 0.4

    def test_invalid_income_zero(self):
        result = calculate_dti(
            income=0, monthly_debt=0, loan_amount=100000000, loan_year=5
        )
        assert result["status"] == "invalid"
        assert "error" in result

    def test_invalid_loan_year_zero(self):
        result = calculate_dti(
            income=15000000, monthly_debt=0, loan_amount=100000000, loan_year=0
        )
        assert result["status"] == "invalid"
        assert "error" in result

    def test_high_dti_rejected(self):
        result = calculate_dti(
            income=5000000, monthly_debt=3000000, loan_amount=1000000000, loan_year=5
        )
        assert result["status"] == "rejected"
        assert result["dti"] > 0.5


class TestCalculateLTV:
    def test_valid_ltv_eligible(self):
        result = calculate_ltv(loan_amount=800000000, asset_value=1000000000)
        assert result["status"] == "eligible"
        assert result["ltv"] == 0.8
        assert result["max_allowed"] == 0.8

    def test_valid_ltv_review(self):
        result = calculate_ltv(loan_amount=850000000, asset_value=1000000000)
        assert result["status"] == "review"
        assert 0.8 < result["ltv"] <= 0.9

    def test_invalid_asset_zero(self):
        result = calculate_ltv(loan_amount=100000000, asset_value=0)
        assert result["status"] == "invalid"
        assert "error" in result

    def test_ltv_rejected(self):
        result = calculate_ltv(loan_amount=950000000, asset_value=1000000000)
        assert result["status"] == "rejected"
        assert result["ltv"] > 0.9


class TestEstimatePayment:
    def test_valid_payment(self):
        result = estimate_payment(
            loan_amount=1000000000, loan_year=20, interest_rate=6.5
        )
        assert result["monthly_payment"] > 0
        assert result["total_interest"] > 0
        assert len(result["schedule"]) == 12  # 12 months

    def test_zero_interest(self):
        result = estimate_payment(loan_amount=1200000000, loan_year=10, interest_rate=0)
        assert result["monthly_payment"] == 10000000

    def test_invalid_input(self):
        result = estimate_payment(loan_amount=0, loan_year=10, interest_rate=6.5)
        assert "error" in result
        assert result["monthly_payment"] == 0
