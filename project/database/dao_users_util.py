from typing import Generator, Iterable


from project.database.dao import (
    MPermission,
    PermissionDAO,
    UserDAO,
)
from project.database.dao_util import clear_table # type: ignore
from project.database.models import MUser, Permission
from project.database.session import async_session


from project.auth_schemas import (
    SPermissionIn,
    SPermissionOut,
    UserFilter,
    SUserInDB,
    SUserOut,
)


async def load_permissions() -> Generator[SPermissionOut, None, None]:
    permissions = (
        SPermissionIn(name=perm.name, desctription=perm.value) for perm in Permission
    )
    async with async_session() as session:
        permissions_dao = PermissionDAO(session)
        result = await permissions_dao.add_permissions(permissions)
        await session.commit()
        out_result = (SPermissionOut(**perm.to_dict()) for perm in result)

    return out_result


async def get_user_by_name(username: str) -> SUserOut | None:
    async with async_session() as session:
        user_m = await UserDAO(session).get_user_by_name(username)
        if user_m is None:
            return None
        ps: list[str] = [p.name.name for p in user_m.permissions]
        out_result = SUserOut(**user_m.to_dict(), permissions=ps)
    return out_result


async def get_user_by_name_with_pass_hash(
    username: str,
) -> tuple[SUserOut, str] | tuple[None, None]:
    async with async_session() as session:
        user_m = await UserDAO(session).get_user_by_name(username)
        if user_m is None:
            return None, None
        ps: list[str] = [p.name.name for p in user_m.permissions]
        out_result = (
            SUserOut(**user_m.to_dict(), permissions=ps),
            user_m.hashed_password,
        )
    return out_result


async def clear_users_table() -> None:
    await clear_table(MUser)


async def clear_permissions_table() -> None:
    await clear_table(MPermission)


async def clear_and_resave_permissions() -> None:
    await clear_permissions_table()
    await load_permissions()


async def create_users(users: Iterable[SUserInDB]) -> list[SUserOut]:

    async with async_session() as session:
        users_m_list: Iterable[MUser] = (MUser(**u.model_dump()) for u in users)
        session.add_all(users_m_list)
        # users_dao = UserDAO(session)
        # users_m = await users_dao.add_new_users(users)
        await session.commit()
        out_result = [SUserOut(**um.to_dict()) for um in users_m_list]

    return out_result


async def create_user(user: SUserInDB) -> SUserOut | None:

    async with async_session() as session:

        users_dao = UserDAO(session)
        # user_m = await users_dao.get_user_by_name(user.username)
        users_m = await users_dao.find_all(
            UserFilter(username=user.username, email=user.email)
        )
        if users_m:
            return None
        user_m = await users_dao.add(user)
        out_result = SUserOut(**user_m.to_dict())
        await session.commit()

    return out_result


async def create_update_superuser(superuser: SUserInDB) -> SUserOut:

    async with async_session() as session:
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
            user_m = await users_dao.add(superuser)
        # await session.flush()
        user_m = await users_dao.get_user_by_name("superuser")
        permissions_dao = PermissionDAO(session)
        all_permissions = await permissions_dao.find_all()
        # user_m = await users_dao.get_user_by_name("superuser")
        user_m.permissions.extend(all_permissions)  # type: ignore
        await session.commit()

        ps: list[str] = [p.name.name for p in user_m.permissions]  # type: ignore
        out_result = SUserOut(**user_m.to_dict(), permissions=ps)  # type: ignore

    return out_result


