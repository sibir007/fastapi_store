from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordRequestForm



from project.lib_services import get_service_resoult_or_raise_http_exaption

# from project.broker_router import broker, broker_router
from project.schemas import SUsername
from project.schemas_auth import (
    SPaymentIn,
    SPaymentOut,
    STopup,
    STopupIn,
    STopupOut,
    TokenData,
    AuthUserData,
    Token,
    SUserOut,
    SUserIn,
)
from project.lib_auth import (
    create_access_token,
    get_token_username,
    verifiy_and_get_token_data,
)
from project.schemas_broker import (
    SPaymentServiceResult,
    STopupServiceResult,
    SUserServiceResult,
)

from project.api import app
import logging

logger = logging.Logger(__name__)

# broker = RedisBroker(settings.REDIS_URL)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await broker.start()
#     yield
#     await broker.stop()


# @asynccontextmanager
# async def start_broker():
#     await broker.start()
#     yield
#     await broker.stop()


# app = FastAPI()


async def get_current_user(
    token_data: Annotated[TokenData, Depends(verifiy_and_get_token_data)],
) -> SUserOut:
    res_out: SUserOut = await get_service_resoult_or_raise_http_exaption(
        SUsername(username=token_data.username), "user", SUserServiceResult
    )
    return res_out


async def login_or_raise_http_exaption(user_data: AuthUserData) -> SUserOut:
    user: SUserOut = await get_service_resoult_or_raise_http_exaption(
        user_data,
        "auth",
        SUserServiceResult,
    )
    return user


# @broker_router.post("/api/auth/token/")
@app.post("/api/auth/token/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    # broker: Annotated[RedisBroker, Depends(broker)],
) -> Token:

    user: SUserOut = await get_service_resoult_or_raise_http_exaption(
        AuthUserData(username=form_data.username, password=form_data.password),
        "auth",
        SUserServiceResult,
    )

    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if "admin_permissions" in form_data.scopes:
        form_data.scopes.extend(user.permissions)
    access_token = create_access_token(user.username, form_data.scopes)
    return Token(access_token=access_token, token_type="bearer")


@app.get("/api/auth/token/")
async def get_token_data(
    token_data: Annotated[TokenData, Depends(verifiy_and_get_token_data)],
) -> TokenData:
    return token_data


# @broker_router.post("/api/auth/register/")
@app.post("/api/auth/register/")
async def register_user(
    user_data: SUserIn,
    # broker: Annotated[RedisBroker, Depends(broker)]
) -> SUserOut:
    user: SUserOut = await get_service_resoult_or_raise_http_exaption(
        user_data, "register", SUserServiceResult
    )

    return user


# @app.post("/api/auth/register2/")
# # @broker_router.post("/api/auth/register2/")
# async def register_user2(
#     user_data: SUserIn,
#     # broker: Annotated[RedisBroker, Depends(broker)]
# ) -> SUserOut:
#     # user: SUserOut = await get_service_resoult_or_raise_http_exaption(
#     #     broker, user_data, "register", SUserServiceResult
#     # )
#     # broker = RedisBroker(settings.REDIS_URL)
#     async with start_broker():
#         try:

#             # await broker.connect()
#             broker_response = await broker.request(user_data, list="register")
#             broker_resoult: dict[str, Any] | None = await broker_response.decode()
#             # mess: RedisChannelMessage = await broker.request(req, list=queue_name)
#             # res_: None | dict[str, Any] = await mess.decode()
#             # logger.error(f"broker res: {broker_resoult}, class {broker_result_class}")
#         except Exception as e:
#             # raise e
#             logger.error(
#                 f"os.environ.get('CONFIG_MODE') ------->>>>> {os.environ.get('CONFIG_MODE')}   exeptionon in get_service_resoult_or_raise_http_exaption: {e.__str__()}, enveron settings.REDIS_URL: {settings.REDIS_URL}"
#             )
#             raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION(
#                 detail=f"error: {e.__str__()}"
#             )

#         if broker_resoult is None:
#             logger.error(
#                 f"exeptionon in get_service_resoult_or_raise_http_exaption res None"
#             )
#             raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION(detail="broker_sesoult None")
#         broker_resoult_obj = SUserServiceResult(**broker_resoult)
#         if broker_resoult_obj.exeption:
#             logger.error(
#                 f"exeptionon in get_service_resoult_or_raise_http_exaption broker_resoult_obj.exeption ditails: {broker_resoult_obj.exeption.detailes}"
#             )
#             raise_exaption(
#                 broker_resoult_obj.exeption.code, broker_resoult_obj.exeption.detailes
#             )

#         user: SUserOut | None = broker_resoult_obj.resoult
#         if user is None:  # should not happen, but just in case
#             logger.error(
#                 f"exeptionon in get_service_resoult_or_raise_http_exaption broker_resoult_obj.resoult None"
#             )
#             raise HTTP_500_INTERNAL_SERVER_ERROR_EXCEPTION(
#                 "Internal server error during user retrieval, incompatible service state"
#             )

#     return user


@app.get("/api/auth/username")
async def get_token_user(
    username: Annotated[str, Depends(get_token_username)],
) -> str:
    return username


@app.get("/api/auth/profile")
async def read_users_me(
    current_user: Annotated[SUserOut, Security(get_current_user, scopes=["me"])],
) -> SUserOut:
    return current_user


@app.post("/api/auth/topup/")
# @broker_router.post("/api/auth/topup/")
async def balance_topup(
    topup: STopupIn,
    username: Annotated[str, Depends(get_token_username)],
    # broker: Annotated[RedisBroker, Depends(broker)],
) -> STopupOut:

    topup_out: STopupOut = await get_service_resoult_or_raise_http_exaption(
        STopup(ammount=topup.ammount, username=username),
        "topup",
        STopupServiceResult,
    )

    return topup_out


@app.post("/api/auth/payment/")
# @broker_router.post("/api/auth/payment/")
async def payment(
    order_id: int,
    username: Annotated[str, Security(get_token_username, scopes=["payment"])],
    # broker: Annotated[RedisBroker, Depends(broker)],
) -> SPaymentOut:

    payment_out: SPaymentOut = await get_service_resoult_or_raise_http_exaption(
        SPaymentIn(order_id=order_id, username=username),
        "payment",
        SPaymentServiceResult,
    )

    return payment_out


# app.include_router(broker_router)

# app=app
