from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.domain.models.db.user import User
from src.app.domain.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize user repository.

        :param session: database session

        :return: None
        """
        super().__init__(
            session=session,
            model=User,
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

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email.

        :param email: user email

        :return: User object
        """
        stmt = select(User).where(User.email == email)
        result = await self.session.scalar(stmt)

        return result

    async def get_by_github_id(self, github_id: int) -> User | None:
        """
        Get user by GitHub id.

        :param github_id: GitHub user id

        :return: User object
        """
        stmt = select(User).where(User.github_id == github_id)
        result = await self.session.scalar(stmt)

        return result
