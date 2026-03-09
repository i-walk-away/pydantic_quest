from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.cfg.cfg import settings

engine = create_async_engine(settings.database.url)
session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    Yields a new SQLAlchemy AsynsSession.

    :return: async session generator
    """
    async with session_factory() as session:
        yield session
