from faststream.redis import RedisBroker

from project.config import settings


from faststream.redis.fastapi import RedisRouter


broker_router = RedisRouter(settings.REDIS_URL)


def broker() -> RedisBroker:
    return broker_router.broker