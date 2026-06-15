from faststream import FastStream, Logger


from project.broker import broker

service = FastStream(broker)


# from project.broker_router import broker as get_brocker

# from faststream.redis import RedisBroker


# from faststream import FastStream, Logger


# broker: RedisBroker = get_brocker()
# service = FastStream(broker)


@service.after_startup
async def test():
    await broker.publish("test startup", list="test")


@broker.subscriber(list="test")
async def base_handler(msg: str, logger: Logger) -> None:
    logger.info(f"test message: {msg}")
