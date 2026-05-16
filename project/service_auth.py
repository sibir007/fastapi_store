from fastapi import status

from faststream import Logger
from project.schemas import SBool
from project.schemas_broker import SBrokerExeption, STopupBrokerResult, SUserBrokerResult, SVerifyReqversBrokerResult
from project.lib_auth import get_password_hash, verify_password
from project.database.dao_users_util import create_user, get_user_by_name, get_user_by_name_with_pass_hash, topup_none_if_user_not_found
from project.schemas_auth import (
    AuthUserData,
    STopup,
    SUserIn,
    SUserInDB,
    SUserName,
    SUserOut,
)
from project.broker import broker
from project.service import service



@broker.subscriber(list="auth")
async def auth_handler(auth_data: AuthUserData, logger: Logger) -> SUserBrokerResult:
    logger.info(f"auth message: {auth_data}")
    try:
        user, pass_hash = await get_user_by_name_with_pass_hash(auth_data.username)
    except Exception as e:
        return SUserBrokerResult(
            exeption=SBrokerExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    if user is None: 
        return SUserBrokerResult(
            exeption=SBrokerExeption(
                code=status.HTTP_401_UNAUTHORIZED,
                detailes="Incorrect username or password",
            )
        )
    if user.disabled:
        return SUserBrokerResult(
            exeption=SBrokerExeption(
                code=status.HTTP_401_UNAUTHORIZED, detailes="User desabled"
            )
        )
    if not verify_password(auth_data.password, pass_hash): # type: ignore
        return SUserBrokerResult(
            exeption=SBrokerExeption(
                code=status.HTTP_401_UNAUTHORIZED,
                detailes="Incorrect username or password",
            )
        )

    return SUserBrokerResult(resoult=user)


@broker.subscriber(list="user")
async def get_user_handler(username: SUserName, logger: Logger) -> SUserBrokerResult:

    logger.info(f"get user handler message: username {username}")
    try:
        user = await get_user_by_name(username.username)
    except Exception as e:
        return SUserBrokerResult(
            exeption=SBrokerExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    if user is None:
        return SUserBrokerResult(
            exeption=SBrokerExeption(
                code=status.HTTP_404_NOT_FOUND, detailes="User not found"
            )
        )

    return SUserBrokerResult(resoult=user)

@broker.subscriber(list="verify-user")
async def verify_user_handler(username: SUserName, logger: Logger) -> SVerifyReqversBrokerResult:

    logger.info(f"verify user handler message: username {username}")
    try:
        user = await get_user_by_name(username.username)
    except Exception as e:
        return SVerifyReqversBrokerResult(
            exeption=SBrokerExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    if user is None:
        return SVerifyReqversBrokerResult(resoult=SBool(result=False))
        
    return SVerifyReqversBrokerResult(resoult=SBool(result=True))



@broker.subscriber(list="topup")
async def topup_handler(topup: STopup, logger: Logger) -> STopupBrokerResult:

    logger.info(f"topup handler message: username {topup.username}, ammount {topup.ammount}")
    try:
        topup_out = await topup_none_if_user_not_found(topup)
    except Exception as e:
        return STopupBrokerResult(
            exeption=SBrokerExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    if topup_out is None:
        return STopupBrokerResult(
            exeption=SBrokerExeption(
                code=status.HTTP_404_NOT_FOUND, detailes="User not found"
            )
        )

    return STopupBrokerResult(resoult=topup_out)


# @broker.subscriber(list="register")
# async def user_register_handler(user_reg: UserIn, logger: Logger) -> UserBrokerResult:
#     async with async_session_maker() as session:
#         user_dao = UserDAO(session)
#         try:

#             user: MUser | None = await user_dao.find_one_or_none(UserFilter(username=user_reg.username, email=user_reg.email))  # type: ignore
#             if user:
#                 return UserBrokerResult(
#                     exeption=BrokerExeption(
#                         code=status.HTTP_409_CONFLICT,
#                         detailes="User with the given name or email already exists",
#                     )
#                 )

#             hashed_password = get_password_hash(user_reg.password)
#             new_user = SUserInDB(
#                 hashed_password=hashed_password, **user_reg.model_dump()
#             )
#             new_user_db: MUser = await user_dao.add(new_user)  # type: ignore
#             logger.info(f"new_user_db: {new_user_db}")
#             user_dict = new_user_db.to_dict(True)  # type: ignore
#             await session.commit()
#             logger.info(f"user_dict: {user_dict}")
#         except Exception as e:
#             return UserBrokerResult(
#                 exeption=BrokerExeption(
#                     code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
#                 )
#             )
#     user_obj = SUserOut(**user_dict)
#     return UserBrokerResult(result=user_obj)


@broker.subscriber(list="register")
async def user_register_handler(user_reg: SUserIn, logger: Logger) -> SUserBrokerResult:
    user_dict = user_reg.model_dump()
    user_db = SUserInDB(
        hashed_password=get_password_hash(user_dict.get("password", "")), **user_dict
    )
    try:
        user_out: SUserOut | None = await create_user(user_db)
        if user_out is None:
            return SUserBrokerResult(
                exeption=SBrokerExeption(
                    code=status.HTTP_409_CONFLICT,
                    detailes="User with the given name or email already exists",
                )
            )

        logger.info(f"user_out: {user_out}")
    except Exception as e:
        return SUserBrokerResult(
            exeption=SBrokerExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    return SUserBrokerResult(resoult=user_out)


@broker.subscriber(list="test")
async def base_handler(msg: str, logger: Logger) -> None:
    logger.info(f"test message: {msg}")


@service.after_startup
async def test():
    await broker.publish("test startup", list="test")
