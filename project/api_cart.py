import time
from typing import Annotated, Awaitable, Callable

from fastapi import Depends, FastAPI, Request, Response, Security
from fastapi.middleware.cors import CORSMiddleware

from faststream.redis import RedisBroker


from project.broker import get_broker_resoult_or_raise_http_exaption
from project.broker_router import broker, broker_router

from project.lib_auth import (
    get_token_username,
)
from project.schemas_broker import SCartBrokerResult, SCatrItemBrokerResoult
from project.schemas_cart import SCartItem, SCart, SCartItemIn, SCartReq

app = FastAPI()



@broker_router.get("/api/cart/")
async def get_cart(
    username: Annotated[str, Security(get_token_username, scopes=["items"])],
    broker: Annotated[RedisBroker, Depends(broker)],
) -> SCart:
    return await get_broker_resoult_or_raise_http_exaption(
        broker, SCartReq(username=username), "get-cart", SCartBrokerResult
    )


@broker_router.post("/api/cart/items/" , description="if quantity=0 - delete cart item, if quantity>0 will create (or update if exist) cart item")
async def add_update_or_delete_cat_item(
    item: SCartItem,
    username: Annotated[str, Security(get_token_username, scopes=["items"])],
    broker: Annotated[RedisBroker, Depends(broker)],
) -> SCartItem:

    return await get_broker_resoult_or_raise_http_exaption(
        broker,
        SCartItemIn(**item.model_dump(), username=username),
        "add-cart-item",
        SCatrItemBrokerResoult,
    )




# @app.delete("/api/cart/items/{id}/")
async def delete_cart_item(
    id: int,
    username: Annotated[str, Security(get_token_username, scopes="items")],
    broker: Annotated[RedisBroker, Depends(broker)],
) -> SCartItem:

    return await get_broker_resoult_or_raise_http_exaption(
        broker,
        SCartItemIn(nom_id=id, quantity=0, username=username),
        "delete-cart-item",
        SCatrItemBrokerResoult,
    )


@app.middleware("http")
async def add_process_time_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
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
