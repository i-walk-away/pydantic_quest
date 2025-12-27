from fastapi import APIRouter, Depends

from src.app.backend.core.dependencies.services.lesson import get_lesson_service
from src.app.backend.models.dto.lesson import LessonDTO, CreateLessonDTO
from src.app.backend.services.lesson import LessonService

#  @router.get(path='', summary='')


router = APIRouter(
    prefix='/lessons',
    tags=['Lessons'],
    dependencies=[Depends()]
)


@router.post(path='/create', summary='Create new lesson')
async def create_lesson(
        data: CreateLessonDTO,
        lesson_service: LessonService = Depends(get_lesson_service)
) -> LessonDTO:
    """
    Create lesson.

    :param lesson_service:
    :param data:
    :return:
    """
    lesson = await lesson_service.create(schema=data)

    return lesson


@router.get(path='/get_all', summary='Get all lessons')
async def get_all_lessons(
        lesson_service: LessonService = Depends(get_lesson_service)
) -> list[LessonDTO]:
    """
    Get all lessons.

    :param lesson_service:
    :return:
    """
    lessons = await lesson_service.get_all()

    return lessons


@router.get(path='/get_by_id', summary='Get lesson by id')
async def get_lesson_by_id(
        lesson_id: str,
        lesson_service: LessonService = Depends(get_lesson_service)
) -> LessonDTO:
    """
    Get lesson by id.

    :param lesson_id:
    :param lesson_service:
    :return:
    """
    lesson = await  lesson_service.get_by_id(id=lesson_id)

    return lesson
