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
    f"{project_name}/backend/app/modules/conversation/grok_client.py",
    f"{project_name}/backend/app/modules/conversation/prompt_template.py",
    f"{project_name}/backend/app/modules/embeddings/embeddings_layer.py",
    f"{project_name}/backend/app/modules/financial_engine/formulas.py",
    f"{project_name}/backend/app/schemas/chat_schema.py",
    f"{project_name}/backend/app/database/session.py",
    f"{project_name}/backend/app/core/config/config.py",
    f"{project_name}/backend/app/core/logging/log.py",
    f"{project_name}/backend/main.py",
    f"{project_name}/backend/src/static/style.css",
    f"{project_name}/backend/src/index.html",
    f"{project_name}/docs/CONTEXT.md",
    f"{project_name}/Dockerfile",
    f"{project_name}/requirements.txt",
    f"{project_name}/.dockerignore",
    f"{project_name}/docker-compose.yml",
    f"{project_name}/.github/workflows/ci.yml",
    "requirements.txt",
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