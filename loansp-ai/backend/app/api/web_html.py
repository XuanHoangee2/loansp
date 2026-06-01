from fastapi.routing import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@router.get("/")
async def home():
    """Trang chủ với giao diện chat"""

    return FileResponse(str(BASE_DIR / "src" / "index.html"))
