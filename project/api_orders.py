from typing import Annotated

from fastapi import Security



from project.lib_services import get_service_resoult_or_raise_http_exaption

from project.lib_auth import (
    get_token_username,
)
from project.schemas import SUsername
from project.schemas_broker import SOrderServiceResult, SOrdersServiceResult
from project.api import app
from project.schemas_orders import SOrderOut

app = app

@app.get("/api/orders/")
async def get_cart(
    username: Annotated[str, Security(get_token_username, scopes=["orders"])],
) -> list[SOrderOut]:
    return await get_service_resoult_or_raise_http_exaption(
        SUsername(username=username), "get-orders", SOrdersServiceResult
    )


@app.post("/api/orders/create/")
async def add_update_or_delete_cat_item(
    username: Annotated[str, Security(get_token_username, scopes=["orders"])],
) -> SOrderOut:
    """
    Create order from cart and clear cart
    """
    
    return await get_service_resoult_or_raise_http_exaption(
        SUsername(username=username),
        "create-order",
        SOrderServiceResult,
    )


# app.add_api_route(broker_router)
# app.include_router(broker_router)


