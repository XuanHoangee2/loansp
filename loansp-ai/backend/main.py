from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.web_html import router as web_router
from app.api.health_check import router as health_router
from contextlib import asynccontextmanager
from app.core.logging.log import logger
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

import uvicorn
import os

from app.modules.conversation.prompt_template import system_prompt_LoanAgent

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "src", "static")


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Initializing application...")

    # Embedding
    # app.state.embedding = download_embeddings()

    # LLM
    app.state.llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API")
    )

    # Prompt
    app.state.prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_LoanAgent),
        MessagesPlaceholder(variable_name="chat_history"), 
        ("human", "{input}")
        ])
    # T?o chain 
    app.state.question_answer_chain = (
        app.state.prompt
        | app.state.llm
        | StrOutputParser()
    )

    logger.info("Application initialized successfully")

    yield

    logger.info("Shutting down application...")


app = FastAPI(
    title="Loan Agent API",
    description="AI-powered loan consultation chatbot",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router)
app.include_router(web_router)
app.include_router(health_router)
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
