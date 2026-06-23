
from project.database.models_base import *
from project.database.models_base import MBase
from project.database.models_cart import *
from project.database.models_order import *
from project.database.models_store import *
from project.database.models_auth import *
from project.database.session import engine


async def init_db():
    """
    Drop and create db
    """
    async with engine.begin() as connection:
        await connection.run_sync(MBase.metadata.drop_all)
        await connection.run_sync(MBase.metadata.create_all)



