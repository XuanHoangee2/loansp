import os
from pathlib import Path
import logging

logging.basicConfig(level= logging.INFO, format= '[%(asctime)s]: %(message)s:')
project_name = "loansp-ai"

list_of_file = [
    f"{project_name}/backend/app/api/chat.py",
    f"{project_name}/backend/app/api/loan.py",
    f"{project_name}/backend/app/api/web_html.py",
    f"{project_name}/backend/app/api/health_check.py",
    f"{project_name}/backend/app/planner/models.py",
    f"{project_name}/backend/app/planner/intent_planner.py",
    f"{project_name}/backend/app/planner/task_planner.py",
    f"{project_name}/backend/app/planner/prompt.py",
    f"{project_name}/backend/app/planner/planner_service.py",
    f"{project_name}/backend/app/validator/models.py",
    f"{project_name}/backend/app/validator/tool_requirements.py",
    f"{project_name}/backend/app/validator/validator.py",
    f"{project_name}/backend/app/validator/validation_service.py",
    f"{project_name}/backend/app/validator/question_generator.py",
    f"{project_name}/backend/app/executor/mcp_router.py",
    f"{project_name}/backend/app/executor/task_executor.py",
    f"{project_name}/backend/app/executor/models.py",
    f"{project_name}/backend/app/executor/task_registry.py",
    f"{project_name}/backend/app/executor/result_builder.py",
    f"{project_name}/backend/app/executor/executor_service.py",
    f"{project_name}/backend/app/memory/memory_service.py",
    f"{project_name}/backend/app/memory/conversation_memory.py",
    f"{project_name}/backend/app/memory/profile_memory.py",
    f"{project_name}/backend/app/memory/task_memory.py",
    f"{project_name}/backend/app/memory/models.py",
    f"{project_name}/backend/app/memory/redis_client.py",

    f"{project_name}/backend/app/MCP/mcp_client.py",

    f"{project_name}/backend/app/langgraph/agentstate.py",
    f"{project_name}/backend/app/langgraph/node.py",
    f"{project_name}/backend/app/langgraph/workflow.py",
    f"{project_name}/backend/app/langgraph/question_bank.py",
    f"{project_name}/backend/app/langgraph/ai_service.py",

    f"{project_name}/backend/app/schemas/chat_schema.py",
    f"{project_name}/backend/app/schemas/state.py",
    f"{project_name}/backend/app/core/config/config.py",
    f"{project_name}/backend/app/core/logging/log.py",
    f"{project_name}/backend/app/main.py",
    f"{project_name}/backend/Dockerfile",
    f"{project_name}/backend/requirements.txt",
    f"{project_name}/backend/docker-compose.yml",
    f"{project_name}/backend/docker-compose.yml",
    f"{project_name}/backend/.dockerignore",
    f"{project_name}/backend/.env",

    f"{project_name}/backend/src/static/style.css",
    f"{project_name}/backend/src/index.html",

    f"{project_name}/test/test_chat.py",
    f"{project_name}/test/test_web.py",
    f"{project_name}/test/conftest.py",
    f"{project_name}/docs/CONTEXT.md",

    f"{project_name}/mcp_server/Dockerfile",
    f"{project_name}/mcp_server/requirements.txt",
    f"{project_name}/mcp_server/docker-compose.yml",
    f"{project_name}/mcp_server/docker-compose.yml",
    f"{project_name}/mcp_server/.dockerignore",
    f"{project_name}/mcp_server/.env",

    f"{project_name}/.github/workflows/ci.yml",
    f"{project_name}/.env",
    ".gitignore",
]

for filepath in list_of_file:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for this file {filename}")

    if (not os.path.exists(filepath) or (os.path.getsize(filepath) == 0)):
        with open(filepath, "w") as f:
            pass
            logging.info(f"Creating empty file: {filename}")
    else:
        logging.info(f"{filename} is already created")