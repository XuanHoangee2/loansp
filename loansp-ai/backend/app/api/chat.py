from fastapi import HTTPException, Request
from fastapi.routing import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.core.logging.log import logger
from langchain_core.messages import HumanMessage

import groq

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, request: Request):
    """API endpoint cho chat"""
    import time

    start_time = time.time()

    try:
        chain = request.app.state.graph
        # input data
        input_data = {"messages": [HumanMessage(content=chat_request.message)]}
        config = {"configurable": {"thread_id": chat_request.thread_id}}

        # Invoke with config
        response_text = await chain.ainvoke(input_data, config)
        ai_response = response_text["messages"][-1].content
        # response

        processing_time = time.time() - start_time

        return ChatResponse(
            response=ai_response,
            thread_id=chat_request.thread_id,
            processing_time=processing_time,
        )

    except groq.AuthenticationError as e:
        logger.error(f"Groq API key invalid: {e}")
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable: Invalid API key. Please set a valid GROQ_API key.",
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
