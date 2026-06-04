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
                "income": profile.get("income"),
                "loan_amount": profile.get("loan_amount"),
                "loan_year": profile.get("loan_year"),
            }
        elif tool == "calculate_ltv":
            return {
                "asset_value": profile.get("asset_value"),
                "loan_amount": profile.get("loan_amount"),
            }
        elif tool == "recommend_loan":
            return {
                "income": profile.get("income"),
                "loan_purpose": profile.get("loan_purpose"),
                "loan_amount": profile.get("loan_amount"),
                "loan_year": profile.get("loan_year"),
            }
        elif tool in ("faq_search", "policy_search"):
            # Lấy tin nhắn gần nhất làm query nếu có
            messages = profile.get("messages", [])
            query = messages[-1].get("content", "") if messages else ""
            return {"query": query}
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
        try:
            route = self.router.resolve(task_name)
            server = route["mcp"]
            tool = route["tool"]

            # Nếu server không kết nối được, fallback sang local
            if server not in getattr(self.mcp_client, 'sessions', {}):
                return await self._fallback_local(task_name, customer_profile)

            arguments = self._build_arguments(tool, customer_profile)
            mcp_result = await self.mcp_client.call_tool(server, tool, arguments)
            data = self._parse_mcp_result(mcp_result)
            return ExecutionResult(task=task_name, success=True, data=data)
        except Exception as e:
            logger.error(f"Task '{task_name}' failed: {e}")
            return ExecutionResult(task=task_name, success=False, error=str(e))

    async def _fallback_local(self, task_name: str, profile: dict) -> ExecutionResult:
        """Xử lý local khi MCP server không khả dụng."""
        if task_name == "calculate_dti":
            income = profile.get("income", 0)
            loan_amount = profile.get("loan_amount", 0)
            loan_year = profile.get("loan_year", 1)
            monthly_income = income / 12 if income else 0
            monthly_payment = (loan_amount / (loan_year * 12)) if loan_amount else 0
            dti = monthly_payment / monthly_income if monthly_income else 0
            return ExecutionResult(task=task_name, success=True, data={"dti": dti})
        # ... thêm fallback cho các task khác
        return ExecutionResult(task=task_name, success=False, error="No MCP server and no local fallback")