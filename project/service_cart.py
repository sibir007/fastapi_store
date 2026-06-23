
from fastapi import status
from faststream import Logger


from project.database.dao_cart import add_update_delete_cart_item, clear_cart, get_cart, restore_cart
from project.lib_services import verify_product_service_request, verify_user_service_request
from project.schemas import SBool, SUsername
from project.service import service, broker
from project.schemas_broker import (
    SServiceExeption,
    SCartServiceResult,
    SCatrItemServiceResoult,
)
from project.schemas_cart import SCartItemIn, SUserCart
from project.schemas_broker import SVerifyReqversServiceResult

# from project.schemas_auth import SV
# from project.service_auth import SVerifyUserBrokerResult
# from project.broker_router import broker, broker_router
service = service


@broker.subscriber(list="clear-cart")
async def clear_cart_handler(cart: SUserCart, logger: Logger) -> SVerifyReqversServiceResult:
    logger.info(f"clear cart handler, cart username: {cart.username}")

    try:
        await clear_cart(cart)
    except Exception as e:
        logger.error(
            f"clear cart handler, username: {cart.username}, service exaption {e}"
        )
        return SVerifyReqversServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=str(e)
            )
        )
    return SVerifyReqversServiceResult(resoult=SBool(result=True))



@broker.subscriber(list="restore-cart")
async def restore_cart_handler(cart: SUserCart, logger: Logger) -> SVerifyReqversServiceResult:
    logger.info(f"restore cart handler, cart username: {cart.username}")

    try:
        await restore_cart(cart)
    except Exception as e:
        logger.error(
            f"restore cart handler, username: {cart.username}, service exaption {e}"
        )
        return SVerifyReqversServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=str(e)
            )
        )
    return SVerifyReqversServiceResult(resoult=SBool(result=True))




@broker.subscriber(list="get-cart")
async def get_cart_handler(cart_req: SUsername, logger: Logger) -> SCartServiceResult:
    logger.info(f"get cart handler, username: {cart_req.username}")

    # get_user_by_name
    broker_resoult = await verify_user_service_request(cart_req.username, logger)
    if broker_resoult.exeption:
        return SCartServiceResult(exeption=broker_resoult.exeption)
    try:
        cart = await get_cart(cart_req)
    except Exception as e:
        logger.error(
            f"get cart handler, username: {cart_req.username}, broker exaption {e.__repr__()} {e.__str__()}"
        )
        return SCartServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    return SCartServiceResult(resoult=cart)


@broker.subscriber(list="add-cart-item")
async def add_cart_item_handler(
    item: SCartItemIn, logger: Logger
) -> SCatrItemServiceResoult:
    logger.info(
        f"add cart item handler, nom_id: {item.nom_id}, username: {item.username}, quantity: {item.quantity}"
    )

    verify_user_broker_resoult = await verify_user_service_request(
        item.username, logger
    )
    if verify_user_broker_resoult.exeption:
        return SCatrItemServiceResoult(exeption=verify_user_broker_resoult.exeption)
    verify_product_broker_resoult = await verify_product_service_request(
        item.nom_id, logger
    )
    if verify_product_broker_resoult.exeption:
        return SCatrItemServiceResoult(exeption=verify_product_broker_resoult.exeption)
    try:
        cart = await add_update_delete_cart_item(item)
    except Exception as e:
        logger.error(
            f"add cart item handler, username: {item.username}, broker exaption {e.__repr__()} {e.__str__()}"
        )
        return SCatrItemServiceResoult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    return SCatrItemServiceResoult(resoult=cart)


