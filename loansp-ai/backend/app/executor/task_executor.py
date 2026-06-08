import json
from typing import Any, Dict

from app.executor.models import ExecutionResult
from app.core.logging.log import logger


class TaskExecutor:
    def __init__(self, router, mcp_client):
        self.router = router
        self.mcp_client = mcp_client

    def _build_arguments(self, tool: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Ánh xạ customer_profile thành arguments cho từng tool."""
        if tool == "calculate_dti":
            return {
                "income": profile.get("income", 0),
                "monthly_debt": profile.get("monthly_debt", 0),
                "loan_amount": profile.get("loan_amount", 0),
                "loan_year": profile.get("loan_year", 1),
            }
        elif tool == "calculate_ltv":
            return {
                "asset_value": profile.get("asset_value", 0),
                "loan_amount": profile.get("loan_amount", 0),
            }
        elif tool == "estimate_payment":
            return {
                "loan_amount": profile.get("loan_amount", 0),
                "loan_year": profile.get("loan_year", 1),
                "interest_rate": 6.5,
            }
        elif tool == "recommend_loan":
            return {
                "income": profile.get("income", 0),
                "loan_purpose": profile.get("loan_purpose", ""),
                "loan_amount": profile.get("loan_amount", 0),
                "loan_year": profile.get("loan_year", 1),
                "asset_value": profile.get("asset_value", 0),
            }
        elif tool == "compare_products":
            return {
                "product_ids": profile.get("product_ids", []),
                "loan_amount": profile.get("loan_amount", 0),
                "loan_year": profile.get("loan_year", 1),
            }
        elif tool in ("faq_search", "policy_search"):
            query = profile.get("last_query", "")
            if not query:
                logger.warning(
                    f"last_query is empty for {tool}; profile keys: {list(profile.keys())}"
                )
            return {"query": query, "language": profile.get("language", "vi")}
        return {}

    def _parse_mcp_result(self, result: Any) -> Dict[str, Any]:
        """Trích xuất dữ liệu từ kết quả MCP call_tool."""
        if hasattr(result, "content") and result.content:
            content = result.content[0]
            if hasattr(content, "text"):
                try:
                    return json.loads(content.text)
                except json.JSONDecodeError:
                    return {"text": content.text}
        return {"raw": str(result)}

    async def execute(self, task_name: str, customer_profile: dict) -> ExecutionResult:
        # Local tasks that don't need MCP
        if task_name == "general_response":
            return ExecutionResult(
                task=task_name,
                success=True,
                data={
                    "response": "Tôi hiểu. Bạn có thể cho tôi biết thêm về nhu cầu vay vốn của mình không?"
                },
            )

        try:
            route = self.router.resolve(task_name)
            server = route["mcp"]
            tool = route["tool"]

            # Nếu server không kết nối được, fallback sang local
            if server not in getattr(self.mcp_client, "sessions", {}):
                return await self._fallback_local(task_name, customer_profile)

            arguments = self._build_arguments(tool, customer_profile)
            logger.info(f"Task '{task_name}' arguments: {arguments}")
            mcp_result = await self.mcp_client.call_tool(server, tool, arguments)
            data = self._parse_mcp_result(mcp_result)
            logger.info(f"Task '{task_name}' raw data: {data}")
            return ExecutionResult(task=task_name, success=True, data=data)
        except Exception as e:
            logger.error(f"Task '{task_name}' failed: {e}")
            return ExecutionResult(task=task_name, success=False, error=str(e))

    async def _fallback_local(self, task_name: str, profile: dict) -> ExecutionResult:
        """Xử lý local khi MCP server không khả dụng."""
        if task_name == "calculate_dti":
            income = profile.get("income", 0)
            monthly_debt = profile.get("monthly_debt", 0)
            loan_amount = profile.get("loan_amount", 0)
            loan_year = profile.get("loan_year", 1)
            monthly_income = income / 12 if income else 0
            monthly_payment = loan_amount / (loan_year * 12) if loan_amount else 0
            total_monthly_debt = monthly_debt + monthly_payment
            dti = total_monthly_debt / monthly_income if monthly_income else 0
            return ExecutionResult(
                task=task_name, success=True, data={"dti": round(dti, 4)}
            )

        elif task_name == "calculate_ltv":
            asset = profile.get("asset_value", 1)
            loan = profile.get("loan_amount", 0)
            ltv = loan / asset if asset else 0
            return ExecutionResult(
                task=task_name, success=True, data={"ltv": round(ltv, 4)}
            )

        elif task_name == "estimate_payment":
            P = profile.get("loan_amount", 0)
            n = profile.get("loan_year", 1) * 12
            r = 6.5 / 100 / 12
            if P <= 0 or n <= 0:
                return ExecutionResult(
                    task=task_name,
                    success=True,
                    data={"monthly_payment": 0, "total_interest": 0},
                )
            pmt = P * (r * (1 + r) ** n) / ((1 + r) ** n - 1) if r else P / n
            total_interest = pmt * n - P
            return ExecutionResult(
                task=task_name,
                success=True,
                data={
                    "monthly_payment": int(pmt),
                    "total_interest": int(total_interest),
                },
            )

        elif task_name == "recommend_loan":
            # Fallback local product recommendation
            _LOCAL_PRODUCTS = [
                {
                    "id": "vib-home-001",
                    "bank": "VIB",
                    "name": "VIB Home Loan",
                    "purpose": "mua_nha",
                    "min_income": 10000000,
                    "max_amount": 10000000000,
                    "max_year": 25,
                    "interest_rate": 6.5,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua nhà/đất với lãi suất ưu đãi 6.5%/năm, thời hạn đến 25 năm.",
                },
                {
                    "id": "vib-car-001",
                    "bank": "VIB",
                    "name": "VIB Car Loan",
                    "purpose": "mua_xe",
                    "min_income": 8000000,
                    "max_amount": 2000000000,
                    "max_year": 7,
                    "interest_rate": 7.5,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua ô tô/xe máy với lãi suất 7.5%/năm, thời hạn đến 7 năm.",
                },
                {
                    "id": "vib-consumer-001",
                    "bank": "VIB",
                    "name": "VIB Consumer Loan",
                    "purpose": "tieu_dung",
                    "min_income": 5000000,
                    "max_amount": 500000000,
                    "max_year": 5,
                    "interest_rate": 10.0,
                    "ltv_limit": 0.0,
                    "dti_limit": 0.5,
                    "description": "Vay tiêu dùng không tài sản đảm bảo, lãi suất 10%/năm.",
                },
                {
                    "id": "vib-biz-001",
                    "bank": "VIB",
                    "name": "VIB Business Loan",
                    "purpose": "kinh_doanh",
                    "min_income": 15000000,
                    "max_amount": 5000000000,
                    "max_year": 10,
                    "interest_rate": 8.0,
                    "ltv_limit": 0.7,
                    "dti_limit": 0.45,
                    "description": "Vay kinh doanh với lãi suất 8%/năm, thời hạn đến 10 năm.",
                },
                {
                    "id": "tech-home-001",
                    "bank": "Techcombank",
                    "name": "Techcombank Home Loan",
                    "purpose": "mua_nha",
                    "min_income": 12000000,
                    "max_amount": 15000000000,
                    "max_year": 30,
                    "interest_rate": 6.2,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua nhà với lãi suất ưu đãi 6.2%/năm, thời hạn đến 30 năm.",
                },
                {
                    "id": "tech-biz-001",
                    "bank": "Techcombank",
                    "name": "Techcombank SME Loan",
                    "purpose": "kinh_doanh",
                    "min_income": 20000000,
                    "max_amount": 10000000000,
                    "max_year": 10,
                    "interest_rate": 7.5,
                    "ltv_limit": 0.7,
                    "dti_limit": 0.45,
                    "description": "Vay kinh doanh SME với lãi suất 7.5%/năm, thời hạn đến 10 năm.",
                },
                {
                    "id": "tech-car-001",
                    "bank": "Techcombank",
                    "name": "Techcombank Auto Loan",
                    "purpose": "mua_xe",
                    "min_income": 10000000,
                    "max_amount": 3000000000,
                    "max_year": 8,
                    "interest_rate": 6.8,
                    "ltv_limit": 0.85,
                    "dti_limit": 0.4,
                    "description": "Vay mua ô tô lãi suất 6.8%/năm, thời hạn đến 8 năm, LTV lên đến 85%.",
                },
                {
                    "id": "vcb-home-001",
                    "bank": "Vietcombank",
                    "name": "Vietcombank Home Plus",
                    "purpose": "mua_nha",
                    "min_income": 15000000,
                    "max_amount": 20000000000,
                    "max_year": 25,
                    "interest_rate": 6.0,
                    "ltv_limit": 0.75,
                    "dti_limit": 0.4,
                    "description": "Vay mua nhà lãi suất 6.0%/năm, thời hạn đến 25 năm, hạn mức lên đến 20 tỷ.",
                },
                {
                    "id": "vcb-car-001",
                    "bank": "Vietcombank",
                    "name": "Vietcombank Auto Plus",
                    "purpose": "mua_xe",
                    "min_income": 12000000,
                    "max_amount": 2500000000,
                    "max_year": 7,
                    "interest_rate": 7.0,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua ô tô lãi suất 7.0%/năm, thời hạn đến 7 năm.",
                },
                {
                    "id": "vcb-consumer-001",
                    "bank": "Vietcombank",
                    "name": "Vietcombank Cash Plus",
                    "purpose": "tieu_dung",
                    "min_income": 7000000,
                    "max_amount": 300000000,
                    "max_year": 4,
                    "interest_rate": 9.5,
                    "ltv_limit": 0.0,
                    "dti_limit": 0.5,
                    "description": "Vay tiêu dùng không tài sản đảm bảo, lãi suất 9.5%/năm.",
                },
                {
                    "id": "vcb-biz-001",
                    "bank": "Vietcombank",
                    "name": "Vietcombank Business Pro",
                    "purpose": "kinh_doanh",
                    "min_income": 25000000,
                    "max_amount": 15000000000,
                    "max_year": 12,
                    "interest_rate": 7.2,
                    "ltv_limit": 0.75,
                    "dti_limit": 0.45,
                    "description": "Vay kinh doanh lãi suất 7.2%/năm, thời hạn đến 12 năm.",
                },
                {
                    "id": "acb-home-001",
                    "bank": "ACB",
                    "name": "ACB Dream Home",
                    "purpose": "mua_nha",
                    "min_income": 10000000,
                    "max_amount": 12000000000,
                    "max_year": 20,
                    "interest_rate": 6.8,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua nhà lãi suất 6.8%/năm, thời hạn đến 20 năm.",
                },
                {
                    "id": "acb-car-001",
                    "bank": "ACB",
                    "name": "ACB Auto Dream",
                    "purpose": "mua_xe",
                    "min_income": 8000000,
                    "max_amount": 1800000000,
                    "max_year": 6,
                    "interest_rate": 7.8,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua xe lãi suất 7.8%/năm, thời hạn đến 6 năm.",
                },
                {
                    "id": "acb-consumer-001",
                    "bank": "ACB",
                    "name": "ACB Easy Cash",
                    "purpose": "tieu_dung",
                    "min_income": 5000000,
                    "max_amount": 500000000,
                    "max_year": 5,
                    "interest_rate": 10.5,
                    "ltv_limit": 0.0,
                    "dti_limit": 0.5,
                    "description": "Vay tiêu dùng nhanh, lãi suất 10.5%/năm.",
                },
                {
                    "id": "vpb-home-001",
                    "bank": "VPBank",
                    "name": "VPBank Home Sweet",
                    "purpose": "mua_nha",
                    "min_income": 12000000,
                    "max_amount": 10000000000,
                    "max_year": 25,
                    "interest_rate": 6.3,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua nhà lãi suất 6.3%/năm, thời hạn đến 25 năm.",
                },
                {
                    "id": "vpb-car-001",
                    "bank": "VPBank",
                    "name": "VPBank Auto Pro",
                    "purpose": "mua_xe",
                    "min_income": 9000000,
                    "max_amount": 2000000000,
                    "max_year": 7,
                    "interest_rate": 7.2,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua ô tô lãi suất 7.2%/năm, thời hạn đến 7 năm.",
                },
                {
                    "id": "vpb-biz-001",
                    "bank": "VPBank",
                    "name": "VPBank SME Growth",
                    "purpose": "kinh_doanh",
                    "min_income": 18000000,
                    "max_amount": 8000000000,
                    "max_year": 10,
                    "interest_rate": 7.8,
                    "ltv_limit": 0.7,
                    "dti_limit": 0.45,
                    "description": "Vay kinh doanh SME lãi suất 7.8%/năm, thời hạn đến 10 năm.",
                },
                {
                    "id": "bidv-home-001",
                    "bank": "BIDV",
                    "name": "BIDV Home Loan",
                    "purpose": "mua_nha",
                    "min_income": 11000000,
                    "max_amount": 15000000000,
                    "max_year": 25,
                    "interest_rate": 6.1,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua nhà lãi suất 6.1%/năm, thời hạn đến 25 năm.",
                },
                {
                    "id": "bidv-car-001",
                    "bank": "BIDV",
                    "name": "BIDV Auto Loan",
                    "purpose": "mua_xe",
                    "min_income": 9000000,
                    "max_amount": 2000000000,
                    "max_year": 7,
                    "interest_rate": 7.0,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua ô tô lãi suất 7.0%/năm, thời hạn đến 7 năm.",
                },
                {
                    "id": "bidv-biz-001",
                    "bank": "BIDV",
                    "name": "BIDV Business Loan",
                    "purpose": "kinh_doanh",
                    "min_income": 20000000,
                    "max_amount": 10000000000,
                    "max_year": 10,
                    "interest_rate": 7.5,
                    "ltv_limit": 0.7,
                    "dti_limit": 0.45,
                    "description": "Vay kinh doanh lãi suất 7.5%/năm, thời hạn đến 10 năm.",
                },
                {
                    "id": "mb-home-001",
                    "bank": "MB Bank",
                    "name": "MB Home Dream",
                    "purpose": "mua_nha",
                    "min_income": 10000000,
                    "max_amount": 10000000000,
                    "max_year": 25,
                    "interest_rate": 6.4,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua nhà lãi suất 6.4%/năm, thời hạn đến 25 năm.",
                },
                {
                    "id": "mb-car-001",
                    "bank": "MB Bank",
                    "name": "MB Auto Dream",
                    "purpose": "mua_xe",
                    "min_income": 8000000,
                    "max_amount": 2000000000,
                    "max_year": 7,
                    "interest_rate": 7.3,
                    "ltv_limit": 0.8,
                    "dti_limit": 0.4,
                    "description": "Vay mua ô tô lãi suất 7.3%/năm, thời hạn đến 7 năm.",
                },
                {
                    "id": "mb-consumer-001",
                    "bank": "MB Bank",
                    "name": "MB Easy Cash",
                    "purpose": "tieu_dung",
                    "min_income": 5000000,
                    "max_amount": 400000000,
                    "max_year": 5,
                    "interest_rate": 10.0,
                    "ltv_limit": 0.0,
                    "dti_limit": 0.5,
                    "description": "Vay tiêu dùng nhanh, lãi suất 10.0%/năm.",
                },
                {
                    "id": "mb-biz-001",
                    "bank": "MB Bank",
                    "name": "MB Business Plus",
                    "purpose": "kinh_doanh",
                    "min_income": 15000000,
                    "max_amount": 6000000000,
                    "max_year": 10,
                    "interest_rate": 7.9,
                    "ltv_limit": 0.7,
                    "dti_limit": 0.45,
                    "description": "Vay kinh doanh lãi suất 7.9%/năm, thời hạn đến 10 năm.",
                },
            ]
            income = profile.get("income", 0)
            loan_purpose = profile.get("loan_purpose", "")
            loan_amount = profile.get("loan_amount", 0)
            loan_year = profile.get("loan_year", 1)
            asset_value = profile.get("asset_value", 0)

            scored = []
            for p in _LOCAL_PRODUCTS:
                score = 0
                reasons = []
                if p["purpose"] == loan_purpose:
                    score += 50
                    reasons.append("Phù hợp mục đích vay")
                else:
                    score -= 30
                if income >= p["min_income"]:
                    score += 20
                else:
                    score -= 40
                    reasons.append(
                        f"Thu nhập thấp hơn yêu cầu tối thiểu {p['min_income']:,} VNĐ"
                    )
                if loan_amount <= p["max_amount"]:
                    score += 15
                else:
                    score -= 20
                    reasons.append(f"Số tiền vay vượt ngưỡng {p['max_amount']:,} VNĐ")
                if loan_year <= p["max_year"]:
                    score += 10
                else:
                    score -= 10
                if asset_value and asset_value > 0:
                    ltv = loan_amount / asset_value
                    if ltv <= p["ltv_limit"]:
                        score += 10
                    else:
                        score -= 15
                        reasons.append(f"LTV vượt ngưỡng {p['ltv_limit'] * 100:.0f}%")
                score += max(0, 15 - p["interest_rate"])
                scored.append({"product": p, "score": score, "reasons": reasons})

            scored.sort(key=lambda x: x["score"], reverse=True)
            top_products = scored[:3]

            if not top_products:
                return ExecutionResult(
                    task=task_name,
                    success=True,
                    data={
                        "products": [],
                        "best_match": None,
                        "reasoning": "Không có sản phẩm local để gợi ý.",
                    },
                )

            best = top_products[0]["product"]
            reasoning = (
                f"Gói vay phù hợp nhất: {best['name']} tại {best['bank']} "
                f"với lãi suất {best['interest_rate']}%/năm, "
                f"hỗ trợ vay đến {best['max_amount']:,} VNĐ trong {best['max_year']} năm."
            )
            return ExecutionResult(
                task=task_name,
                success=True,
                data={
                    "products": [p["product"] for p in top_products],
                    "best_match": best,
                    "reasoning": reasoning,
                },
            )

        elif task_name in ("faq_search", "policy_search"):
            # Fallback local keyword search
            query = profile.get("last_query", "")
            data_pool = []
            if task_name == "faq_search":
                data_pool = [
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
                query_lower = query.lower()
                local_results = []
                for item in data_pool:
                    score = 0
                    if any(
                        word in item["question"].lower() for word in query_lower.split()
                    ):
                        score += 2
                    if any(
                        word in item["answer"].lower() for word in query_lower.split()
                    ):
                        score += 1
                    if score > 0:
                        local_results.append({"score": score, "item": item})
                local_results.sort(key=lambda x: x["score"], reverse=True)
                answers = [r["item"] for r in local_results[:3]]
                if not answers:
                    answers = [
                        {
                            "question": "",
                            "answer": "MCP server không khả dụng và không có câu trả lời local phù hợp.",
                            "found": False,
                        }
                    ]
                return ExecutionResult(
                    task=task_name,
                    success=True,
                    data={
                        "answers": answers,
                        "sources": ["local_fallback"],
                        "found": bool(answers[0].get("found", True)),
                    },
                )
            else:
                data_pool = [
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
                query_lower = query.lower()
                local_results = []
                for item in data_pool:
                    score = 0
                    if any(
                        word in item["title"].lower() for word in query_lower.split()
                    ):
                        score += 3
                    if any(
                        word in item["content"].lower() for word in query_lower.split()
                    ):
                        score += 2
                    if any(
                        word in item["category"].lower() for word in query_lower.split()
                    ):
                        score += 1
                    if score > 0:
                        local_results.append({"score": score, "item": item})
                local_results.sort(key=lambda x: x["score"], reverse=True)
                policies = [r["item"] for r in local_results[:5]]
                if not policies:
                    policies = [
                        {
                            "title": "",
                            "content": "MCP server không khả dụng và không có chính sách local phù hợp.",
                            "found": False,
                        }
                    ]
                return ExecutionResult(
                    task=task_name,
                    success=True,
                    data={
                        "policies": policies,
                        "effective_date": "2026-01-01",
                        "found": bool(policies[0].get("found", True)),
                    },
                )

        elif task_name == "general_response":
            return ExecutionResult(
                task=task_name,
                success=True,
                data={
                    "response": "Tôi hiểu. Bạn có thể cho tôi biết thêm về nhu cầu vay vốn của mình không?"
                },
            )

        return ExecutionResult(
            task=task_name, success=False, error="No MCP server and no local fallback"
        )
