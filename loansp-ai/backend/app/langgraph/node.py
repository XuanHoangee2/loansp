from langchain_core.messages import AIMessage
from .question_bank import QUESTION_BANK


# Node 1 Load Memory
def load_memory_node(memory_service):
    async def _node(state):
        profile = await memory_service.get_profile(state["session_id"])
        task = await memory_service.get_active_task(state["session_id"])
        return {
            "customer_profile": profile.model_dump(),
            "active_task": task.model_dump() if task else None,
        }

    return _node


# Node 2 Extract User Information


def extract_profile_node(ai_service, memory_service):
    async def _node(state):

        user_message = state["messages"][-1].content

        extracted = await ai_service.extract_chain.ainvoke({"input": user_message})
        updates = {
            "income": extracted.income,
            "asset_value": extracted.asset_value,
            "loan_amount": extracted.loan_amount,
            "loan_year": extracted.loan_year,
            "loan_purpose": extracted.loan_purpose,
            "language": extracted.language,
            "last_query": user_message,
        }
        profile = await memory_service.update_profile(state["session_id"], updates)
        return {"customer_profile": profile.model_dump()}

    return _node


# Node 3 Intent
def intent_node(planner_service):
    async def _node(state):

        user_input = state["messages"][-1].content

        intent = await planner_service.plan(user_input)

        return {"intent": intent}

    return _node


# Edge 1 Route based on Intent
def route_intent(state):
    if state["intent"] == "general_chat":
        return "general_chat"

    return "planner"


# Node 4 General Chat
def general_chat_node(ai_service):
    async def _node(state):

        response = await ai_service.conversation_chain.ainvoke(
            {
                "input": state["messages"][-1].content,
                "chat_history": state["messages"][:-1],
            }
        )

        return {"messages": [AIMessage(content=response)]}

    return _node


# Node 5 Planner
def planner_node(planner_service):
    async def _node(state):

        plan = await planner_service.plan(
            user_query=state["messages"][-1].content,
        )

        return {"plan": plan}

    return _node


# Node 6 Validator
def validator_node(validation_service):
    async def _node(state):

        result = validation_service.validate_plan(
            plan=state["plan"], customer_profile=state["customer_profile"]
        )

        return {"validation_result": result}

    return _node


# Edge 2 Route based on validation result
def validation_router(state):
    result = state["validation_result"]
    if result["status"] == "valid":
        return "executor"
    return "ask_missing"


# Node 7 Ask Missing Information
def ask_missing_node(memory_service):
    async def _node(state):
        missing_fields = state["validation_result"]["missing_fields"]

        plan = state["plan"]
        if isinstance(plan, dict):
            task_name = plan.get("task", "unknown")
        else:
            # PlanResult object
            tasks = plan.tasks if hasattr(plan, "tasks") else []
            if tasks:
                task_name = str(tasks[0].task)
            else:
                task_name = "unknown"

        await memory_service.save_active_task(
            state["session_id"], task_name, missing_fields
        )

        questions = []
        for field in missing_fields:
            questions.append(QUESTION_BANK["vi"][field][0])

        return {"messages": [AIMessage(content="\n".join(questions))]}

    return _node


# Node 8 Executor
def executor_node(executor_service, ai_service):
    async def _node(state):
        plan = state["plan"]
        # Check if all tasks are general_response
        tasks = plan.tasks if hasattr(plan, "tasks") else []
        if tasks and all(
            str(t.task) == "TaskType.GENERAL_RESPONSE"
            or str(t.task) == "general_response"
            for t in tasks
        ):
            # Use LLM for general response
            response = await ai_service.conversation_chain.ainvoke(
                {
                    "input": state["messages"][-1].content,
                    "chat_history": state["messages"][:-1],
                }
            )
            return {
                "execution_result": {"response": response, "results": []},
                "messages": [AIMessage(content=response)],
            }

        result = await executor_service.execute_plan(
            plan=plan,
            customer_profile=state["customer_profile"],
        )
        return {
            "execution_result": result,
            "messages": [AIMessage(content=result["response"])],
        }

    return _node


# Node 9 Clear Task
def clear_task_node(memory_service):
    async def _node(state):
        await memory_service.clear_task(state["session_id"])
        return {"active_task": state.get("active_task")}

    return _node


