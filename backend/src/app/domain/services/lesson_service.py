from uuid import UUID

from src.app.domain.models.db.lesson import Lesson
from src.app.domain.models.dto.lesson import CreateLessonDTO, LessonDTO, UpdateLessonDTO
from src.app.domain.repositories.lesson_repository import LessonRepository


class LessonService:
    def __init__(self, lesson_repository: LessonRepository):
        """
        Initialize lesson service.

        :param lesson_repository: lesson repository

        :return: None
        """
        self.repository = lesson_repository

    async def get_by_id(self, id: UUID) -> LessonDTO | None:
        """
        Get lesson by id.

        :param id: lesson id

        :return: lesson dto
        """
        result = await self.repository.get(id=id)
        return result.to_dto()

    async def get_all(self) -> list[LessonDTO]:
        """
        Get all lessons sorted by lesson.order

        :return: lesson list
        """
        lessons = await self.repository.get_all()

        ordered_lessons = sorted(lessons, key=lambda lesson: lesson.order)

        return [lesson.to_dto() for lesson in ordered_lessons]

    async def create(self, schema: CreateLessonDTO) -> LessonDTO:
        """
        Create new lesson.

        :param schema: DTO object containing fields needed to construct new Lesson

        :return: DTO representation of created Lesson
        """
        data = schema.model_dump()

        lesson = Lesson(
            **data
        )

        await self.repository.add(lesson)
        await self.repository.session.commit()
        await self.repository.session.refresh(lesson)

        return lesson.to_dto()

    async def update(self, id: UUID, schema: UpdateLessonDTO) -> LessonDTO:
        """
        Update existing lesson.

        :param id: lesson id
        :param schema: lesson update data

        :return: updated lesson
        """
        result = await self.repository.update(
            id=id,
            data=schema.model_dump(exclude_none=True)
        )

        return result.to_dto()

    async def delete(self, id: UUID) -> bool:
        """
        Delete lesson from the database.

        :param id: lesson id

        :return: ``True`` if lesson was deleted
        """
        deleted = await self.repository.delete(id=id)
        await self.repository.session.commit()

        return deleted
