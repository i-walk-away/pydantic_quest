from fastapi import APIRouter

from backend.src.app.api.v1.lesson import router as lesson_router

router = APIRouter()
router.include_router(router=lesson_router)
