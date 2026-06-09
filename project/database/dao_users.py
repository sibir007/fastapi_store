from typing import Generator, Iterable, cast

from sqlalchemy import select


from project.database.dao import (
    BaseDAO,
    logger,
)
from project.database.dao import clear_table
from project.database.models_auth import MPayment, MPermission
from project.database.models_auth import MUser, Permission
from project.database.session import async_session


from project.schemas_auth import (
    SPaymentInDB,
    SPaymentOut,
    SPermissionIn,
    SPermissionOut,
    STopup,
    STopupOut,
    SUserWithoutPermission,
    UserFilter,
    SUserInDB,
    SUserOut,
)


class PermissionDAO(BaseDAO[MPermission]):
    model = MPermission

    async def add_permissions(
        self, permissions: Iterable[SPermissionIn]
    ) -> list[MPermission]:
        return await self.add_many(permissions)

    async def add_permission(self, permission: SPermissionIn) -> MPermission:
        return await self.add(permission)


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


class UserDAO(BaseDAO[MUser]):
    model = MUser

    async def get_user_by_name(self, username: str) -> MUser | None:

        user: MUser | None = cast(
            MUser, await self.find_one_or_none(filters=UserFilter(username=username))
        )
        return user

    async def add_new_users(self, users: Iterable[SUserInDB]) -> list[MUser]:
        return await self.add_many(users)

    async def add_permission_to_user(self, username: str, permission: SPermissionIn):

        user: MUser | None = await self.find_one_or_none(
            filters=UserFilter(username=username)
        )
        if not user:
            logger.error(f"Пользователь с именем {username} не найден.")
            raise ValueError(f"Пользователь с именем {username} не найден.")

        permission_dao = PermissionDAO(self._session)
        perm: MPermission | None = await permission_dao.find_one_or_none(
            filters=SPermissionIn(name=permission.name)
        )
        if not perm:
            logger.error(f"Разрешение {permission.name} не найдено.")
            raise ValueError(f"Разрешение {permission.name} не найдено`.")

        if perm in user.permissions:
            logger.warning(
                f"Пользователь {username} уже имеет разрешение {permission.name}."
            )
            return user

        user.permissions.append(perm)
        await self._session.flush()
        user.permissions
        return user

    async def add_permissions_to_user(
        self, username: str, permissions: Iterable[SPermissionIn]
    ):

        user: MUser | None = await self.find_one_or_none(
            filters=UserFilter(username=username)
        )
        if not user:
            logger.error(f"Пользователь с именем {username} не найден.")
            raise ValueError(f"Пользователь с именем {username} не найден.")

        permission_dao = PermissionDAO(self._session)
        for permission in permissions:
            perm: MPermission | None = await permission_dao.find_one_or_none(
                filters=SPermissionIn(name=permission.name)
            )
            if not perm:
                logger.error(f"Разрешение {permission} не найдено.")
                continue
            if perm in user.permissions:
                logger.warning(
                    f"Пользователь {username} уже имеет разрешение {permission}."
                )
                continue
            user.permissions.append(perm)
            await self._session.flush()
        return user


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


async def topup_none_if_user_not_found(topup: STopup) -> STopupOut | None:
    async with async_session() as session:
        users_dao = UserDAO(session)
        user_m = await users_dao.get_user_by_name(topup.username)
        if not user_m:
            return None
        user_m.balance += topup.ammount
        await session.commit()
        topup_out = STopupOut(topup=topup.ammount, balance=user_m.balance)
    return topup_out


async def get_users_without_permissions() -> list[SUserWithoutPermission]:
    async with async_session() as sesion:
        users_res = await sesion.scalars(select(MUser))
        users_list = users_res.all()
        users_out_list = [SUserWithoutPermission.model_validate(u) for u in users_list]
    return users_out_list

async def get_users_names() -> list[str]:
    return [n.username for n in await get_users_without_permissions()]


async def applay_payment(payment: SPaymentInDB) -> SPaymentOut:
    async with async_session() as session:
        stm = (
            select(MUser)
            .where(MUser.username == payment.username)
        )
        result = await session.execute(stm)
        user_m = result.scalar_one()
        if user_m.balance < payment.ammount:
            raise ValueError(
                f"Not enough funds on {payment.username}'s balance. Current balance: {user_m.balance}, required: {payment.ammount}"
            )
        user_m.balance -= payment.ammount
        payment_in = MPayment(
                username=payment.username,
                order_id=payment.order_id,
                sale_id=payment.sale_id,
                ammount=payment.ammount,
            ) 
        session.add(
            payment_in
        )
        await session.flush()
        payment_out = SPaymentOut.model_validate(payment_in)
        await session.commit()
    return payment_out

async def add_permission_to_user(username: str, permission: Permission) -> SUserOut:
    async with async_session() as session:
        user_m = await UserDAO(session).add_permission_to_user(username, SPermissionIn(name=permission.name))
        await session.commit()
        ps: list[str] = [p.name.name for p in user_m.permissions]
        return SUserOut(**user_m.to_dict(), permissions=ps)