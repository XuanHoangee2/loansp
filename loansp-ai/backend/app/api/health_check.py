from fastapi.routing import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint cho monitoring"""
    return {
        "status": "healthy",
        "service": "medical-chatbot",
        "version": "1.0.0"
    }