from typing import Iterable

from sqlalchemy.future import select


from project.database.dao import BaseDAO
from project.database.models_store import MProduct, MNomenclature, MSale, MSaleItem
from project.database.dao import clear_table
from decimal import Decimal
from sqlalchemy import func
from project.database.session import async_session
from project.schemas_store import (
    SProductSummaryOutAdmin,
    SProductSummaryOutByer,
    SNomenclatureIn,
    SNomenclatureOut,
    SProductIn,
    SProsuctDbOut,
    SProsuctDbOutFull,
    SSaleIn,
    SSaleOut,
)


class ProductDAO(BaseDAO[MProduct]):
    model = MProduct


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

# class SNomFilter(BaseModel):
#     name: str | None = None
#     description: str | None = None
#     min_price: Decimal | None = None
#     max_price: Decimal | None = None


async def get_nomenclatures(ids: list[int] | None = None) -> list[SNomenclatureOut]:
    async with async_session() as session:
        stm = select(MNomenclature)
        if ids is not None:
            stm = stm.where(MNomenclature.id.in_(ids))
        nom_m_list_res = await session.execute(stm)
        nom_m_list = nom_m_list_res.scalars().all()
        nom_out = [MNomenclature_to_SNomenclatureOut(n) for n in nom_m_list]
    return nom_out


async def get_products_by_id(
    ids: Iterable[int] | None = None,
) -> list[SProsuctDbOutFull]:
    async with async_session() as session:
        stmt = select(
            MProduct.id,
            MProduct.nom_id,
            MProduct.created,
            MProduct.cost_price,
            MProduct.remainder,
            MNomenclature.name,
            MNomenclature.description,
            MNomenclature.markup,
        ).join(MNomenclature.products)
        if ids is not None:
            stmt = stmt.where(MProduct.id.in_(ids))
        pr_m_list_res = await session.execute(stmt)
        pr_m_list = pr_m_list_res.all()
        pr_out_list = [SProsuctDbOutFull(**pr._asdict()) for pr in pr_m_list]  # type: ignore
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


async def get_nomenclature_by_id(id: int) -> SNomenclatureOut | None:
    async with async_session() as session:
        nom_m_res = await session.execute(
            select(MNomenclature).where(MNomenclature.id == id)
        )
        nom_m = nom_m_res.scalar_one_or_none()
        if nom_m is None:
            return None
        return MNomenclature_to_SNomenclatureOut(nom_m)


async def get_products_summary_for_admin(
    ids: list[int] | None = None,
) -> list[SProductSummaryOutAdmin]:
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
        if ids:
            stm = stm.where(MNomenclature.id.in_(ids))
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


async def get_products_summary_for_byer(
    ids: list[int] | None = None,
) -> list[SProductSummaryOutByer]:
    res_summ = await get_products_summary_for_admin(ids)
    res_summ_byer = [
        SProductSummaryOutAdmin_to_SProductSummaryOutByer(summ_admin_m)
        for summ_admin_m in res_summ
    ]
    return res_summ_byer


# async def _add_sale_item(session: AsyncSession, item: SSaleIn) -> MSaleItem:
#     sale_item_m = MSaleItem(
#         nom_id=item.nom_id,
#         quantity=item.quantity,
#         byer_price=item.byer_price,
#     )
#     session.add(sale_item_m)
#     await session.flush()
#     return sale_item_m


async def add_sale(sale: SSaleIn) -> SSaleOut:
    """add sale to store, decrease remainder of products and increase booked of nomenclature
    1. Get products by nom_id from sale items
    2. If any product is not found, raise exception
    5. Increase booked of nomenclature by quantity in sale item
    6. Commit session
    """
    async with async_session() as session:
        nom_ids = [item.nom_id for item in sale.items]
        products_res = await session.execute(
            select(MNomenclature).where(MNomenclature.id.in_(nom_ids))
        )
        product_noms = products_res.scalars().all()
        if len(product_noms) != len(set(nom_ids)):
            not_found_prods = set(nom_ids) - set(p.id for p in product_noms)
            raise Exception(f"Products not found: {not_found_prods}")
        sale_db_in = MSale(
            order_id=sale.order_id,
            items=[MSaleItem(**item.model_dump()) for item in sale.items],
        )
        prods_noms = {p.id: p for p in product_noms}
        for s_item in sale.items:
            prod = prods_noms[s_item.nom_id]

            prod.booked += s_item.quantity
        session.add(sale_db_in)
        await session.flush()  # to get id of sale_db_in
        await session.commit()
    return SSaleOut.model_validate(sale_db_in)
