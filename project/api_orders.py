from typing import Annotated

from fastapi import Depends, Security

from faststream.redis import RedisBroker


from project.lib_services import get_service_resoult_or_raise_http_exaption
from project.broker_router import broker, broker_router

from project.lib_auth import (
    get_token_username,
)
from project.schemas import SUsername
from project.schemas_broker import SOrderServiceResult, SOrdersServiceResult
from project.api import app
from project.schemas_orders import SOrderOut

app = app

@broker_router.get("/api/orders/")
async def get_cart(
    username: Annotated[str, Security(get_token_username, scopes=["orders"])],
    broker: Annotated[RedisBroker, Depends(broker)],
) -> list[SOrderOut]:
    return await get_service_resoult_or_raise_http_exaption(
        broker, SUsername(username=username), "get-orders", SOrdersServiceResult
    )


@broker_router.post("/api/orders/create/")
async def add_update_or_delete_cat_item(
    username: Annotated[str, Security(get_token_username, scopes=["orders"])],
    broker: Annotated[RedisBroker, Depends(broker)],
) -> SOrderOut:
    """
    Create order from cart and clear cart
    """
    
    return await get_service_resoult_or_raise_http_exaption(
        broker,
        SUsername(username=username),
        "create-order",
        SOrderServiceResult,
    )


# app.add_api_route(broker_router)
app.include_router(broker_router)


