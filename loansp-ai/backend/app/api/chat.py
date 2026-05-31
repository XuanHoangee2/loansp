from langchain_core.messages import BaseMessage, HumanMessage
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request, Form
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
        # Tạo input data
        input_data = {
            "input": chat_request.message,
            "chat_history": [] 
        }
        
        # Thực thi 
        response_text = await chain.ainvoke(input_data)
        ai_response = response_text if isinstance(response_text, str) else response_text.get("answer", str(response_text))    
        # Lấy response
        
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
    
# @router.post("/chat")
# async def chat_form(request: Request, msg: str = Form(...)):
#     """Endpoint cho form submit"""
#     chat_request = ChatRequest(message=msg, thread_id="1")
#     chat_response = await chat(chat_request)
#     return JSONResponse(content={"response": chat_response.response})
