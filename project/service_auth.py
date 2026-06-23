from fastapi import status

from faststream import Logger

from project.lib_services import (
    sale_in_store_service_request,
    get_order_service_request,
    set_order_state_paid_service_request,
)
from project.schemas import OrderStatus, SBool, SUsername
from project.schemas_broker import (
    SOrderServiceResult,
    SPaymentServiceResult,
    SSaleInStoreServiceResult,
    SServiceExeption,
    STopupServiceResult,
    SUserServiceResult,
    SVerifyReqversServiceResult,
)
from project.lib_auth import get_password_hash, verify_password
from project.database.dao_users import (
    applay_payment,
    create_user,
    get_user_by_name,
    get_user_by_name_with_pass_hash,
    topup_none_if_user_not_found,
)
from project.schemas_auth import (
    AuthUserData,
    SPaymentIn,
    SPaymentInDB,
    STopup,
    SUserIn,
    SUserInDB,
    SUserOut,
)
from project.schemas_orders import SOrderId
from project.service import service, broker

import logging

logger = logging.getLogger(__name__)

service = service

@broker.subscriber(list="auth")
async def auth_handler(auth_data: AuthUserData, logger: Logger) -> SUserServiceResult:
    logger.info(f"auth message: {auth_data}")
    try:
        user, pass_hash = await get_user_by_name_with_pass_hash(auth_data.username)
    except Exception as e:
        logger.error(f"error in auth_handler: {e}")
        return SUserServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    if user is None:
        return SUserServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_401_UNAUTHORIZED,
                detailes="Incorrect username or password",
            )
        )
    if user.disabled:
        return SUserServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_401_UNAUTHORIZED, detailes="User desabled"
            )
        )
    if not verify_password(auth_data.password, pass_hash):  # type: ignore
        return SUserServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_401_UNAUTHORIZED,
                detailes="Incorrect username or password",
            )
        )

    return SUserServiceResult(resoult=user)


@broker.subscriber(list="user")
async def get_user_handler(username: SUsername, logger: Logger) -> SUserServiceResult:

    logger.info(f"get user handler message: username {username}")
    try:
        user = await get_user_by_name(username.username)
    except Exception as e:
        logger.error(f"error in get_user_handler: {e}")
        return SUserServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    if user is None:
        return SUserServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_404_NOT_FOUND, detailes="User not found"
            )
        )

    return SUserServiceResult(resoult=user)


@broker.subscriber(list="verify-user")
async def verify_user_handler(
    username: SUsername, logger: Logger
) -> SVerifyReqversServiceResult:

    logger.info(f"verify user handler message: username {username}")
    try:
        user = await get_user_by_name(username.username)
    except Exception as e:
        logger.error(f"error in verify_user_handler: {e}")
        return SVerifyReqversServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    if user is None:
        return SVerifyReqversServiceResult(resoult=SBool(result=False))

    return SVerifyReqversServiceResult(resoult=SBool(result=True))


@broker.subscriber(list="topup")
async def topup_handler(topup: STopup, logger: Logger) -> STopupServiceResult:

    logger.info(
        f"topup handler message: username {topup.username}, ammount {topup.ammount}"
    )
    try:
        topup_out = await topup_none_if_user_not_found(topup)
    except Exception as e:
        logger.error(f"error in topup_handler: {e}")
        return STopupServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    if topup_out is None:
        return STopupServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_404_NOT_FOUND, detailes="User not found"
            )
        )

    return STopupServiceResult(resoult=topup_out)


