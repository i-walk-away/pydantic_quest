from sqlalchemy import select

from src.app.backend.models.db.lesson import Lesson
from src.app.backend.repositories.base import BaseRepository


class LessonRepository(BaseRepository):
    async def add(self, model: Lesson) -> None:
        self.session.add(model)

    async def get_all(self) -> list[Lesson]:
        statement = select(Lesson)
        result = await self.session.scalars(statement)

        return list(result.unique())

    async def get_by_id(self, id: str) -> Lesson | None:
        statement = select(Lesson).where(Lesson.id == id)
        result = await self.session.scalar(statement)

        return result

    async def delete(self, id: str) -> bool:
        statement = select(Lesson).where(Lesson.id == id)
        result = await self.session.delete(statement)

        return result