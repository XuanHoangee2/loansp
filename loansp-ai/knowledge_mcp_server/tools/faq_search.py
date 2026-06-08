from difflib import SequenceMatcher

FAQ_DATA = [
    {
        "question": "Lãi suất vay mua nhà hiện tại là bao nhiêu?",
        "answer": "Lãi suất vay mua nhà hiện tại tại VIB là 6.5%/năm, Techcombank là 6.2%/năm. Lãi suất có thể thay đổi theo thời điểm.",
    },
    {
        "question": "Cần chuẩn bị những giấy tờ gì khi vay mua nhà?",
        "answer": "Các giấy tờ cần thiết: CCCD/CMND, Hộ khẩu, Giấy đăng ký kết hôn/Độc thân, Hợp đồng lao động, Sao kê lương 3 tháng gần nhất, Hợp đồng mua bán nhà/đất.",
    },
    {
        "question": "Thời gian giải ngân vay mua nhà là bao lâu?",
        "answer": "Thời gian giải ngân thông thường từ 7-15 ngày làm việc sau khi hồ sơ đầy đủ và được phê duyệt.",
    },
    {
        "question": "Có thể vay mua nhà không có tài sản đảm bảo không?",
        "answer": "Có thể vay không có tài sản đảm bảo với gói vay tiêu dùng, nhưng hạn mức thấp hơn và lãi suất cao hơn (khoảng 10%/năm).",
    },
    {
        "question": "Điều kiện để được vay mua xe ô tô?",
        "answer": "Thu nhập tối thiểu 8 triệu/tháng, có giấy tờ chứng minh thu nhập, tuổi từ 20-60. Có thể dùng chính xe mua làm tài sản đảm bảo.",
    },
    {
        "question": "Có thể trả nợ trước hạn không? Có phí gì không?",
        "answer": "Có thể trả nợ trước hạn. Phí trả nợ trước hạn thường là 1-3% số tiền trả trước hạn tùy thời điểm trong hợp đồng.",
    },
    {
        "question": "DTI là gì? Tại sao quan trọng?",
        "answer": "DTI (Debt-to-Income) là tỷ lệ nợ trên thu nhập. Nếu DTI > 40%, ngân hàng có thể từ chối vay vì lo ngại khả năng trả nợ.",
    },
    {
        "question": "LTV là gì?",
        "answer": "LTV (Loan-to-Value) là tỷ lệ vay trên giá trị tài sản. Thông thường ngân hàng cho vay tối đa 80% giá trị tài sản (LTV = 0.8).",
    },
    {
        "question": "Có thể vay kinh doanh không có tài sản đảm bảo không?",
        "answer": "Có thể, nhưng hạn mức thấp hơn và cần chứng minh doanh thu kinh doanh ổn định từ 6 tháng trở lên.",
    },
    {
        "question": "Thủ tục vay tiêu dùng có đơn giản hơn vay mua nhà không?",
        "answer": "Đúng, vay tiêu dùng có thủ tục đơn giản hơn, không cần tài sản đảm bảo, giải ngân nhanh hơn (1-3 ngày).",
    },
]


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _search(query: str, top_k: int = 3) -> list:
    """Fuzzy + keyword search in FAQ data."""
    if not query or not query.strip():
        return FAQ_DATA[:top_k]

    query_lower = query.lower().strip()
    results = []
    for item in FAQ_DATA:
        q_text = item["question"].lower()
        a_text = item["answer"].lower()

        score = 0.0
        # fuzzy similarity
        score += _similarity(query_lower, q_text) * 3
        score += _similarity(query_lower, a_text) * 2

        # keyword boost
        words = [w for w in query_lower.split() if len(w) > 1]
        for word in words:
            if word in q_text:
                score += 1.0
            if word in a_text:
                score += 0.5

        if score > 0.3:
            results.append({"score": score, "item": item})

    results.sort(key=lambda x: x["score"], reverse=True)
    return [r["item"] for r in results[:top_k]]


def faq_search(query: str, language: str = "vi", top_k: int = 3) -> dict:
    """
    Tìm câu trả lời FAQ.

    Args:
        query: Câu hỏi tìm kiếm.
        language: Ngôn ngữ (vi | en).
        top_k: Số kết quả tối đa.

    Returns:
        dict: {"answers": list, "sources": list, "found": bool}
    """
    answers = _search(query, top_k)
    if not answers:
        return {
            "answers": [
                {
                    "question": "",
                    "answer": "Xin lỗi, không tìm thấy câu trả lời phù hợp trong cơ sở dữ liệu. Vui lòng liên hệ tư vấn viên để được hỗ trợ.",
                    "found": False,
                }
            ],
            "sources": [],
            "found": False,
        }

    return {
        "answers": [{**a, "found": True} for a in answers],
        "sources": ["internal_faq"],
        "found": True,
    }
