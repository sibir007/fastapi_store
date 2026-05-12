from typing import Iterable

from sqlalchemy.future import select


from project.schemas_products import SProductSummaryOutAdmin, SProductSummaryOutByer
from project.database.dao import MProduct
from project.database.dao_util import clear_table  # type: ignore
from project.database.models import Decimal, MNomenclature, func
from project.database.session import async_session
from project.schemas_products import SNomenclatureIn, SNomenclatureOut, SProductIn, SProsuctDbOut, SProsuctDbOutFull


async def clear_nomenclature_table() -> None:
    await clear_table(MNomenclature)


async def clear_product_table() -> None:
    await clear_table(MProduct)


def MProduct_to_SProsuctDbOut(product: MProduct) -> SProsuctDbOut:
    return SProsuctDbOut(**product.to_dict())


def MNomenclature_to_SNomenclatureOut(nomenclature: MNomenclature) -> SNomenclatureOut:
    products: Iterable[MProduct] = nomenclature.products
    products_out = [MProduct_to_SProsuctDbOut(p) for p in products]
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


# async def add_nomenclature(nomenclature: SNomenclatureIn) -> SNomenclatureOut:
#     async with async_session() as session:
#         nom_m = MNomenclature(**nomenclature.model_dump())
#         session.add(nom_m)
#         await session.commit()
#         nom_out = MNomenclature_to_SNomenclatureOut(nom_m)
#     return nom_out


async def get_nomenclatures() -> list[SNomenclatureOut]:
    async with async_session() as session:
        nom_m_list_res = await session.execute(select(MNomenclature))
        nom_m_list = nom_m_list_res.scalars().all()
        nom_out = [MNomenclature_to_SNomenclatureOut(n) for n in nom_m_list]
    return nom_out


async def get_products_by_id(ids: Iterable[int]) -> list[SProsuctDbOutFull]:
    async with async_session() as session:
        stmt = (
            select(
                MProduct.id,
                MProduct.nom_id,
                MProduct.created,
                MProduct.cost_price,
                MProduct.remainder,
                MNomenclature.name,
                MNomenclature.description,
                MNomenclature.markup,
            )
            .join(MNomenclature.products)
            .where(MProduct.id.in_(ids))
        )
        pr_m_list_res = await session.execute(stmt)
        pr_m_list = pr_m_list_res.all()
        pr_out_list = [SProsuctDbOutFull(**pr._asdict()) for pr in pr_m_list] # type: ignore
    return pr_out_list


async def add_products(products: Iterable[SProductIn]) -> list[SProsuctDbOutFull]:
    async with async_session() as session:
        pr_in_db_list = [
            MProduct(remainder=pr.quantity, nom_id=pr.nom_id, cost_price=pr.cost_price)
            for pr in products
        ]
        session.add_all(pr_in_db_list)
        await session.commit()

        return await get_products_by_id([pr.id for pr in pr_in_db_list])


# async def add_prduct(product: SProductIn) -> SProsuctDbOutFull:
#     async with async_session() as session:
#         pr_m = MProduct(
#             remainder=product.quantity,
#             nom_id=product.nom_id,
#             cost_price=product.cost_price,
#         )
#         session.add(pr_m)
#         await session.commit()
#         product_out = MProduct_to_SProsuctDbOut(pr_m)
#     return product_out


async def get_products_summary_for_admin() -> list[SProductSummaryOutAdmin]:
    """
    return products grouped by nom_id with sum of
    remainder quantity and maximum cost price
    for each nom_id
    """
    async with async_session() as session:
        stm = (
            select(
                MNomenclature.id,
                MNomenclature.name,
                MNomenclature.description,
                MNomenclature.markup,
                MNomenclature.booked,
                func.sum(MProduct.remainder).label("total_remainder"),
                func.max(MProduct.cost_price).label("max_cost_price"),
            )
            .join(MNomenclature.products)
            .group_by(MNomenclature.id)
        )
        r = await session.execute(stm)

        res = r.all()
        # print([row._asdict() for row in res]) # type: ignore
        res_out = [SProductSummaryOutAdmin(**row._asdict()) for row in res]  # type: ignore

    return res_out


def SProductSummaryOutAdmin_to_SProductSummaryOutByer(
    summ_admin_m: SProductSummaryOutAdmin,
) -> SProductSummaryOutByer:
    summ_admin_dict = summ_admin_m.model_dump()
    summ_admin_dict.update(
        {"total_remainder": summ_admin_m.total_remainder - summ_admin_m.booked}
    )
    return SProductSummaryOutByer(
        **summ_admin_dict,
        selling_price=(summ_admin_m.max_cost_price * (Decimal("1") + summ_admin_m.markup)).quantize(  # type: ignore
            Decimal("1.00")
        ),
    )


async def get_products_summary_for_byer() -> list[SProductSummaryOutByer]:
    res_summ = await get_products_summary_for_admin()
    res_summ_byer = [
        SProductSummaryOutAdmin_to_SProductSummaryOutByer(summ_admin_m)
        for summ_admin_m in res_summ
    ]
    return res_summ_byer
