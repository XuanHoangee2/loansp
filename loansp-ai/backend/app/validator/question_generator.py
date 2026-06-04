QUESTION_BANK = {

    "income":
        "Thu nhập hàng tháng của anh/chị là bao nhiêu?",

    "monthly_debt":
        "Hiện tại anh/chị đang trả các khoản nợ bao nhiêu mỗi tháng?",

    "loan_amount":
        "Anh/chị dự định vay bao nhiêu?",

    "loan_year":
        "Anh/chị muốn vay trong bao nhiêu năm?",

    "asset_value":
        "Giá trị tài sản đảm bảo khoảng bao nhiêu?",

    "loan_purpose":
        "Mục đích vay vốn của anh/chị là gì?"
}

class QuestionGenerator:

    def build_question(
        self,
        missing_fields: list[str]
    ) -> str:

        questions = []

        for field in missing_fields:

            if field in QUESTION_BANK:
                questions.append(
                    QUESTION_BANK[field]
                )

        return "\n".join(
            f"{idx+1}. {q}"
            for idx, q in enumerate(questions)
        )