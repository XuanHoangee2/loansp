from tools.recommend import recommend_loan, compare_products, _load_products


class TestRecommendLoan:
    def test_recommend_home_loan(self):
        result = recommend_loan(
            income=20000000,
            loan_purpose="mua_nha",
            loan_amount=500000000,
            loan_year=20,
            asset_value=800000000,
        )
        assert result["best_match"] is not None
        assert result["best_match"]["purpose"] == "mua_nha"
        assert len(result["products"]) > 0
        assert "reasoning" in result

    def test_recommend_no_match(self):
        result = recommend_loan(
            income=1000000,
            loan_purpose="mua_nha",
            loan_amount=50000000000,
            loan_year=50,
            asset_value=0,
        )
        assert result["best_match"] is None
        assert len(result["products"]) == 0

    def test_recommend_car_loan(self):
        result = recommend_loan(
            income=15000000,
            loan_purpose="mua_xe",
            loan_amount=800000000,
            loan_year=5,
            asset_value=0,
        )
        assert result["best_match"] is not None
        assert result["best_match"]["purpose"] == "mua_xe"


class TestCompareProducts:
    def test_compare_two_products(self):
        result = compare_products(
            product_ids=["vib-home-001", "tech-home-001"],
            loan_amount=1000000000,
            loan_year=20,
        )
        assert len(result["comparison"]) == 2
        assert "recommendation" in result

    def test_compare_invalid_product(self):
        result = compare_products(
            product_ids=["invalid-id"],
            loan_amount=1000000000,
            loan_year=20,
        )
        assert len(result["comparison"]) == 0

    def test_compare_finds_best_rate(self):
        result = compare_products(
            product_ids=["vib-home-001", "tech-home-001"],
            loan_amount=1000000000,
            loan_year=20,
        )
        best = min(result["comparison"], key=lambda x: x["total_interest"])
        assert best["rate"] == 6.2  # tech-home-001 has lower rate


class TestLoadProducts:
    def test_load_products(self):
        products = _load_products()
        assert len(products) >= 6
        assert all("id" in p and "bank" in p for p in products)
