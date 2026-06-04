from app.langgraph.question_bank import LOAN_KEYWORDS

def detect_loan_by_keyword(text: str) -> bool:
    text = text.lower()
    if any(
        keyword in text
        for keyword in LOAN_KEYWORDS
    ):
        return True 

    return False