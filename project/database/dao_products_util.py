from typing import Iterable

from sqlalchemy.future import select

from project.auth_schemas import (
    SNomenclatureIn,
    SNomenclatureOut,
    SProductIn,
    SProsuctDbOut,
    SProsuctDbOutFull,
)
from project.database.dao import MProduct
from project.database.dao_util import clear_table  # type: ignore
from project.database.models import MNomenclature
from project.database.session import async_session


async def clear_nomenclature_table() -> None:
    await clear_table(MNomenclature)


async def clear_product_table() -> None:
    await clear_table(MProduct)


def MProduct_to_SProsuctDbOutFull(product: MProduct) -> SProsuctDbOutFull:
    nom: MNomenclature = product.nomenclature
    return SProsuctDbOutFull(
        **product.to_dict(), name=nom.name, description=nom.description
    )


def MNomenclature_to_SNomenclatureOut(nomenclature: MNomenclature) -> SNomenclatureOut:
    products: Iterable[MProduct] = nomenclature.products
    products_out = [MProduct_to_SProsuctDbOutFull(p) for p in products]
    return SNomenclatureOut(**nomenclature.to_dict(), products=products_out)


async def add_nomenclatures(
    nomenclatures: Iterable[SNomenclatureIn],
) -> list[SNomenclatureOut]:
    async with async_session() as session:
        nom_m_list = [MNomenclature(**n.model_dump()) for n in nomenclatures]
        session.add_all(nom_m_list)
        await session.commit()
        no_out_list = [MNomenclature_to_SNomenclatureOut(n) for n in nom_m_list]
    return no_out_list


async def add_nomenclature(nomenclature: SNomenclatureIn) -> SNomenclatureOut:
    async with async_session() as session:
        nom_m = MNomenclature(**nomenclature.model_dump())
        session.add(nom_m)
        await session.commit()
        nom_out = MNomenclature_to_SNomenclatureOut(nom_m)
    return nom_out

async def get_nomenclatures() -> list[SNomenclatureOut]:
    async with async_session() as session:
        nom_m_list_res = await session.execute(select(MNomenclature))
        nom_m_list = nom_m_list_res.scalars().all()
        nom_out = [MNomenclature_to_SNomenclatureOut(n) for n in nom_m_list]
    return nom_out


async def add_prducts(products: Iterable[SProductIn]) -> list[SProsuctDbOutFull]:
    async with async_session() as session:
        pr_in_db_list = [
            MProduct(
                remainder=pr.quantity, 
                nom_id=pr.nom_id,
                cost_price=pr.cost_price
                ) for pr in products
        ]
        session.add_all(pr_in_db_list)
        await session.commit()
        res = await session.execute(select(MProduct))
        pr_m_list = res.scalars().all()
        pr_out_list: list[SProsuctDbOutFull] = [
            MProduct_to_SProsuctDbOutFull(pr) for pr in pr_m_list
        ]
        return pr_out_list


async def add_prduct(product: SProductIn) -> SProsuctDbOut:
    async with async_session() as session:
        pr_m = MProduct(
                remainder=product.quantity, 
                nom_id=product.nom_id,
                cost_price=product.cost_price
                )
        session.add(pr_m)
        await session.commit()
        product_out = MProduct_to_SProsuctDbOutFull(pr_m)
    return product_out
