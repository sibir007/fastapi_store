from fastapi import FastAPI, Security
from project.lib_auth import get_token_username

from fastapi.middleware.cors import CORSMiddleware

from project.database.dao_products_util import (
    get_products_summary_for_byer,
    get_products_summary_for_admin,
    add_nomenclatures as add_nomenclatures_util,
    add_products as add_products_util,
)
from project.schemas_products import (
    SNomenclatureIn,
    SNomenclatureOut,
    SProductIn,
    SProductSummaryOutAdmin,
    SProductSummaryOutByer,
    SProsuctDbOutFull,
)

app = FastAPI()


@app.get(
    "/api/products/", dependencies=[Security(get_token_username, scopes=["items"])]
)
async def get_products() -> list[SProductSummaryOutByer]:
    return await get_products_summary_for_byer()


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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
