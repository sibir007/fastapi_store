from datetime import timedelta

from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordRequestForm

from faststream.redis import RedisBroker


from project.lib_services import get_service_resoult_or_raise_http_exaption
from project.broker_router import broker, broker_router
from project.schemas import SUsername
from project.schemas_auth import (
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
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_token_username,
    verifiy_and_get_token_data,
)
from project.schemas_broker import STopupServiceResult, SUserServiceResult
from project.api import app

# app = FastAPI()


async def get_current_user(
    token_data: Annotated[TokenData, Depends(verifiy_and_get_token_data)],
    broker: Annotated[RedisBroker, Depends(broker)],
) -> SUserOut:
    res_out: SUserOut = await get_service_resoult_or_raise_http_exaption(broker, SUsername(username=token_data.username), "user",  SUserServiceResult)
    return res_out


@broker_router.post("/api/auth/token/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    broker: Annotated[RedisBroker, Depends(broker)],
) -> Token:

    user: SUserOut = await get_service_resoult_or_raise_http_exaption(
        broker, 
        AuthUserData(username=form_data.username, password=form_data.password),
        "auth",
        SUserServiceResult
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if "admin_permissions" in form_data.scopes:
        form_data.scopes.extend(user.permissions)
    access_token = create_access_token(
        data={"sub": user.username, "scope": " ".join(form_data.scopes)},
        expires_delta=access_token_expires,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/api/auth/token/")
async def get_token_data(
    token_data: Annotated[TokenData, Depends(verifiy_and_get_token_data)],
) -> TokenData:
    return token_data


@broker_router.post("/api/auth/register/")
async def register_user(
    user_data: SUserIn, broker: Annotated[RedisBroker, Depends(broker)]
) -> SUserOut:
    user: SUserOut = await get_service_resoult_or_raise_http_exaption(
        broker,
        user_data,
        "register",
        SUserServiceResult
        )

    return user


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

@broker_router.post("/api/auth/topup/")
async def balance_topup(
    topup: STopupIn,
    username: Annotated[str, Depends(get_token_username)],
    broker: Annotated[RedisBroker, Depends(broker)],
) -> STopupOut:
    
    topup_out: STopupOut = await get_service_resoult_or_raise_http_exaption(
        broker,
        STopup(ammount=topup.ammount, username=username),
        "topup",
        STopupServiceResult
        )
    

    return topup_out

app.include_router(broker_router)
