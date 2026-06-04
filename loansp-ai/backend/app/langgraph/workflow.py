from fastapi import FastAPI

from langgraph.graph import (
    StateGraph,
    END,
)

from app.langgraph.agentstate import (
    LoanAgentState,
)

from app.langgraph.node import (
    load_memory_node,
    extract_profile_node,
    intent_node,
    planner_node,
    validator_node,
    executor_node,
    ask_missing_node,
    clear_task_node,
    general_chat_node,
)

from app.langgraph.node import (
    route_intent,
    validation_router,
)

def _initialize_graph(
    app: FastAPI,
    planner_service,
    validation_service,
    executor_service,
    memory_service,
    ai_service,
):
    """Khởi tạo và cấu hình workflow graph"""
    workflow = StateGraph(
        LoanAgentState
    )

    # Thêm các Node vào hệ thống
    workflow.add_node(
        "load_memory",
        load_memory_node(
            memory_service
        )
    )

    workflow.add_node(
        "extract_profile",
        extract_profile_node(
            ai_service,
            memory_service,
        )
    )

    workflow.add_node(
        "intent_classifier",
        intent_node(
            planner_service
        )
    )

    workflow.add_node(
        "general_chat",
        general_chat_node(
            ai_service
        )
    )

    workflow.add_node(
        "planner",
        planner_node(
            planner_service
        )
    )

    workflow.add_node(
        "validator",
        validator_node(
            validation_service
        )
    )

    workflow.add_node(
        "ask_missing",
        ask_missing_node(
            memory_service
        )
    )

    workflow.add_node(
        "executor",
        executor_node(
            executor_service
        )
    )

    workflow.add_node(
        "clear_task",
        clear_task_node(
            memory_service
        )
    )

    # Thiết lập điểm bắt đầu
    workflow.set_entry_point(
        "load_memory"
    )

    workflow.add_edge(
        "load_memory",
        "extract_profile"
    )

    workflow.add_edge(
        "extract_profile",
        "intent_classifier"
    )
    workflow.add_edge(
        "general_chat",
        END,
    )
    workflow.add_edge(
        "planner",
        "validator",
    )
    workflow.add_edge(
        "ask_missing",
        END,
    )
    workflow.add_edge(
        "executor",
        "clear_task",
    )
    workflow.add_edge(
        "clear_task",
        END,
    )

    workflow.add_conditional_edges(
        "intent_classifier",
        route_intent,
        {
            "general_chat":
                "general_chat",

            "planner":
                "planner",
        },
    )
    workflow.add_conditional_edges(
        "validator",
        validation_router,
        {
            "ask_missing":
                "ask_missing",

            "executor":
                "executor",
        },
    )
    # Compile Graph thành một ứng dụng hoàn chỉnh
    return workflow.compile(
        checkpointer=
            app.state.checkpointer
    )