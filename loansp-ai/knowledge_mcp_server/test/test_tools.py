from tools.faq_search import faq_search
from tools.policy_search import policy_search


class TestFAQSearch:
    def test_search_interest_rate(self):
        result = faq_search(query="lãi suất", language="vi", top_k=3)
        assert len(result["answers"]) > 0
        assert (
            "6.5" in result["answers"][0]["answer"]
            or "6.2" in result["answers"][0]["answer"]
        )

    def test_search_documents(self):
        result = faq_search(
            query="CCCD", language="vi", top_k=3
        )
        assert len(result["answers"]) > 0
        assert "CCCD" in result["answers"][0]["answer"]

    def test_search_no_match(self):
        result = faq_search(query="xyzqwerty12345 nonsense", language="vi", top_k=3)
        assert len(result["answers"]) == 1
        assert "không tìm thấy" in result["answers"][0]["answer"].lower()

    def test_search_dti(self):
        result = faq_search(query="Debt-to-Income", language="vi", top_k=3)
        assert len(result["answers"]) > 0
        assert any("Debt-to-Income" in a["answer"] for a in result["answers"])


class TestPolicySearch:
    def test_search_interest_policy(self):
        result = policy_search(query="lãi suất", category="interest")
        assert len(result["policies"]) > 0
        assert result["policies"][0]["category"] == "interest"

    def test_search_fee_policy(self):
        result = policy_search(query="phí", category="fee")
        assert len(result["policies"]) > 0

    def test_search_no_category(self):
        result = policy_search(query="giải ngân")
        assert len(result["policies"]) > 0

    def test_search_no_match(self):
        result = policy_search(query="xyzqwerty12345 nonsense")
        assert len(result["policies"]) == 1
        assert "không tìm thấy" in result["policies"][0]["content"].lower()

    def test_search_process(self):
        result = policy_search(query="quy trình", category="process")
        assert len(result["policies"]) > 0
        assert "Bước 1" in result["policies"][0]["content"]
