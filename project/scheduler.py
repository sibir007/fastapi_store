from apscheduler import AsyncScheduler

from project.database.session import engine

from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
from apscheduler.eventbrokers.redis import RedisEventBroker


from project.config import settings




data_store = SQLAlchemyDataStore(engine)
event_broker = RedisEventBroker(client_or_url=settings.REDIS_URL)
async_scheduler = AsyncScheduler(data_store=data_store, event_broker=event_broker)
