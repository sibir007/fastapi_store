from typing import Iterable, cast

from project.database.dao import PermissionDAO, UserDAO
from project.database.models import MBase, MPermission, Permission, MUser
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


async def create_users(users: Iterable[UserInDB]) -> list[UserOut]:

    async with async_session_maker() as session:
        users_dao = UserDAO(session)
        users_m = await users_dao.add_new_users(users)
        out_result = [UserOut(**um.to_dict()) for um in users_m]  
        await session.commit()

    return out_result


async def create_update_superuser(superuser: UserInDB) -> UserOut:

    async with async_session_maker() as session:
        users_dao = UserDAO(session)
        user_m = await users_dao.get_user_by_name("superuser")
        if user_m:
            user_m.full_name = superuser.full_name
            user_m.email = superuser.email
            user_m.hashed_password = superuser.hashed_password
            user_m.disabled = False
            user_m.permissions.clear()
            await session.flush()
        else:
            user_m = cast(MUser,await users_dao.add(superuser))
        # await session.flush()
        user_m = cast(MUser, await users_dao.get_user_by_name("superuser"))
        permissions_dao = PermissionDAO(session)
        all_permissions = cast(Iterable[MPermission], await permissions_dao.find_all())
        # user_m = await users_dao.get_user_by_name("superuser")
        user_m.permissions.extend(all_permissions)
        await session.commit()
        # user_m = await users_dao.get_user_by_name("superuser")
        # user_m = cast(MUser, await users_dao.get_user_by_name("superuser"))
        ps: list[str] = [p.name.name for p in user_m.permissions]
        out_result = UserOut(**user_m.to_dict(), permissions=ps)

    return out_result