from typing import TypeVar
from uuid import UUID

from sqlalchemy import select
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

    async def add(self, model: Model) -> None:
        self.session.add(model)

    async def delete(self, id: UUID) -> None:
        item = await self.get(id=id)
        await self.session.delete(item)

        return

    async def update(self, id: UUID, data: dict) -> Model | None:
        """
        Update an existing object.

        :param id: Object's id.
        :param data: Dictionary contining updated fields.
        
        :return: Updated object.
        """
        if not data:
            return await self.get(id=id)

        item = await self.get(id=id)

        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)

        return item