# # NODE 1: Trích xuất thông tin
# # node.py
# def info_extractor(extract_chain):
#     def _extractor(state: LoanAgentState):
#         user_input = state["messages"][-1].content
#         extracted_data = extract_chain.invoke({
#             "input": user_input
#         })
#         return {
#             "income": extracted_data.income or state.get("income"),
#             "asset_value": extracted_data.asset_value or state.get("asset_value"),
#             "loan_purpose": extracted_data.loan_purpose or state.get("loan_purpose"),
#             "loan_amount": extracted_data.loan_amount or state.get("loan_amount"),
#             "loan_year": extracted_data.loan_year or state.get("loan_year"),
#             "language": extracted_data.language or state.get("language")
#         }
#     return _extractor

# # NODE 2: Thực hiện truy vấn Vector DB khi đã đủ điều kiện
# def query_vector_db(state: LoanAgentState):
#     # Lấy các thông tin từ State để làm tham số filter cho Vector DB
#     user_income = state["income"]
#     purpose = state["loan_purpose"]

#     # Giả lập gọi Vector DB (Hybrid Search)
#     # results = vector_db.similarity_search(query=..., filter={"min_income": {"$lte": user_income}, ...})
#     dummy_result = f"Dựa trên thu nhập {user_income:,} VNĐ và mục đích {purpose}, gợi ý gói vay VIB rải ngân 80% với lãi suất 6.5%."

#     return {
#         "messages": [AIMessage(content=f"Tôi đã tìm thấy giải pháp phù hợp cho bạn: {dummy_result}")],
#         "final_recommendation": dummy_result
#     }

# # Node 3: Hỏi thêm thông tin từ người dùng nếu chưa đủ điều kiện
# def ask_user_more(state: LoanAgentState):

#     language = state.get("language") or "vi"

#     missing_fields = []

#     if state.get("income") is None:
#         missing_fields.append("income")

#     if state.get("asset_value") is None:
#         missing_fields.append("asset_value")

#     if state.get("loan_purpose") is None:
#         missing_fields.append("loan_purpose")

#     if state.get("loan_amount") is None:
#         missing_fields.append("loan_amount")

#     if state.get("loan_year") is None:
#         missing_fields.append("loan_year")

#     missing_fields = missing_fields[:MAX_QUESTION_PER_TURN]

#     questions = [
#         random.choice(
#             QUESTION_BANK[language][field]
#         )
#         for field in missing_fields
#     ]

#     response = "\n".join(
#         f"{idx + 1}. {question}"
#         for idx, question in enumerate(questions)
#     )

#     return {
#         "messages": [
#             AIMessage(content=response)
#         ]
#     }

# # Node 4: Phân loại ý định ko dùng LLM
# def intend_classifier(state: LoanAgentState):
#     user_input = state["messages"][-1].content
#     intend = detect_loan_by_keyword(user_input)
#     return {
#         "intend": intend
#     }
# # Node 5: Trò chuyện chung
# def general_conversation(conversation_chain):
#     def _general_conversation(state: LoanAgentState):
#         user_input = state["messages"][-1].content
#         response = conversation_chain.invoke({
#             "input": user_input,
#             "chat_history": state["messages"][:-1]
#         })
#         return {
#             "messages": [
#                 AIMessage(content=response)
#             ]
#         }
#     return _general_conversation

# # EDGE 3: Phân loại ý định dùng LLM
# def intend_classifier_LLM(classifier_chain):
#     def _classifier(state: LoanAgentState):

#         if state.get("intend") is not None:
#             return "loan_inquiry" if state["intend"] else "generally_conversation"

#         user_input = state["messages"][-1].content
#         intend = classifier_chain.invoke({"input": user_input})

#         # IMPORTANT: return STRING ONLY
#         return "loan_inquiry" if intend else "generally_conversation"

#     return _classifier

# # EDGE 2: Kiểm tra xem đã đủ thông tin để đi tiếp chưa
# def check_information_status(state: LoanAgentState):
#     # Kiểm tra xem 5 thông tin cốt lõi đã được điền đầy đủ chưa
#     if (state.get("income") is not None and
#         state.get("asset_value") is not None and
#         state.get("loan_purpose") is not None and
#         state.get("loan_amount") is not None and
#         state.get("loan_year") is not None):

#         return "go_to_db"

#     return "ask_user_more"
