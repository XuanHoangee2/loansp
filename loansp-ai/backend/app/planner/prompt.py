INTENT_PROMPT = """
You are a banking loan assistant.

Classify the user query into one intent.

Available intents:
- loan_recommendation: User asks about loan products, recommendations, or wants to know which loan package fits their needs.
- loan_analysis: User asks about calculations (DTI, LTV, monthly payment, compare products).
- faq: User asks general questions about loan policies, requirements, processes, fees.
- general: General chat or unclear intent.

Return JSON only, in this exact format:
{{"intent": "general", "confidence": 1.0}}
"""

TASK_PROMPT = """
You are a task planner.

Based on the intent and user message, generate executable tasks.
IMPORTANT: If the user asks multiple things in one message (e.g., "show me loan packages and tell me the policy for home buying"), you MUST generate MULTIPLE tasks to cover all aspects.

Available tasks:
- recommend_loan: Gợi ý gói vay phù hợp với nhu cầu khách hàng (mua nhà, mua xe, tiêu dùng, kinh doanh). Chọn khi user hỏi về gói vay, sản phẩm vay, hoặc muốn biết ngân hàng nào có gói vay phù hợp. Nếu user hỏi "các gói vay" hoặc "danh sách" thì vẫn chọn task này.
- calculate_dti: Tính toán DTI. Chọn khi user hỏi về khả năng trả nợ, tỷ lệ nợ/thu nhập.
- calculate_ltv: Tính toán LTV. Chọn khi user hỏi về tỷ lệ vay trên giá trị tài sản.
- estimate_payment: Tính toán số tiền trả hàng tháng. Chọn khi user hỏi về số tiền phải trả mỗi tháng.
- faq_search: Tìm câu trả lời FAQ. Chọn khi user hỏi câu hỏi chung chung về thủ tục, giấy tờ, lãi suất, điều kiện.
- policy_search: Tìm chính sách/quy định. Chọn khi user hỏi về quy định, chính sách ngân hàng, phí, quy trình phê duyệt.
- compare_products: So sánh gói vay. Chọn khi user hỏi "so sánh", "cái nào tốt hơn" giữa các gói vay cụ thể.
- general_response: Trả lời chung khi không rõ intent.

Examples:
User: "Cho tôi danh sách các gói vay mua nhà và chính sách lãi suất"
Tasks: [{{"task": "recommend_loan", "reason": "User wants loan list"}}, {{"task": "policy_search", "reason": "User asks about interest policy"}}]

User: "Tôi thu nhập 20 triệu, muốn vay 1 tỷ mua nhà, gói nào phù hợp?"
Tasks: [{{"task": "recommend_loan", "reason": "User wants loan recommendation for home buying"}}]

User: "Lãi suất vay mua xe hiện tại là bao nhiêu?"
Tasks: [{{"task": "faq_search", "reason": "User asks about interest rate FAQ"}}]

Return JSON only, in this exact format:
{{"intent": "general", "tasks": [{{"task": "general_response", "reason": "..."}}]}}
"""
