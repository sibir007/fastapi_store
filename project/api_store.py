from typing import Annotated

from fastapi import Depends, Security
from faststream.redis import RedisBroker
from pydantic import BaseModel
from project.lib_services import get_service_resoult_or_raise_http_exaption
from project.broker_router import broker, broker_router
from project.lib_auth import get_token_username


from project.database.dao_store import (
    get_products_summary_for_admin,
    add_nomenclatures as add_nomenclatures_util,
    add_products as add_products_util,
)
from project.schemas_broker import SProductsSummaryOutByerServiceResoult
from project.schemas_store import (
    SNomenclatureIn,
    SNomenclatureOut,
    SProductIn,
    SProductSummaryOutAdmin,
    SProductSummaryOutByer,
    SProsuctDbOutFull,
)
from project.api import app
# app = FastAPI()

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



@app.get(
    "/api/admin/products/",
    dependencies=[Security(get_token_username, scopes=["PRODUCT_CREATE"])],
)
async def get_admin_products() -> list[SProductSummaryOutAdmin]:
    return await get_products_summary_for_admin()


@app.post(
    "/api/admin/products/",
    dependencies=[Security(get_token_username, scopes=["PRODUCT_CREATE"])],
)
async def add_products(products: list[SProductIn]) -> list[SProsuctDbOutFull]:
    return await add_products_util(products)


@app.post(
    "/api/admin/nomenclatures/",
    dependencies=[Security(get_token_username, scopes=["PRODUCT_CREATE"])],
)
async def add_nomenclatures(
    nomenclatures: list[SNomenclatureIn],
) -> list[SNomenclatureOut]:
    return await add_nomenclatures_util(nomenclatures)

app.include_router(broker_router)
