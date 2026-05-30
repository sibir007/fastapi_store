

from fastapi import status
from faststream import Logger
from pydantic import BaseModel

from project.schemas_broker import SOrderServiceResult, SOrdersServiceResult
from project.database.dao_order import add_order, cancel_order, get_all_orders, get_order
from project.database.dao_order import add_order
from project.lib_services import (
    clear_cart_service_request,
    get_cart_service_request,
    get_products_for_order_service_request,
    restore_cart_service_request,
)
from project.schemas import SUsername
from project.schemas_broker import (
    SServiceExeption,
)
from project.schemas_cart import SCart, SUserCart
from project.schemas_orders import SOrderIn, SOrderItem, SOrderOut
from project.schemas_products import SProductSummaryOutByer

from project.service import service
from project.broker import broker


from project.scheduler_calable import set_order_canceled_service_reqvest, test_service_orders
from project.scheduler import async_scheduler
from apscheduler.triggers.date import DateTrigger

from datetime import timedelta, datetime



class SCartProductsOrderConvert(BaseModel):
    order: SOrderOut
    errors: list[int]  # unavalible products id


# def checking_for_missing_products(cart: SCart, products: list[SProductSummaryOutByer]) -> list[int]:
#     errors: list[int] = []
#     cart_ids = {cart_item.nom_id for cart_item in cart.items}
#     products_ids = {product.id for product in products}
#     missing_ids = cart_ids - products_ids
#     errors.extend(missing_ids)
#     return errors


def checking_for_unavalible_products(
    cart: SCart, products: list[SProductSummaryOutByer]
) -> list[int]:
    errors: list[int] = []
    products_dict = {product.id: product for product in products}
    for cart_item in cart.items:
        product = products_dict.get(cart_item.nom_id)
        if not product or product.total_remainder < cart_item.quantity:
            errors.append(cart_item.nom_id)
    return errors


def create_order_from_cart(
    username: str, cart: SCart, products: list[SProductSummaryOutByer]
) -> SOrderIn:
    products_dict = {product.id: product for product in products}
    order_items: list[SOrderItem] = []
    for cart_item in cart.items:
        product = products_dict.get(cart_item.nom_id)
        if product:
            order_items.append(
                SOrderItem(
                    nom_id=cart_item.nom_id,
                    quantity=cart_item.quantity,
                    byer_price=product.selling_price,
                )
            )
    order = SOrderIn(
        username=username,
        items=order_items,
    )
    return order



@broker.subscriber(list="create-order")
async def create_order_handler(
    username: SUsername, logger: Logger
) -> SOrderServiceResult:
    logger.info(f"create` order handler: accept")

    """
    Create order from cart and clear cart
    
    1. Get cart and verify user by username
    2. Get products summary for byer
    3. Check products in cart with products summary for byer, if some product is unavalible return error with unavalible products id
    4. Create order from cart
    5. Add order to database
    6. Clear cart
    7. Create scheule for canceling order if order will not be paid in time
    8. Return order out
    """

    # 1. Get cart and verify user by username
    cart_servese_resoult = await get_cart_service_request(username, broker, logger)
    if cart_servese_resoult.exeption:
        return SOrderServiceResult(exeption=cart_servese_resoult.exeption)

    cart = cart_servese_resoult.resoult
    if cart is None:
        return SOrderServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detailes="cart is None",
            )
        )

    # 2. Get products summary for byer
    products_service_resoult = await get_products_for_order_service_request(
        cart, broker, logger
    )
    if products_service_resoult.exeption:
        return SOrderServiceResult(exeption=products_service_resoult.exeption)
    products = products_service_resoult.resoult
    if products is None:
        return SOrderServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detailes="products is None",
            )
        )
    # 3. Check products in cart with products summary for byer, if some product is unavalible return error with unavalible products id
    check_resoult = checking_for_unavalible_products(cart, products)
    if check_resoult:
        return SOrderServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_400_BAD_REQUEST,
                detailes=f"Some products are unavalible, unavalible products id: {check_resoult}",
            )
        )
    # 4. Create order from cart
    order_in = create_order_from_cart(username.username, cart, products)

    try:
    # 5. Add order to database
        order_out = await add_order(order_in)
    except Exception as e:
        logger.error(f"error in create_order_handler add_order: {e}")
        return SOrderServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    
    # 6. Clear cart
    # TODO: if clear cart will be failed? need to add some compensation mechanism
    clear_cart_broker_resoult = await clear_cart_service_request(SUserCart(username=username.username, items=cart.items), broker, logger) # type: ignore

    # 7. Create scheule for canceling order if order will not be paid in time
    async with async_scheduler as scheduler:
        await scheduler.add_schedule(
            set_order_canceled_service_reqvest,
            DateTrigger(run_time=datetime.now() + timedelta(seconds=20)),
            id=f"cancel_order_{order_out.id}",
            args=[order_out.id]
            # kwargs={"task_id": "test_scheduler", "optional_mes": "start up test_scheduler"},
        )

    # 8. Return order out
    return SOrderServiceResult(resoult=order_out)

