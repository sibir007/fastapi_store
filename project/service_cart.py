
from fastapi import status
from faststream import Logger

from project.api_auth import SUserName

from project.broker import broker, get_broker_resoult
from project.schemas_products import SNomId
from project.service import service
from project.database.dao_cart_util import add_update_delete_cart_item, get_cart
from project.schemas_broker import (
    SBrokerExeption,
    SCartBrokerResult,
    SCatrItemBrokerResoult,
    SVerifyReqversBrokerResult,
)
from project.schemas_cart import SCartItemIn, SCartReq

# from project.schemas_auth import SV
# from project.service_auth import SVerifyUserBrokerResult
# from project.broker_router import broker, broker_router


@broker.subscriber(list="get-cart")
async def get_cart_handler(cart_req: SCartReq, logger: Logger) -> SCartBrokerResult:
    logger.info(f"get cart handler, username: {cart_req.username}")

    # get_user_by_name
    broker_resoult = await verify_user_service_request(cart_req.username, logger)  # type: ignore
    if broker_resoult.exeption:  # type: ignore
        return SCartBrokerResult(exeption=broker_resoult.exeption)  # type: ignore
    try:
        cart = await get_cart(cart_req)
    except Exception as e:
        logger.error(
            f"get cart handler, username: {cart_req.username}, broker exaption {e.__repr__()} {e.__str__()}"
        )
        return SCartBrokerResult(
            exeption=SBrokerExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    return SCartBrokerResult(resoult=cart)


async def verify_user_service_request(
    username: str, logger: Logger
) -> SVerifyReqversBrokerResult:
    broker_resoult: SVerifyReqversBrokerResult = await get_broker_resoult(
        broker,
        SUserName(username=username),
        "verify-user",
        SVerifyReqversBrokerResult,
        logger,
    )

    return broker_resoult


@broker.subscriber(list="add-cart-item")
async def add_cart_item_handler(
    item: SCartItemIn, logger: Logger
) -> SCatrItemBrokerResoult:
    logger.info(
        f"add cart item handler, nom_id: {item.nom_id}, username: {item.username}, quantity: {item.quantity}"
    )

    verify_user_broker_resoult = await verify_user_service_request(
        item.username, logger
    )
    if verify_user_broker_resoult.exeption:
        return SCatrItemBrokerResoult(exeption=verify_user_broker_resoult.exeption)
    verify_product_broker_resoult = await verify_product_service_request(
        item.nom_id, logger
    )
    if verify_product_broker_resoult.exeption:
        return SCatrItemBrokerResoult(exeption=verify_product_broker_resoult.exeption)
    try:
        cart = await add_update_delete_cart_item(item)
    except Exception as e:
        logger.error(
            f"add cart item handler, username: {item.username}, broker exaption {e.__repr__()} {e.__str__()}"
        )
        return SCatrItemBrokerResoult(
            exeption=SBrokerExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    return SCatrItemBrokerResoult(resoult=cart)


async def verify_product_service_request(nom_id: int, logger: Logger):
    broker_resoult: SVerifyReqversBrokerResult = await get_broker_resoult(
        broker,
        SNomId(nom_id=nom_id),
        "verify-product",
        SVerifyReqversBrokerResult,
        logger,
    )

    return broker_resoult


@broker.subscriber(list="test")
async def base_handler(msg: str, logger: Logger) -> None:
    logger.info(f"test message: {msg}")


@service.after_startup
async def test():
    await broker.publish("test startup", list="test")
