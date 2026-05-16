from typing import Iterable

# from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import delete, update
from sqlalchemy.future import select


from project.schemas_cart import SCart, SCartItem, SCartItemDbOut, SCartItemIn, SCartReq
from project.database.dao_util import clear_table  # type: ignore
from project.database.models import MCartItem
from project.database.session import async_session
import logging

logger = logging.getLogger(__name__)


async def clear_cart_items_table() -> None:
    await clear_table(MCartItem)


async def get_cart(cart_req: SCartReq) -> SCart:
    async with async_session() as session:
        try:
            stmt = select(MCartItem).where(MCartItem.username == cart_req.username)
            # cart_m_list_res = await session.scalars(select(MCartItem))
            cart_m_list_res = await session.scalars(stmt)
            cart_m_list: Iterable[MCartItem] = cart_m_list_res.all()
            cart_out = SCart(
                items=[
                    SCartItem.model_validate(cart)
                    for cart in cart_m_list
                ]
            )
        except Exception as e:
            logger.error(f"error in get_cart: {e.__repr__()}")
            raise

    return cart_out


async def add_update_delete_cart_item(cart_item: SCartItemIn) -> SCartItem:
    async with async_session() as s:
        item = await s.scalar(
            select(MCartItem).filter_by(
                username=cart_item.username, nom_id=cart_item.nom_id
            )
        )
        if item is None:
            if cart_item.quantity <= 0:
                return cart_item
            s.add(MCartItem(**cart_item.model_dump()))
        elif cart_item.quantity <= 0:
            await s.execute(delete(MCartItem).where(MCartItem.id == item.id))
        else:
            await s.execute(update(MCartItem).where(MCartItem.id == item.id).values(quantity=cart_item.quantity))
        await s.commit()
        return cart_item


async def get_all_cards() -> list[SCartItemDbOut]:
    async with async_session() as session:
        iems_res = await session.scalars(select(MCartItem))
        items = iems_res.all()
        items_out = [SCartItemDbOut.model_validate(item) for item in items]
        return items_out

        