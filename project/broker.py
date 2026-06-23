from contextlib import asynccontextmanager
from typing import AsyncGenerator

from project.config import settings


from faststream.redis import RedisBroker

broker = RedisBroker(settings.REDIS_URL)


@asynccontextmanager
async def get_started_broker() -> AsyncGenerator[RedisBroker, None]:
    await broker.start()
    yield broker
    await broker.stop()
