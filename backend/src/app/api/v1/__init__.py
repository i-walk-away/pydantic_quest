from fastapi import APIRouter

from .auth import router as auth_router
from .execution import router as execution_router
from .lesson import router as lesson_router
from .user import router as user_router

router = APIRouter()

router.include_router(router=lesson_router)
router.include_router(router=auth_router)
router.include_router(router=user_router)
router.include_router(router=execution_router)
