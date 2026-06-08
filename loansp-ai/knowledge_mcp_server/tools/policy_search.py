from difflib import SequenceMatcher

POLICY_DATA = [
    {
        "category": "interest",
        "title": "Quy định lãi suất vay mua nhà",
        "content": "Lãi suất vay mua nhà áp dụng theo thỏa thuận giữa ngân hàng và khách hàng. Lãi suất ưu đãi áp dụng trong 12-24 tháng đầu, sau đó chuyển sang lãi suất thả nổi theo thị trường.",
    },
    {
        "category": "fee",
        "title": "Phí trả nợ trước hạn",
        "content": "Phí trả nợ trước hạn: 1-3% số tiền trả trước hạn nếu trả trong 1-3 năm đầu. Sau 3 năm không tính phí.",
    },
    {
        "category": "requirement",
        "title": "Yêu cầu thu nhập tối thiểu",
        "content": "Thu nhập tối thiểu phụ thuộc gói vay: mua nhà 10tr/tháng, mua xe 8tr/tháng, tiêu dùng 5tr/tháng, kinh doanh 15tr/tháng.",
    },
    {
        "category": "process",
        "title": "Quy trình xét duyệt vay mua nhà",
        "content": "Bước 1: Nộp hồ sơ. Bước 2: Thẩm định tài sản và thu nhập. Bước 3: Phê duyệt (3-7 ngày). Bước 4: Ký hợp đồng. Bước 5: Giải ngân.",
    },
    {
        "category": "requirement",
        "title": "Yêu cầu độ tuổi",
        "content": "Độ tuổi từ 20-60 tại thời điểm vay. Tuổi cộng thời hạn vay không vượt quá 65.",
    },
    {
        "category": "fee",
        "title": "Phí thẩm định tài sản",
        "content": "Phí thẩm định: 0.1-0.2% giá trị tài sản, tối thiểu 500,000 VNĐ. Khách hàng chịu chi phí.",
    },
    {
        "category": "interest",
        "title": "Lãi suất thả nổi",
        "content": "Lãi suất thả nổi = Lãi suất tham chiếu (VD: SBV rate) + Biên độ (2-4%). Điều chỉnh 6 tháng/lần.",
    },
    {
        "category": "process",
        "title": "Thời gian giải ngân",
        "content": "Thời gian giải ngân từ 7-15 ngày làm việc sau khi hồ sơ đầy đủ. Trường hợp phức tạp có thể kéo dài đến 30 ngày.",
    },
]


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _search(query: str, category: str = None) -> list:
    """Fuzzy + keyword search in policy data."""
    if not query or not query.strip():
        results = POLICY_DATA[:5]
        if category:
            results = [r for r in results if r["category"] == category]
        return results

    query_lower = query.lower().strip()
    results = []
    for item in POLICY_DATA:
        if category and item["category"] != category:
            continue

        t_text = item["title"].lower()
        c_text = item["content"].lower()
        cat_text = item["category"].lower()

        score = 0.0
        score += _similarity(query_lower, t_text) * 3
        score += _similarity(query_lower, c_text) * 2
        score += _similarity(query_lower, cat_text) * 1

        words = [w for w in query_lower.split() if len(w) > 1]
        for word in words:
            if word in t_text:
                score += 1.0
            if word in c_text:
                score += 0.5
            if word in cat_text:
                score += 0.3

        if score > 0.3:
            results.append({"score": score, "item": item})

    results.sort(key=lambda x: x["score"], reverse=True)
    return [r["item"] for r in results[:5]]


def policy_search(query: str, category: str = None) -> dict:
    """
    Tìm chính sách/quy định.

    Args:
        query: Từ khóa tìm kiếm.
        category: Loại chính sách (interest | fee | requirement | process).

    Returns:
        dict: {"policies": list, "effective_date": str, "found": bool}
    """
    policies = _search(query, category)
    if not policies:
        return {
            "policies": [
                {
                    "title": "",
                    "content": "Không tìm thấy chính sách phù hợp trong cơ sở dữ liệu.",
                    "found": False,
                }
            ],
            "effective_date": "2026-01-01",
            "found": False,
        }

    return {
        "policies": [{**p, "found": True} for p in policies],
        "effective_date": "2026-01-01",
        "found": True,
    }
