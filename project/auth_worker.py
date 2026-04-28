from fastapi import status

from faststream import FastStream, Logger
from faststream.redis import RedisBroker
from project.auth_lib import get_password_hash, verify_password
from project.database.dao import UserDAO
from project.database.models import MUser
from project.database.session import async_session_maker
from project.auth_schemas import AuthUserData, BrokerExeption, UserBrokerResult, UserFilter, UserIn, UserInDB, UserOut
from project.config import settings

broker = RedisBroker(settings.REDIS_URL)

app = FastStream(broker)


@broker.subscriber(list='auth')
async def auth_handler(auth_data: AuthUserData, logger: Logger) -> UserBrokerResult:
    logger.info(f'auth message: {auth_data}')
    try:
        async with async_session_maker() as session:

            user = await UserDAO(session).get_user_by_name(auth_data.username)
    except Exception as e:
        return UserBrokerResult(exeption=BrokerExeption(code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()))
    if user is None: # type: ignore
        return UserBrokerResult(exeption=BrokerExeption(code=status.HTTP_401_UNAUTHORIZED, detailes="Incorrect username or password"))
    if user.disabled:
        return UserBrokerResult(exeption=BrokerExeption(code=status.HTTP_401_UNAUTHORIZED, detailes="User desabled"))
    if not verify_password(auth_data.password, user.hashed_password):
        return UserBrokerResult(exeption=BrokerExeption(code=status.HTTP_401_UNAUTHORIZED, detailes="Incorrect username or password"))

    user_dict = user.to_dict()
    user_obj = UserOut(**user_dict)
    return UserBrokerResult(result=user_obj)


@broker.subscriber(list='user')
async def get_user_handler(username: str, logger: Logger) -> UserBrokerResult:

    logger.info(f'get user handler message: username {username}')
    try:
        async with async_session_maker() as session:

            user = await UserDAO(session).get_user_by_name(username)
    except Exception as e:
        return UserBrokerResult(exeption=BrokerExeption(code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()))
    if user is None: # type: ignore
        return UserBrokerResult(exeption=BrokerExeption(code=status.HTTP_404_NOT_FOUND, detailes="User not found"))
    

    user_dict = user.to_dict()
    user_obj = UserOut(**user_dict)
    return UserBrokerResult(result=user_obj)

@broker.subscriber(list='register')
async def user_register(user_reg: UserIn, logger: Logger) -> UserBrokerResult:
    async with async_session_maker() as session:
        user_dao = UserDAO(session)
        try:
            
            user: MUser | None = await user_dao.find_one_or_none(UserFilter(username=user_reg.username, email=user_reg.email)) # type: ignore
            if user:
                return UserBrokerResult(exeption=BrokerExeption(code=status.HTTP_409_CONFLICT, detailes="User with the given name or email already exists"))
            
            hashed_password = get_password_hash(user_reg.password)
            new_user = UserInDB(hashed_password=hashed_password, **user_reg.model_dump())
            new_user_db: MUser = await user_dao.add(new_user) # type: ignore
            logger.info(f'new_user_db: {new_user_db}')
            user_dict = new_user_db.to_dict(True) # type: ignore
            await session.commit()
            logger.info(f'user_dict: {user_dict}')
        except Exception as e:
            return UserBrokerResult(exeption=BrokerExeption(code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()))
    user_obj = UserOut(**user_dict)
    return UserBrokerResult(result=user_obj)


@broker.subscriber(list='test')
async def base_handler(msg: str, logger: Logger) -> None:
    logger.info(f'test message: {msg}')

@app.after_startup
async def test():
    await broker.publish('test startup', list='test')