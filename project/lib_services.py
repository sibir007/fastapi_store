from project.schemas import SUsername
from project.exceptions import HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION, raise_exaption
from project.schemas_broker import (
    SServiceResoultBase,
    SServiceExeption,
    SCartServiceResult,
    SProductsSummaryOutByerServiceResoult,
    SVerifyReqversServiceResult,
)


from fastapi import status
from faststream import Logger
from faststream.redis import RedisBroker, RedisChannelMessage
from pydantic import BaseModel


from typing import Any

from project.schemas_cart import SCart, SUserCart
from project.schemas_products import SNomId
import logging

logger = logging.getLogger(__name__)


async def get_service_resoult[T](
    broker: RedisBroker,
    req: BaseModel,
    queue_name: str,
    broker_result_class: type[T],
    logger: Logger,
) -> T:

    try:
        mess: RedisChannelMessage = await broker.request(req, list=queue_name)
        res_: None | dict[str, Any] = await mess.decode()
    except Exception as e:
        logger.error(f"exeptionon in get_service_resoult: {e.__str__()}")
        return broker_result_class(
            exeption=SServiceExeption(  # type: ignore
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )  # type: ignore
    if res_ is None:
        logger.error(f"user service result is None")
        return broker_result_class(
            exeption=SServiceExeption(  # type: ignore
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detailes="user service result is None",
            )
        )  # type: ignore
    res = broker_result_class(**res_)
    if res.resoult and res.exeption:  # type: ignore
        logger.error(
            f"user service result error, incompatible service state resoult and exeption is True"
        )
        return broker_result_class(
            exeption=SServiceExeption(  # type: ignore
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detailes="user service result error, incompatible service state resoult and exeption is True",
            )
        )  # type: ignore

    if res.resoult is None and res.exeption is None:  # type: ignore
        logger.error(
            f"user service result error, incompatible service state resoult and exeption is None"
        )
        return broker_result_class(
            exeption=SServiceExeption(  # type: ignore
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detailes="user service result error, incompatible service state resoult and exeption is None",
            )  # type: ignore
        )

    return res


async def  get_service_resoult_or_raise_http_exaption[T](
    broker: RedisBroker,
    req: BaseModel,
    queue_name: str,
    broker_result_class: type[SServiceResoultBase[T]],
) -> T:

    try:
        broker_response = await broker.request(req, list=queue_name)
        broker_resoult: dict[str, Any] | None = await broker_response.decode()
        # mess: RedisChannelMessage = await broker.request(req, list=queue_name)
        # res_: None | dict[str, Any] = await mess.decode()
        # logger.error(f"broker res: {broker_resoult}, class {broker_result_class}")
    except Exception as e:
        # raise e
        logger.error(f"exeptionon in get_service_resoult_or_raise_http_exaption: {e.__str__()}")
        raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION(detail=e.__str__())

    if broker_resoult is None:
        logger.error(f"exeptionon in get_service_resoult_or_raise_http_exaption res None")
        raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION(detail="broker_sesoult None")
    broker_resoult_obj = broker_result_class(**broker_resoult)
    if broker_resoult_obj.exeption:
        logger.error(f"exeptionon in get_service_resoult_or_raise_http_exaption broker_resoult_obj.exeption ditails: {broker_resoult_obj.exeption.detailes}")
        raise_exaption(
            broker_resoult_obj.exeption.code, broker_resoult_obj.exeption.detailes
        )

    res = broker_resoult_obj.resoult
    if res is None:  # should not happen, but just in case
        logger.error(f"exeptionon in get_service_resoult_or_raise_http_exaption broker_resoult_obj.resoult None")
        raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION(
            "Internal server error during user retrieval, incompatible service state"
        )

    return res


async def verify_product_service_request(
    nom_id: int, broker: RedisBroker, logger: Logger
):
    broker_resoult: SVerifyReqversServiceResult = await get_service_resoult(
        broker,
        SNomId(nom_id=nom_id),
        "verify-product",
        SVerifyReqversServiceResult,
        logger,
    )

    return broker_resoult


async def verify_user_service_request(
    username: str,
    broker: RedisBroker,
    logger: Logger,
) -> SVerifyReqversServiceResult:
    broker_resoult: SVerifyReqversServiceResult = await get_service_resoult(
        broker,
        SUsername(username=username),
        "verify-user",
        SVerifyReqversServiceResult,
        logger,
    )

    return broker_resoult



async def clear_cart_service_request(
    cart: SUserCart, broker: RedisBroker, logger: Logger
) -> SVerifyReqversServiceResult:
    broker_resoult: SVerifyReqversServiceResult = await get_service_resoult(
        broker,
        cart,
        "clear-cart",
        SVerifyReqversServiceResult,
        logger,
    )

    return broker_resoult


async def restore_cart_service_request(
    cart: SUserCart, broker: RedisBroker, logger: Logger
) -> SVerifyReqversServiceResult:
    broker_resoult: SVerifyReqversServiceResult = await get_service_resoult(
        broker,
        cart,
        "restore-cart",
        SVerifyReqversServiceResult,
        logger,
    )

    return broker_resoult



async def get_cart_service_request(
    username: SUsername, broker: RedisBroker, logger: Logger
) -> SCartServiceResult:
    broker_resoult: SCartServiceResult = await get_service_resoult(
        broker,
        username,
        "get-cart",
        SCartServiceResult,
        logger,
    )

    return broker_resoult


async def get_products_for_order_service_request(
    cart: SCart, broker: RedisBroker, logger: Logger
):
    broker_resoult: SProductsSummaryOutByerServiceResoult = await get_service_resoult(
        broker,
        cart,
        "products-for-order",
        SProductsSummaryOutByerServiceResoult,
        logger,
    )
    return broker_resoult
