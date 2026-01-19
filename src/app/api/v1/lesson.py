from src.app.transport.lesson_transporter import build_lesson_router

router = build_lesson_router(
    prefix='/lessons',
    tags=['Lessons'],
    dependencies=[]
)