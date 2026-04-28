

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from project.config import settings



engine = create_async_engine(url=settings.POSTGRES_URL, echo=True)
async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, class_=AsyncSession)

async def get_session_with_commit() -> AsyncGenerator[AsyncSession, None]:
    """Async session with auto commit"""

    async with async_session_maker() as session:
        yield session
        await session.commit()
        # try:
        # except Exception:
        #     await session.rollback()
        #     raise
        # finally:
        #     await session.close()


async def get_session_without_commit() -> AsyncGenerator[AsyncSession, None]:
    """Async session without commit"""

    async with async_session_maker() as session:
        yield session
        # try:
        # except Exception:
        #     await session.rollback()
        #     raise
        # finally:
        #     await session.close()
