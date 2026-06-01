from fastapi import HTTPException, Request
from fastapi.routing import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.core.logging.log import logger

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, request: Request):
    """API endpoint cho chat"""
    import time
    start_time = time.time()
    
    try:
        chain = request.app.state.question_answer_chain
        # T?o input data
        input_data = {
            "input": chat_request.message,
            "chat_history": [] 
        }
        
        # Th?c thi 
        response_text = await chain.ainvoke(input_data)
        ai_response = response_text if isinstance(response_text, str) else response_text.get("answer", str(response_text))    
        # L?y response
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            response=ai_response,
            thread_id=chat_request.thread_id,
            processing_time=processing_time,
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
