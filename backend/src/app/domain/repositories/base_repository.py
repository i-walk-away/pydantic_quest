from typing import TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.exceptions.base_exc import NotFoundError
from src.app.domain.models.db import Base

Model = TypeVar("Model", bound=Base)


class BaseRepository[Model]:
    def __init__(
            self,
            session: AsyncSession,
            model: type[Model]
    ):
        """
        Initialize repository with session and model.

        :param session: database session
        :param model: model class

        :return: None
        """
        self.session = session
        self.model = model
        self.model_name_str = self.model.__name__

    async def get(self, id: UUID) -> Model:
        """
        Get object from database by id.

        :param id: Object id

        :return: Object
        """
        stmt = select(self.model).where(self.model.id == id)  # type: ignore
        result = await self.session.scalar(stmt)

        if result is None:
            raise NotFoundError(
                entity_type_str=self.model_name_str,
                field_name="id",
                field_value=id
            )

        return result

    async def get_all(self) -> list[Model]:
        """
        Get all objects from the database

        :return: List of all objects from the database
        """
        stmt = select(self.model)
        result = await self.session.scalars(stmt)

        return list(result.unique())

    async def add(self, model: Model) -> None:
        """
        Add a model instance to the session.

        :param model: model instance

        :return: None
        """
        self.session.add(model)

    async def delete(self, id: UUID) -> bool:
        """
        Delete an object by id.

        :param id: object id

        :return: ``True`` if object was found and deleted
        """
        item = await self.get(id=id)
        await self.session.delete(item)

        return True

    async def update(self, id: UUID, data: dict[str, object]) -> Model:
        """
        Update an existing object

        :param id: Object's id
        :param data: Dictionary containing updated fields

        :return: Updated object
        """
        if not data:
            return await self.get(id=id)

        item = await self.get(id=id)

        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)

        return item
