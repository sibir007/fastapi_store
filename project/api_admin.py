
from fastapi import Security
from project.database.dao_users import add_permission_to_user, get_user_by_name
from project.database.models_auth import Permission
from project.lib_auth import HTTPException, get_token_username


from project.database.dao_store import (
    get_products_summary_for_admin,
    add_nomenclatures as add_nomenclatures_util,
    add_products as add_products_util,
)
from project.schemas_store import (
    SNomenclatureIn,
    SNomenclatureOut,
    SProductIn,
    SProductSummaryOutAdmin,
    SProsuctDbOutFull,
)

from project.schemas_auth import SUserOut

from project.api import app

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


@app.get(
    "/api/admin/user/",
    dependencies=[Security(get_token_username, scopes=["USER_READ"])],
)
async def get_user(
    username: str,
) -> SUserOut:
    user = await get_user_by_name(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post(
    "/api/admin/permissions/user_read/",
    dependencies=[Security(get_token_username, scopes=["USER_PERMISSIONS_UPDATE"])],
    description="Добавить разрешение на чтение информации о пользователе",
)
async def add_user_read_permission(
    username: str,
) -> SUserOut:
    try:
        user = await add_permission_to_user(username, Permission.USER_READ)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user
