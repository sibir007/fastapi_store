from typing import Annotated

from fastapi import Depends, Security
from faststream.redis import RedisBroker
from pydantic import BaseModel
from project.lib_services import get_service_resoult_or_raise_http_exaption
from project.broker_router import broker, broker_router
from project.lib_auth import get_token_username


from project.schemas_broker import SProductsSummaryOutByerServiceResoult
from project.schemas_store import (
    SProductSummaryOutByer,
)
from project.api import app # type: ignore

class SEmpty(BaseModel):
    pass

@broker_router.get(
    "/api/products/", dependencies=[Security(get_token_username, scopes=["items"])]
)
async def get_products(
    broker: Annotated[RedisBroker, Depends(broker)],
) -> list[SProductSummaryOutByer]:
    return await get_service_resoult_or_raise_http_exaption(
        broker, SEmpty(), "products", SProductsSummaryOutByerServiceResoult
    )

