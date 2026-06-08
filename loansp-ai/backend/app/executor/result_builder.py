from langchain_core.messages import SystemMessage, HumanMessage


class ResultBuilder:
    def __init__(self, llm=None):
        self.llm = llm

    def _is_not_found(self, result):
        """Kiểm tra kết quả có phải là fallback 'không tìm thấy' không."""
        found = result.data.get("found")
        if found is False:
            return True
        if result.task == "faq_search":
            answers = result.data.get("answers", [])
            if len(answers) == 1 and not answers[0].get("question"):
                return True
        elif result.task == "policy_search":
            policies = result.data.get("policies", [])
            if len(policies) == 1 and not policies[0].get("title"):
                return True
        return False

    def _extract_task_context(self, result):
        """Trích xuất context từ một execution result."""
        if result.task == "faq_search":
            answers = result.data.get("answers", [])
            lines = ["FAQ Search Results:"]
            for idx, ans in enumerate(answers, 1):
                q = ans.get("question", "")
                a = ans.get("answer", "")
                if q:
                    lines.append(f"  {idx}. Câu hỏi: {q}\n     Trả lời: {a}")
                else:
                    lines.append(f"  {idx}. {a}")
            return "\n".join(lines)

        elif result.task == "policy_search":
            policies = result.data.get("policies", [])
            lines = ["Policy Search Results:"]
            for idx, pol in enumerate(policies, 1):
                title = pol.get("title", "")
                content = pol.get("content", "")
                if title:
                    lines.append(f"  {idx}. {title}: {content}")
                else:
                    lines.append(f"  {idx}. {content}")
            return "\n".join(lines)

        elif result.task == "recommend_loan":
            products = result.data.get("products", [])
            best = result.data.get("best_match")
            lines = ["Loan Recommendations:"]
            if best:
                lines.append(
                    f"  Best match: {best['name']} at {best['bank']} - "
                    f"rate {best['interest_rate']}%/year, "
                    f"limit up to {best['max_amount']:,} VND, "
                    f"term up to {best['max_year']} years. "
                    f"Description: {best.get('description', '')}"
                )
            for idx, p in enumerate(products, 1):
                lines.append(
                    f"  {idx}. {p['name']} ({p['bank']}) - "
                    f"rate {p['interest_rate']}%/year, "
                    f"limit {p['max_amount']:,} VND, "
                    f"term {p['max_year']} years. "
                    f"Description: {p.get('description', '')}"
                )
            return "\n".join(lines)

        elif result.task == "calculate_dti":
            dti = result.data.get("dti", 0)
            status = result.data.get("status", "unknown")
            return f"DTI Analysis: {dti * 100:.1f}% (status: {status})"

        elif result.task == "calculate_ltv":
            ltv = result.data.get("ltv", 0)
            status = result.data.get("status", "unknown")
            return f"LTV Analysis: {ltv * 100:.1f}% (status: {status})"

        elif result.task == "estimate_payment":
            pmt = result.data.get("monthly_payment", 0)
            total = result.data.get("total_interest", 0)
            return f"Payment Estimate: monthly {pmt:,.0f} VND, total interest {total:,.0f} VND"

        elif result.task == "compare_products":
            comparison = result.data.get("comparison", [])
            recommendation = result.data.get("recommendation", "")
            lines = ["Product Comparison:"]
            for idx, item in enumerate(comparison, 1):
                lines.append(
                    f"  {idx}. {item['name']} ({item['bank']}) - "
                    f"rate {item['rate']}%/year, monthly {item['monthly_payment']:,} VND, "
                    f"total interest {item['total_interest']:,} VND"
                )
            if recommendation:
                lines.append(f"  Recommendation: {recommendation}")
            return "\n".join(lines)

        return None

    async def _build_single_with_llm(self, task, context, user_query, is_listing=False):
        """Dùng LLM để tổng hợp câu trả lời tự nhiên từ context của một task."""
        if not self.llm or not context:
            return None
        if is_listing:
            system_text = (
                "Bạn là trợ lý tư vấn tài chính thân thiện và chuyên nghiệp. "
                "Khách hàng đang hỏi về danh sách các gói vay. "
                "Dựa trên thông tin các gói vay bên dưới, hãy giới thiệu các gói vay phù hợp nhất "
                "một cách tự nhiên, rõ ràng. Nêu rõ ngân hàng, lãi suất, hạn mức, thời hạn. "
                "Trả lời bằng tiếng Việt."
            )
        else:
            system_text = (
                "Bạn là trợ lý tư vấn tài chính thân thiện và chuyên nghiệp. "
                "Dựa trên câu hỏi của khách hàng và thông tin tìm kiếm được bên dưới, "
                "hãy viết một câu trả lời tự nhiên, rõ ràng, dễ hiểu và đầy đủ thông tin. "
                "Không liệt kê máy móc. Trả lời bằng tiếng Việt."
            )
        human_text = (
            f"Câu hỏi của khách hàng: {user_query}\n\n"
            f"Thông tin:\n{context}\n\n"
            f"Hãy trả lời khách hàng một cách tự nhiên:"
        )
        messages = [
            SystemMessage(content=system_text),
            HumanMessage(content=human_text),
        ]
        try:
            response = await self.llm.ainvoke(messages)
            return response.content if hasattr(response, "content") else str(response)
        except Exception:
            return None

    async def _build_multi_with_llm(self, contexts, user_query):
        """Dùng LLM để tổng hợp câu trả lời từ nhiều context (multi-task)."""
        if not self.llm or not contexts:
            return None
        combined = "\n\n".join(contexts)
        system_text = (
            "Bạn là trợ lý tư vấn tài chính thân thiện và chuyên nghiệp. "
            "Khách hàng đang hỏi nhiều vấn đề cùng lúc. "
            "Dựa trên tất cả thông tin được cung cấp bên dưới, hãy viết MỘT câu trả lời duy nhất "
            "gộp tất cả các nội dung lại một cách mạch lạc, tự nhiên, dễ hiểu. "
            "Không liệt kê máy móc. Trả lời bằng tiếng Việt."
        )
        human_text = (
            f"Câu hỏi của khách hàng: {user_query}\n\n"
            f"Thông tin từ nhiều nguồn:\n{combined}\n\n"
            f"Hãy trả lời khách hàng một cách tự nhiên và mạch lạc:"
        )
        messages = [
            SystemMessage(content=system_text),
            HumanMessage(content=human_text),
        ]
        try:
            response = await self.llm.ainvoke(messages)
            return response.content if hasattr(response, "content") else str(response)
        except Exception:
            return None

    async def _build_fallback_llm(self, user_query):
        """Dùng LLM để trả lời khi không có kết quả trong cơ sở dữ liệu."""
        if not self.llm:
            return None
        system_text = (
            "Bạn là trợ lý tư vấn tài chính thân thiện và chuyên nghiệp. "
            "Hiện tại bạn chưa có thông tin cụ thể trong cơ sở dữ liệu để trả lời câu hỏi này. "
            "Hãy dùng kiến thức chung của bạn để đưa ra câu trả lời hữu ích, lịch sự và chuyên nghiệp. "
            "Nếu câu hỏi quá cụ thể, hãy đề xuất khách hàng liên hệ tư vấn viên. "
            "Trả lời bằng tiếng Việt."
        )
        human_text = (
            f"Câu hỏi của khách hàng: {user_query}\n\n"
            f"Hãy trả lời khách hàng một cách tự nhiên và lịch sự:"
        )
        messages = [
            SystemMessage(content=system_text),
            HumanMessage(content=human_text),
        ]
        try:
            response = await self.llm.ainvoke(messages)
            return response.content if hasattr(response, "content") else str(response)
        except Exception:
            return None

    def _is_listing_query(self, user_query):
        """Kiểm tra xem user có đang hỏi danh sách / các gói vay không."""
        if not user_query:
            return False
        listing_keywords = [
            "các", "danh sách", "những", "list", "gói nào", "hiện có",
            "tất cả", "bao nhiêu gói", "mấy gói", "có gì", "có những",
        ]
        q = user_query.lower()
        return any(k in q for k in listing_keywords)

    async def build(self, execution_results, user_query=""):
        # Separate results into categories
        rich_results = []  # results that need LLM synthesis (recommend, search, policy)
        calc_results = []  # results that are simple calculations
        fallback_outputs = []  # outputs for failed tasks or general_response

        for result in execution_results:
            if not result.success:
                fallback_outputs.append(f"Lỗi: {result.error}")
                continue

            if result.task in ("faq_search", "policy_search", "recommend_loan", "compare_products"):
                if not self._is_not_found(result):
                    rich_results.append(result)
                else:
                    # Not found - will be handled as fallback
                    if result.task == "faq_search":
                        fallback_outputs.append("faq_not_found")
                    elif result.task == "policy_search":
                        fallback_outputs.append("policy_not_found")
                    elif result.task == "recommend_loan":
                        fallback_outputs.append("recommend_not_found")
            elif result.task in ("calculate_dti", "calculate_ltv", "estimate_payment"):
                calc_results.append(result)
            elif result.task == "general_response":
                response = result.data.get(
                    "response",
                    "Tôi hiểu. Bạn có thể cho tôi biết thêm về nhu cầu vay vốn của mình không?",
                )
                fallback_outputs.append(response)
            else:
                fallback_outputs.append(str(result.data))

        # Build contexts for rich results
        rich_contexts = []
        for result in rich_results:
            ctx = self._extract_task_context(result)
            if ctx:
                rich_contexts.append(ctx)

        # Build outputs for calculation results
        calc_outputs = []
        for result in calc_results:
            if result.task == "calculate_dti":
                dti = result.data.get("dti", 0)
                status = result.data.get("status", "unknown")
                if status == "eligible":
                    status_text = "đủ điều kiện"
                elif status == "review":
                    status_text = "cần xem xét"
                elif status == "rejected":
                    status_text = "vượt ngưỡng"
                else:
                    status_text = status
                calc_outputs.append(f"DTI hiện tại là {dti * 100:.1f}% ({status_text})")
            elif result.task == "calculate_ltv":
                ltv = result.data.get("ltv", 0)
                status = result.data.get("status", "unknown")
                if status == "eligible":
                    status_text = "đủ điều kiện"
                elif status == "review":
                    status_text = "cần xem xét"
                elif status == "rejected":
                    status_text = "vượt ngưỡng"
                else:
                    status_text = status
                calc_outputs.append(f"LTV hiện tại là {ltv * 100:.1f}% ({status_text})")
            elif result.task == "estimate_payment":
                pmt = result.data.get("monthly_payment", 0)
                total = result.data.get("total_interest", 0)
                calc_outputs.append(
                    f"Trả hàng tháng: {pmt:,.0f} VNĐ. Tổng lãi: {total:,.0f} VNĐ"
                )

        # Determine if we should use multi-task LLM synthesis
        all_contexts = rich_contexts + calc_outputs

        if len(all_contexts) >= 2 or (len(rich_contexts) == 1 and calc_outputs):
            # Multi-task or combined: use LLM to synthesize everything
            combined_contexts = list(rich_contexts)
            if calc_outputs:
                combined_contexts.append("Phân tích tài chính:\n  " + "\n  ".join(calc_outputs))
            if fallback_outputs:
                combined_contexts.append("Thông tin bổ sung:\n  " + "\n  ".join(fallback_outputs))

            llm_response = await self._build_multi_with_llm(combined_contexts, user_query)
            if llm_response:
                return llm_response

        elif len(rich_contexts) == 1:
            # Single rich task
            result = rich_results[0]
            if result.task == "recommend_loan":
                is_listing = self._is_listing_query(user_query)
                llm_response = await self._build_single_with_llm(
                    "recommend_loan", rich_contexts[0], user_query, is_listing
                )
                if llm_response:
                    return llm_response
                # Fallback
                best = result.data.get("best_match")
                if best:
                    return f"Gợi ý: {best['name']} tại {best['bank']} - lãi suất {best['interest_rate']}%/năm"
                return "Không tìm thấy gói vay phù hợp."
            else:
                llm_response = await self._build_single_with_llm(
                    result.task, rich_contexts[0], user_query
                )
                if llm_response:
                    return llm_response
                # Fallback
                if result.task == "faq_search":
                    answers = result.data.get("answers", [])
                    return answers[0].get("answer", "") if answers else ""
                elif result.task == "policy_search":
                    policies = result.data.get("policies", [])
                    return policies[0].get("content", "") if policies else ""
                elif result.task == "compare_products":
                    rec = result.data.get("recommendation", "")
                    return rec or "Không có sản phẩm để so sánh."

        elif calc_outputs:
            return "\n\n".join(calc_outputs + fallback_outputs)

        elif fallback_outputs:
            # Handle not-found fallbacks
            not_found_count = sum(
                1 for f in fallback_outputs if f in ("faq_not_found", "policy_not_found", "recommend_not_found")
            )
            if not_found_count > 0:
                llm_response = await self._build_fallback_llm(user_query)
                if llm_response:
                    return llm_response
            return "\n\n".join(
                f for f in fallback_outputs if f not in ("faq_not_found", "policy_not_found", "recommend_not_found")
            ) or "Xin lỗi, tôi chưa có thông tin để trả lời."

        return "Xin lỗi, tôi chưa hiểu yêu cầu của bạn."
