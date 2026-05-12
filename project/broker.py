from project.config import settings


from faststream.redis import RedisBroker


broker = RedisBroker(settings.REDIS_URL)