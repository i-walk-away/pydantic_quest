from typing import TypeVar
from uuid import UUID

from sqlalchemy import select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.backend.core.exceptions.repositories.repository_exc import NotFoundError
from src.app.backend.models.db import Base

Model = TypeVar("Model", bound=Base)


class BaseRepository[Model]:
    def __init__(
            self,
            session: AsyncSession,
            model: type[Model]
    ):
        self.session = session
        self.model = model
        self.model_name = self.model.__name__

    async def get(self, id: UUID) -> Model | None:
        stmt = select(self.model).where(self.model.id == id)  # type: ignore
        result = await self.session.scalar(stmt)

        if result is None:
            raise NotFoundError(
                entity_type=self.model_name,
                id=id
            )
        return result

    async def get_all(self) -> list[Model]:
        stmt = select(self.model)
        result = await self.session.scalars(stmt)

        return list(result.unique())

    async def delete(self, id: UUID) -> None:
        item = await self.get(id=id)
        await self.session.delete(item)

        return

    async def update(self, id: UUID, data: dict) -> Model | None:
        item = await self.get(id=id)

        stmt = sql_update(item).values(**data)
        await self.session.execute(stmt)

        return await self.get(id=id)
