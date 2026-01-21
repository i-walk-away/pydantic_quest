from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def get_by_username(self, username: str) -> User | None:
        """
        Get user by username

        :param username: username

        :return: User object
        """
        stmt = select(User).where(User.username == username)
        result = await self.session.scalar(stmt)

        return result
