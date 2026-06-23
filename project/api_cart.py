from typing import Annotated

from fastapi import Security


from project.api import app
from project.lib_services import get_service_resoult_or_raise_http_exaption

from project.lib_auth import (
    get_token_username,
)
from project.schemas import SUsername
from project.schemas_broker import SCartServiceResult, SCatrItemServiceResoult
from project.schemas_cart import SCartItem, SCart, SCartItemIn


@app.get("/api/cart/")
async def get_cart(
    username: Annotated[str, Security(get_token_username, scopes=["cart"])],
) -> SCart:
    return await get_service_resoult_or_raise_http_exaption(
        SUsername(username=username), "get-cart", SCartServiceResult
    )


app = app


@app.post(
    "/api/cart/items/",
    description="if quantity=0 - delete cart item, if quantity>0 will create (or update if exist) cart item",
)
async def add_update_or_delete_cat_item(
    item: SCartItem,
    username: Annotated[str, Security(get_token_username, scopes=["cart"])],
) -> SCartItem:

    return await get_service_resoult_or_raise_http_exaption(
        SCartItemIn(**item.model_dump(), username=username),
        "add-cart-item",
        SCatrItemServiceResoult,
    )


# @app.delete("/api/cart/items/{id}/")
async def delete_cart_item(
    id: int,
    username: Annotated[str, Security(get_token_username, scopes="cart")],
) -> SCartItem:

    return await get_service_resoult_or_raise_http_exaption(
        SCartItemIn(nom_id=id, quantity=0, username=username),
        "delete-cart-item",
        SCatrItemServiceResoult,
    )
