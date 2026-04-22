from faststream import FastStream, Logger
from faststream.redis import RedisBroker
from project.auth_lib import AuthResoult, authenticate_user
from project.auth_schemas import AuthUserData
from project.config import settings

broker = RedisBroker(settings.REDIS_URL)

app = FastStream(broker)


@broker.subscriber(list='auth')
async def auth_handler(auth_data: AuthUserData, logger: Logger) -> AuthResoult:
    logger.info(f'auth message: {auth_data}')
    # logger.info(f'auth message: {msg}')
    return await authenticate_user(auth_data.username, auth_data.password)

@broker.subscriber(list='test')
async def base_handler(msg: str, logger: Logger) -> None:
    logger.info(f'test message: {msg}')

@app.after_startup
async def test():
    await broker.publish('test startup', list='test')