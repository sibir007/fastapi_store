from faststream.redis import RedisBroker

from project.config import settings


from faststream.redis.fastapi import RedisRouter

# import logging

# logger = logging.Logger(__name__)

# logger.info(settings.model_dump_json())

# broker_router = RedisRouter(settings.REDIS_URL)


# def broker() -> RedisBroker:
#     return broker_router.broker