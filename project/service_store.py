from fastapi import status
from faststream import Logger
from pydantic import BaseModel

from project.database.dao_store import (
    add_sale,
    get_nomenclatures,
    get_products_summary_for_byer,
)
from project.schemas import SBool
from project.schemas_broker import (
    SSaleInStoreServiceResult,
    SServiceExeption,
    SProductsSummaryOutByerServiceResoult,
    SVerifyReqversServiceResult,
)
from project.schemas_cart import SCart
from project.schemas_store import SNomId, SProductSummaryOutByer, SSaleIn

from project.service import service
from project.broker import broker

# from project.broker_router import broker, broker_router


@broker.subscriber(list="products")
async def get_products_handler(
    _: BaseModel, logger: Logger
) -> SProductsSummaryOutByerServiceResoult:
    logger.info(f"get products handler: accept")
    try:
        products: list[SProductSummaryOutByer] = await get_products_summary_for_byer()
    except Exception as e:
        logger.error(f"error in get_products_handler: {e}")
        return SProductsSummaryOutByerServiceResoult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )

    return SProductsSummaryOutByerServiceResoult(resoult=products)



@broker.subscriber(list="products-for-order")
async def get_products_for_order_handler(
    products: SCart, logger: Logger
) -> SProductsSummaryOutByerServiceResoult:
    logger.info(f"get products for order handler: accept")
    try:
        products_for_byer: list[SProductSummaryOutByer] = (
            await get_products_summary_for_byer(
                [product.nom_id for product in products.items]
            )
        )

    except Exception as e:
        logger.error(f"error in get_products_for_order_handler: {e}")
        return SProductsSummaryOutByerServiceResoult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    
    
    return SProductsSummaryOutByerServiceResoult(resoult=products_for_byer)


# "verify-product"

# SNomId(nom_id=nom_id),
#         "verify-product",
#         ,


@broker.subscriber(list="verify-product")
async def verify_product_handler(
    nom_id: SNomId, logger: Logger
) -> SVerifyReqversServiceResult:
    logger.info(f"verify product handler: nom_id {nom_id}")
    try:
        noms = await get_nomenclatures([nom_id.nom_id])
    except Exception as e:
        logger.error(f"error in verify_product_handler: {e}")
        return SVerifyReqversServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    return SVerifyReqversServiceResult(resoult=SBool(result=bool(noms)))



@broker.subscriber(list="sale-in-store")
async def sale_in_store_handler(
    sale: SSaleIn, logger: Logger
) -> SSaleInStoreServiceResult:
    logger.info(f"sale in store handler: order {sale}")
    try:
        sale_out = await add_sale(sale)
    except Exception as e:
        logger.error(f"error in sale_in_store_handler: {e}")
        return SSaleInStoreServiceResult(
            exeption=SServiceExeption(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
            )
        )
    return SSaleInStoreServiceResult(resoult=sale_out)





# @broker.subscriber(list="user")
# async def get_user_handler(username: str, logger: Logger) -> SUserBrokerResult:

#     logger.info(f"get user handler message: username {username}")
#     try:
#         user = await get_user_by_name(username)
#     except Exception as e:
#         return SUserBrokerResult(
#             exeption=SBrokerExeption(
#                 code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
#             )
#         )
#     if user is None:
#         return SUserBrokerResult(
#             exeption=SBrokerExeption(
#                 code=status.HTTP_404_NOT_FOUND, detailes="User not found"
#             )
#         )

#     return SUserBrokerResult(resoult=user)


# @broker.subscriber(list="topup")
# async def topup_handler(topup: STopup, logger: Logger) -> STopupBrokerResult:

#     logger.info(
#         f"topup handler message: username {topup.username}, ammount {topup.ammount}"
#     )
#     try:
#         topup_out = await topup_none_if_user_not_found(topup)
#     except Exception as e:
#         return STopupBrokerResult(
#             exeption=SBrokerExeption(
#                 code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
#             )
#         )
#     if topup_out is None:
#         return STopupBrokerResult(
#             exeption=SBrokerExeption(
#                 code=status.HTTP_404_NOT_FOUND, detailes="User not found"
#             )
#         )

#     return STopupBrokerResult(resoult=topup_out)


# @broker.subscriber(list="register")
# async def user_register_handler(user_reg: SUserIn, logger: Logger) -> SUserBrokerResult:
#     user_dict = user_reg.model_dump()
#     user_db = SUserInDB(
#         hashed_password=get_password_hash(user_dict.get("password", "")), **user_dict
#     )
#     try:
#         user_out: SUserOut | None = await create_user(user_db)
#         if user_out is None:
#             return SUserBrokerResult(
#                 exeption=SBrokerExeption(
#                     code=status.HTTP_409_CONFLICT,
#                     detailes="User with the given name or email already exists",
#                 )
#             )

#         logger.info(f"user_out: {user_out}")
#     except Exception as e:
#         return SUserBrokerResult(
#             exeption=SBrokerExeption(
#                 code=status.HTTP_500_INTERNAL_SERVER_ERROR, detailes=e.__str__()
#             )
#         )
#     return SUserBrokerResult(resoult=user_out)


@broker.subscriber(list="test")
async def base_handler(msg: str, logger: Logger) -> None:
    logger.info(f"test message: {msg}")


@service.after_startup
async def test():
    await broker.publish("test startup", list="test")
