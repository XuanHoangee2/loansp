import uvicorn
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from app.api.chat import router as chat_router
from app.api.web_html import router as web_router
from app.api.health_check import router as health_router

from app.core.logging.log import logger

from app.schemas.chat_schema import LoanUserInfo, ClassifierLoan

from langgraph.checkpoint.memory import MemorySaver
from app.langgraph.workflow import _initialize_graph
from app.langgraph.ai_service import AIService

from app.memory.redis_client import RedisClient
from app.memory.profile_memory import ProfileMemory
from app.memory.task_memory import TaskMemory
from app.memory.conversation_memory import ConversationMemory
from app.memory.memory_service import MemoryService

from app.planner.planner_service import PlannerService

from app.validator.validation_service import ValidationService

from app.MCP.mcp_client import MCPClient

from app.executor.task_executor import TaskExecutor
from app.executor.result_builder import ResultBuilder
from app.executor.executor_service import ExecutorService
from app.executor.mcp_router import MCPRouter

from app.modules.conversation.prompt_template import (
    system_prompt_extract_LoanAgent,
    system_prompt_classifier_LoanAgent,
    system_prompt_conversation_LoanAgent,
)


load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "src", "static")


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Initializing application...")

    # Embedding
    # app.state.embedding = download_embeddings()
    try:
        # LLM
        app.state.llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0.7,
            groq_api_key=os.getenv("GROQ_API"),
        )
        #################################################################

        structured_llm = app.state.llm.with_structured_output(LoanUserInfo)

        classifier_llm = app.state.llm.with_structured_output(ClassifierLoan)

        prompt_extract = ChatPromptTemplate.from_messages(
            [("system", system_prompt_extract_LoanAgent), ("human", "{input}")]
        )

        classifier_prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt_classifier_LoanAgent), ("human", "{input}")]
        )

        conversation_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt_conversation_LoanAgent),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        extract_chain = prompt_extract | structured_llm

        classifier_chain = classifier_prompt | classifier_llm

        conversation_chain = conversation_prompt | app.state.llm | StrOutputParser()

        ai_service = AIService(
            extract_chain=extract_chain,
            classifier_chain=classifier_chain,
            conversation_chain=conversation_chain,
        )

        # Memory
        redis_client = RedisClient(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
        )

        redis = redis_client.redis
        profile_memory = ProfileMemory(redis)
        task_memory = TaskMemory(redis)
        conversation_memory = ConversationMemory(redis)
        memory_service = MemoryService(
            profile_memory=profile_memory,
            task_memory=task_memory,
            conversation_memory=conversation_memory,
        )
        #######################################

        # Planner
        planner_service = PlannerService(llm=app.state.llm)
        # validation
        validation_service = ValidationService()
        ##########################################

        # MCP Client
        try:
            mcp_client = MCPClient(
                server_configs={
                    "loan_mcp": os.getenv("LOAN_MCP_URL", "http://localhost:8001/sse"),
                    "knowledge_mcp": os.getenv(
                        "KNOWLEDGE_MCP_URL", "http://localhost:8002/sse"
                    ),
                }
            )
            await mcp_client.connect()
        except Exception as e:
            logger.warning(f"MCP init failed: {e}")
            mcp_client = None  # vẫn cho app chạy
        #############################################

        # executor
        router = MCPRouter()

        task_executor = TaskExecutor(
            router=router,
            mcp_client=mcp_client,
        )

        result_builder = ResultBuilder()

        executor_service = ExecutorService(
            task_executor=task_executor,
            result_builder=result_builder,
        )

        app.state.checkpointer = MemorySaver()
        app.state.graph = _initialize_graph(
            app,
            planner_service,
            validation_service,
            executor_service,
            memory_service,
            ai_service,
        )
        logger.info("Application initialized successfully")

        yield

    finally:
        logger.info("Shutting down application...")

        if hasattr(app.state, "memory_service"):
            await redis.close()
        if hasattr(app.state, "mcp_client"):
            await app.state.mcp_client.disconnect()


app = FastAPI(
    title="Loan Agent API",
    description="AI-powered loan consultation chatbot",
    version="1.0.0",
    lifespan=lifespan,
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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")

# docker run -d -p 6379:6379 redis:alpine
