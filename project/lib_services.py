from project.schemas import SUsername
from project.exceptions import HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION, raise_exaption
from project.schemas_broker import (
    SOrderServiceResult,
    SSaleInStoreServiceResult,
    SServiceResoultBase,
    SServiceExeption,
    SCartServiceResult,
    SProductsSummaryOutByerServiceResoult,
    SVerifyReqversServiceResult,
)

from project.schemas_cart import SCart, SUserCart
from project.schemas_orders import SOrderOut
from project.schemas_store import SNomId, SSaleIn
from project.schemas_orders import SOrderId
from project.broker import get_started_broker, broker

from fastapi import status
from faststream import Logger
from faststream.redis import RedisChannelMessage
from pydantic import BaseModel


from typing import Any

import logging


logger = logging.getLogger(__name__)


async def get_service_resoult[T](
    req: BaseModel,
    queue_name: str,
    broker_result_class: type[T],
    logger: Logger,
) -> T:


    # async with get_started_broker() as broker:
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


async def get_service_resoult_or_raise_http_exaption[T](
    req: BaseModel,
    queue_name: str,
    broker_result_class: type[SServiceResoultBase[T]],
) -> T:

    async with get_started_broker() as broker:
        try:
            broker_response = await broker.request(req, list=queue_name)
            broker_resoult: dict[str, Any] | None = await broker_response.decode()
            # mess: RedisChannelMessage = await broker.request(req, list=queue_name)
            # res_: None | dict[str, Any] = await mess.decode()
            # logger.error(f"broker res: {broker_resoult}, class {broker_result_class}")
        except Exception as e:
            # raise e
            logger.error(
                f"exeptionon in get_service_resoult_or_raise_http_exaption: {e.__str__()}"
            )
            raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION(detail=e.__str__())

        if broker_resoult is None:
            logger.error(
                f"exeptionon in get_service_resoult_or_raise_http_exaption res None"
            )
            raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION(detail="broker_sesoult None")
        broker_resoult_obj = broker_result_class(**broker_resoult)
        if broker_resoult_obj.exeption:
            logger.error(
                f"exeptionon in get_service_resoult_or_raise_http_exaption broker_resoult_obj.exeption ditails: {broker_resoult_obj.exeption.detailes}"
            )
            raise_exaption(
                broker_resoult_obj.exeption.code, broker_resoult_obj.exeption.detailes
            )

        res = broker_resoult_obj.resoult
        if res is None:  # should not happen, but just in case
            logger.error(
                f"exeptionon in get_service_resoult_or_raise_http_exaption broker_resoult_obj.resoult None"
            )
            raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION(
                "Internal server error during user retrieval, incompatible service state"
            )

    return res


async def verify_product_service_request(
    nom_id: int, logger: Logger
) -> SVerifyReqversServiceResult:
    broker_resoult: SVerifyReqversServiceResult = await get_service_resoult(
        SNomId(nom_id=nom_id),
        "verify-product",
        SVerifyReqversServiceResult,
        logger,
    )

    return broker_resoult


async def verify_user_service_request(
    username: str,
    logger: Logger,
) -> SVerifyReqversServiceResult:
    broker_resoult: SVerifyReqversServiceResult = await get_service_resoult(
        SUsername(username=username),
        "verify-user",
        SVerifyReqversServiceResult,
        logger,
    )

    return broker_resoult


async def clear_cart_service_request(
    cart: SUserCart, logger: Logger
) -> SVerifyReqversServiceResult:
    broker_resoult: SVerifyReqversServiceResult = await get_service_resoult(
        cart,
        "clear-cart",
        SVerifyReqversServiceResult,
        logger,
    )

    return broker_resoult


async def restore_cart_service_request(
    cart: SUserCart, logger: Logger
) -> SVerifyReqversServiceResult:
    broker_resoult: SVerifyReqversServiceResult = await get_service_resoult(
        cart,
        "restore-cart",
        SVerifyReqversServiceResult,
        logger,
    )

    return broker_resoult


async def get_order_service_request(
    order_id: SOrderId, logger: Logger
) -> SOrderServiceResult:
    broker_resoult: SOrderServiceResult = await get_service_resoult(
        order_id,
        "get-order",
        SOrderServiceResult,
        logger,
    )

    return broker_resoult


async def set_order_state_paid_service_request(
    order_id: SOrderId, logger: Logger
) -> SOrderServiceResult:
    broker_resoult: SOrderServiceResult = await get_service_resoult(
        order_id,
        "set-order-state-paid",
        SOrderServiceResult,
        logger,
    )

    return broker_resoult


async def get_cart_service_request(
    username: SUsername, logger: Logger
) -> SCartServiceResult:
    broker_resoult: SCartServiceResult = await get_service_resoult(
        username,
        "get-cart",
        SCartServiceResult,
        logger,
    )

    return broker_resoult


async def get_products_for_order_service_request(
    cart: SCart, logger: Logger
) -> SProductsSummaryOutByerServiceResoult:
    broker_resoult: SProductsSummaryOutByerServiceResoult = await get_service_resoult(
        cart,
        "products-for-order",
        SProductsSummaryOutByerServiceResoult,
        logger,
    )
    return broker_resoult


async def sale_in_store_service_request(
    order: SOrderOut, logger: Logger
) -> SSaleInStoreServiceResult:
    broker_resoult: SSaleInStoreServiceResult = await get_service_resoult(
        SSaleIn(order_id=order.id, items=order.items),
        "sale-in-store",
        SSaleInStoreServiceResult,
        logger,
    )
    return broker_resoult
