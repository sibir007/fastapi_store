

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from project.config import settings



engine = create_async_engine(url=settings.POSTGRES_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)