from datetime import timedelta

import time
from typing import Annotated, Any,Awaitable, Callable

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from faststream.redis import RedisBroker
from faststream.redis.fastapi import RedisRouter
from pwdlib import PasswordHash

from project.config import settings

from project.auth_schemas import AuthUserData, Token, UserBase

from project.auth_lib import (
    AuthResoult,
    get_current_user_by_token, 

    create_access_token
    )

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()

# DUMMY_HASH = password_hash.hash("dummypassword")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    # scopes={"me": "Read information about the current user.", "items": "Read items."},
)


app = FastAPI()



broker_router = RedisRouter(settings.REDIS_URL)

def broker() -> RedisBroker:
    return broker_router.broker

# app = FastStream(broker)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> UserBase:

    return get_current_user_by_token(token)


@broker_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    broker: Annotated[RedisBroker, Depends(broker)]
) -> Token:
    
    # await broker.connect()
    auth_response = await broker.request(
        AuthUserData(username=form_data.username, password=form_data.password), 
        list='auth'
    )
    auth_resoult: dict[str, Any] | None = await auth_response.decode()

    if auth_resoult is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error",
        )
    
    auth_resoult_obj: AuthResoult = AuthResoult(**auth_resoult)
    if auth_resoult_obj.error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=auth_resoult_obj.error,
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_resoult_obj.user
    # user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scope": " ".join(user.scopes)}, 
        expires_delta=access_token_expires,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/")
async def read_users_me(
    current_user: Annotated[UserBase, Depends(get_current_user)],
) -> UserBase:
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[UserBase, Depends(get_current_user)],
) -> list[dict[str, str]]:
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start_time = time.perf_counter()
    response: Response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(broker_router)