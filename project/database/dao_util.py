from typing import Iterable

from project.database.dao import PermissionDAO, UserDAO
from project.database.models import MBase, Permission
from project.database.session import async_session_maker, engine


from project.auth_schemas import SPermissionIn, SPermissionOut, UserInDB, UserOut


async def load_permissions() -> list[SPermissionOut]:
    permissions = (
        SPermissionIn(name=perm.name, desctription=perm.value) for perm in Permission
    )
    async with async_session_maker() as session:
        permissions_dao = PermissionDAO(session)
        result = await permissions_dao.add_permissions(permissions)
        out_result = [SPermissionOut(**perm.to_dict()) for perm in result]
        await session.commit()

    return out_result


async def init_db():
    """
    Drop and create db
    """
    async with engine.begin() as connection:
        await connection.run_sync(MBase.metadata.drop_all)
        await connection.run_sync(MBase.metadata.create_all)


async def load_users(users: Iterable[UserInDB]) -> list[UserOut]:

    async with async_session_maker() as session:
        users_dao = UserDAO(session)
        users_m = await users_dao.add_new_users(users)
        out_result = [UserOut(**um.to_dict()) for um in users_m]  
        await session.commit()

    return out_result