@broker.subscriber(list="payment")
async def payment_handler(payment: SPaymentIn, logger: Logger) -> SPaymentServiceResult:
    """Handle payment for an order.

    1. Verify that the user exists.
    2. Verify that the user is not disabled.
    3. Verify that the order exists.
    4. Verify that the order belongs to the user.
    5. Verify that the order has status WAITING
    6. Verify that the user has enough balance to pay for the order.
    7. Fulfilling a sale in a store
    7.
    7. If any of the above checks fail, return an appropriate error message.
    8. If all checks pass, deduct the order amount from the user's balance and mark the order as paid.
    """

    logger.info(
        f"payment handler message: username {payment.username}, order_id {payment.order_id}"
    )
    try:
        # 1. Verify that the user exists.
        user = await get_user_by_name(payment.username)
    except Exception as e:
        logger.error(f"error in payment handler: {e}")
        return SPaymentServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    if user is None:
        logger.error(f"error in payment handler: user not found")
        return SPaymentServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_404_NOT_FOUND, detailes="User not found"
            )
        )
    # 2. Verify that the user is not disabled.
    if user.disabled:
        logger.error(f"error in payment handler: user {user.username} disabled")
        return SPaymentServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_400_BAD_REQUEST, detailes="User disabled"
            )
        )

    # 3. Verify that the order exists.
    order_servese_resoult: SOrderServiceResult = await get_order_service_request(
        SOrderId(id=payment.order_id), logger
    )
    if order_servese_resoult.exeption:
        logger.error(
            f"error in payment handler: error in order service request: {order_servese_resoult.exeption.detailes}"
        )
        return SPaymentServiceResult(exeption=order_servese_resoult.exeption)

    order = order_servese_resoult.resoult
    if order is None:
        logger.error(f"error in payment handler: order is None")
        return SPaymentServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detailes="order is None",
            )
        )
    # 4. Verify that the order belongs to the user.
    if order.username != payment.username:
        logger.error(f"error in payment handler: order does not belong to the user")
        return SPaymentServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_400_BAD_REQUEST,
                detailes="Order does not belong to the user",
            )
        )
    # 5. Verify that the order has status WAITING
    # TODO: rise condition, scheduler can cancel order in that moment and restore cart
    if order.status != OrderStatus.WAITING:
        logger.error(
            f"error in payment handler: order status {order.status} is not WAITING"
        )
        return SPaymentServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_400_BAD_REQUEST,
                detailes=f"Order status is: {order.status}, expected status: {OrderStatus.WAITING}",
            )
        )

    # 6. Verify that the user has enough balance to pay for the order.
    # TODO: rise condition, balance can be changed in that moment, need to block payment ammount for user before all checks.
    # logger.info(f"order items {order.items}")
    if user.balance < order.total_price:
        logger.error(
            f"error in payment handler: not enough balance to pay for the order, user balance: {user.balance}, order total price: {order.total_price}"
        )
        return SPaymentServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_400_BAD_REQUEST,
                detailes="Not enough balance to pay for the order",
            )
        )
    # 7. Fulfilling a sale in a store
    sale_servese_resoult: SSaleInStoreServiceResult = (
        await sale_in_store_service_request(order, logger)
    )
    if sale_servese_resoult.exeption:
        logger.error(
            f"error in payment handler: error in sale in store service request: {sale_servese_resoult.exeption.detailes}"
        )
        return SPaymentServiceResult(exeption=sale_servese_resoult.exeption)

    store_sale = sale_servese_resoult.resoult
    if store_sale is None:
        logger.error(
            f"error in payment handler: error in sale in store service request: sale is None"
        )
        return SPaymentServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detailes="sale is None",
            )
        )
    set_order_state_paid_resoult = await set_order_state_paid_service_request(
        SOrderId(id=payment.order_id), logger
    )
    if set_order_state_paid_resoult.exeption:
        logger.error(
            f"error in payment handler: error in set order state paid in order service request: {set_order_state_paid_resoult.exeption.detailes}"
        )
        # TODO: need to bask to restore store state, if set order state paid fail after sale in store
        return SPaymentServiceResult(exeption=set_order_state_paid_resoult.exeption)
    try:
        payment_out = await applay_payment(
            SPaymentInDB(
                username=payment.username,
                order_id=payment.order_id,
                ammount=order.total_price,
                sale_id=store_sale.id,
            ),
        )
    except Exception as e:
        logger.error(f"error in payment handler: error in applay_payment: {e}")
        # TODO: if applay_payment fail after sale in store, need bask to restore store and order states,
        return SPaymentServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    # TODO: cancel scedule to cancel order after some time if order is not paid, because in that moment order is in paid state but payment can be not applayed and need to restore store and order states in that case
    return SPaymentServiceResult(resoult=payment_out)


@broker.subscriber(list="register")
async def user_register_handler(
    user_reg: SUserIn, logger: Logger
) -> SUserServiceResult:
    user_dict = user_reg.model_dump()
    user_db = SUserInDB(
        hashed_password=get_password_hash(user_dict.get("password", "")), **user_dict
    )
    try:
        user_out: SUserOut | None = await create_user(user_db)
        if user_out is None:
            return SUserServiceResult(
                exeption=SServiceExeption(
                    code=status.HTTP_409_CONFLICT,
                    detailes="User with the given name or email already exists",
                )
            )

        logger.info(f"user_out: {user_out}")
    except Exception as e:
        logger.error(f"error in user_register_handler: {e}")
        return SUserServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    return SUserServiceResult(resoult=user_out)

