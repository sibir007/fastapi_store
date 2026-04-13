from faststream import FastStream, Logger
from faststream.redis import RedisBroker
from project.config import settings

broker = RedisBroker(settings.REDIS_URL)

app = FastStream(broker)

@broker.subscriber(list='test')
async def base_handler(msg: str, logger: Logger) -> None:
    logger.info(f'test message: {msg}')

@app.after_startup
async def test():
    await broker.publish('test startup', list='test')