@broker.subscriber(list="cancel-order")
async def cancel_order_handler(order_id: int, logger: Logger):
    logger.info(f"cancel order handler: accept")
    try:
        order_out = await cancel_order(order_id)

        if order_out is None:
            logger.error(f"order with id {order_id} not found or not in waiting status")
        else:
            logger.info(f"order with id {order_out.id} {order_out.status.value}")
            # TODO: if restore cart will be failed? need to add some compensation mechanism
            restore_cart_broker_resoult = await restore_cart_service_request(SUserCart(**order_out.model_dump()), broker, logger) # type: ignore


    except Exception as e:
        logger.error(f"exeption in cancel_order_handler: {e.__str__()}")
        



@broker.subscriber(list="get-order")
async def get_order_handler(order_id: int, logger: Logger) -> SOrderServiceResult:
    logger.info(f"get order handler: accept")

    try:
        order_out = await get_order(order_id)
    except Exception as e:
        return SOrderServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    if order_out is None:
        return SOrderServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_404_NOT_FOUND, detailes="Order not found"
            )
        )

    return SOrderServiceResult(resoult=order_out)


@broker.subscriber(list="get-orders")
async def get_orders_handler(username: SUsername, logger: Logger) -> SOrdersServiceResult:
    logger.info(f"get orders handler: accept")

    try:
        orders_out = await get_all_orders(username.username)
    except Exception as e:
        return SOrdersServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )

    return SOrdersServiceResult(resoult=orders_out)


# @broker.subscriber(list="verify-product")
# async def verify_product_handler(
#     nom_id: SNomId, logger: Logger
# ) -> SVerifyReqversBrokerResult:
#     logger.info(f"verify product handler: nom_id {nom_id}")
#     try:
#         noms = await get_nomenclatures([nom_id.nom_id])
#     except Exception as e:
#         return SVerifyReqversBrokerResult(
#             exeption=SBrokerExeption(
#                 code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
#             )
#         )
#     return SVerifyReqversBrokerResult(resoult=SBool(result=bool(noms)))


@broker.subscriber(list="test-service-orders")
async def test_handler(msg: str, logger: Logger) -> None:
    logger.info(f"test message: {msg}")


@service.after_startup
async def test():
    await broker.publish("test startup", list="test-service-orders")



@service.after_startup
async def test_scheduler():

    async with async_scheduler as scheduler:
        await scheduler.add_schedule(
            test_service_orders,
            DateTrigger(run_time=datetime.now() + timedelta(seconds=5)),
            id="test_scheduler",
            args=["test_scheduler_from_scheuduler"]
            # kwargs={"task_id": "test_scheduler", "optional_mes": "start up test_scheduler"},
        )


