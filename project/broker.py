from typing import Any

from faststream import Logger
from pydantic import BaseModel


from project.config import settings


from faststream.redis import RedisBroker, RedisChannelMessage

from project.exceptions import HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION, raise_exaption
from project.schemas_broker import SBorkerResoultBase, SBrokerExeption
from fastapi import status

broker = RedisBroker(settings.REDIS_URL)

async def get_broker_resoult[T](
        broker: RedisBroker,
        req: BaseModel,
        queue_name: str,
        broker_result_class: type[T],
        logger: Logger
        ) -> T:

    try:
        mess: RedisChannelMessage = await broker.request(req, list=queue_name)
        res_: None | dict[str, Any] = await mess.decode()
    except Exception as e:
        logger.error(f"exeptionon in get_broker_resoult: {e.__str__()}")
        return broker_result_class( 
            exeption=SBrokerExeption( # type: ignore
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        ) # type: ignore
    if res_ is None:
        logger.error(f"user broker result is None") 
        return broker_result_class(
            exeption=SBrokerExeption( # type: ignore
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes="user broker result is None"
            )
        ) # type: ignore
    res = broker_result_class(**res_)
    if res.resoult and res.exeption: # type: ignore
        logger.error(f"user broker result error, incompatible service state resoult and exeption is True") 
        return broker_result_class(
            exeption=SBrokerExeption( # type: ignore
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes="user broker result error, incompatible service state resoult and exeption is True"
            ) 
        ) # type: ignore
    
    if res.resoult is None and res.exeption is None: # type: ignore
        logger.error(f"user broker result error, incompatible service state resoult and exeption is None") 
        return broker_result_class(
            exeption=SBrokerExeption( # type: ignore
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes="user broker result error, incompatible service state resoult and exeption is None"
            ) # type: ignore
        )
    
    return res
    
    


async def get_broker_resoult_or_raise_http_exaption[T](
        broker: RedisBroker,
        req: BaseModel,
        queue_name: str,
        broker_result_class: type[SBorkerResoultBase[T]]
        ) -> T:
    
    try:
        broker_response = await broker.request(req, list=queue_name)
        broker_resoult: dict[str, Any] | None = await broker_response.decode()
        # mess: RedisChannelMessage = await broker.request(req, list=queue_name)
        # res_: None | dict[str, Any] = await mess.decode()
    except Exception as e:
        # logger.error(f"exeptionon in get_broker_resoult_or_raise_http_exaption: {e.__str__()}")
        raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION(detail=e.__str__())



    # broker_response = await broker.request(req, list=queue_name)
    # broker_resoult: dict[str, Any] | None = await broker_response.decode()

    if broker_resoult is None:
        raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION()
    broker_resoult_obj = broker_result_class(**broker_resoult)
    if broker_resoult_obj.exeption:
        raise_exaption(
            broker_resoult_obj.exeption.code, broker_resoult_obj.exeption.detailes
        )

    res = broker_resoult_obj.resoult
    if res is None:  # should not happen, but just in case
        raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION(
            "Internal server error during user retrieval, incompatible service state"
        )

    return res