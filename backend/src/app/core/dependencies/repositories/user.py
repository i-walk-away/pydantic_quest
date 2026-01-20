from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.dependencies.db import get_session
from src.app.domain.repositories import UserRepository


def get_user_repository(
        session: AsyncSession = Depends(get_session)
) -> UserRepository:
    """
    Constructs an instance of UserRepository with SQLA Async Session injected.

    :param session: database session

    :return: user repository
    """

    return UserRepository(session=session)
