from sqlalchemy import delete

from project.database.models import MBase
from project.database.session import async_session, engine


async def init_db():
    """
    Drop and create db
    """
    async with engine.begin() as connection:
        await connection.run_sync(MBase.metadata.drop_all)
        await connection.run_sync(MBase.metadata.create_all)


async def clear_table(table_type):  # type: ignore
    """clear table"""
    async with async_session() as session:
        statement = delete(table_type)  # type: ignore
        await session.execute(statement)
        await session.commit()