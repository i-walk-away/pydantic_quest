from datetime import datetime
from uuid import UUID

from src.app.domain.models.db.lesson import Lesson
from src.app.domain.models.dto.lesson import LessonDTO, CreateLessonDTO, UpdateLessonDTO
from src.app.domain.repositories.lesson import LessonRepository


class LessonService:
    def __init__(self, lesson_repository: LessonRepository):
        self.repository = lesson_repository

    async def get_by_id(self, id: UUID) -> LessonDTO:
        result = await self.repository.get(id=id)
        return result.to_dto()

    async def get_all(self) -> list[LessonDTO]:
        lessons = await self.repository.get_all()

        return [lesson.to_dto() for lesson in lessons]

    async def create(self, schema: CreateLessonDTO) -> LessonDTO:
        """
        Create new lesson.

        :param schema: DTO object containing fields needed to contstruct new Lesson.
        :return: DTO representation of created Lesson
        """
        data = schema.model_dump()

        created_now = datetime.now()

        lesson = Lesson(
            **data,
            created_at=created_now
        )

        await self.repository.add(lesson)
        await self.repository.session.commit()
        await self.repository.session.refresh(lesson)

        return lesson.to_dto()

    async def update(self, schema: UpdateLessonDTO) -> LessonDTO:
        """
        Update existing lesson.

        :param schema:
        :return:
        """
        result = await self.repository.update(
            id=schema.id,
            data=schema.model_dump(exclude_none=True)
        )

        return result.to_dto()

    async def delete(self, id: UUID) -> None:
        """
        Delete lesson from the database.

        :param id:
        :return:
        """
        await self.repository.delete(id=id)

        return
