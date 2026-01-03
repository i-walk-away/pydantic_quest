from fastapi import APIRouter

from src.app.admin.routes.lesson import router as lessons_router

router = APIRouter()
router.include_router(router=lessons_router)

# новые админ роуты сюда
