
from fastapi import Security
from pydantic import BaseModel
from project.lib_services import get_service_resoult_or_raise_http_exaption
from project.lib_auth import get_token_username


from project.schemas_broker import SProductsSummaryOutByerServiceResoult
from project.schemas_store import (
    SProductSummaryOutByer,
)
from project.api import app

app = app

class SEmpty(BaseModel):
    pass

@app.get(
    "/api/products/", dependencies=[Security(get_token_username, scopes=["items"])]
)
async def get_products(
) -> list[SProductSummaryOutByer]:
    return await get_service_resoult_or_raise_http_exaption(
        SEmpty(), "products", SProductsSummaryOutByerServiceResoult
    )

