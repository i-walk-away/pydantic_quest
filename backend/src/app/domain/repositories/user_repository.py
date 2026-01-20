from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.exceptions.base_exc import NotFoundError
from src.app.domain.models.db.user import User
from src.app.domain.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        """
        Initialize user repository.

        :param session: database session

        :return: None
        """
        super().__init__(
            session=session,
            model=User
        )

    async def get_by_username(self, username: str) -> User:
        """
        Get user by username

        :param username: username

        :return: User object
        """
        stmt = select(User).where(User.username == username)
        result = await self.session.scalar(stmt)

        if result is None:
            raise NotFoundError(
                entity_type_str=self.model_name_str,
                field_name="username",
                field_value=username
            )

        return result
