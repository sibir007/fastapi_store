from typing import Iterable

from sqlalchemy import delete, update
from sqlalchemy.future import select


from project.schemas import SUsername
from project.schemas_cart import (
    SCart,
    SCartItem,
    SCartItemDbOut,
    SCartItemIn,
    SUserCart,
)
from project.database.dao import clear_table
from project.database.models_cart import MCartItem
from project.database.session import async_session
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


async def clear_cart_items_table() -> None:
    await clear_table(MCartItem)


async def get_cart(cart_req: SUsername) -> SCart:
    async with async_session() as session:
        try:
            stmt = select(MCartItem).where(MCartItem.username == cart_req.username)
            cart_m_list_res = await session.scalars(stmt)
            cart_m_list: Iterable[MCartItem] = cart_m_list_res.all()
            cart_out = SCart(
                items=[SCartItem.model_validate(cart) for cart in cart_m_list]
            )
        except Exception as e:
            logger.error(f"error in get_cart: {e.__repr__()}")
            raise

    return cart_out


async def clear_cart(cart: SUserCart) -> None:
    async with async_session() as session:
        try:
            stmt = (
                delete(MCartItem)
                .where(MCartItem.username == cart.username)
                .where(MCartItem.nom_id.in_([item.nom_id for item in cart.items]))
            )
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            logger.error(f"error in clear_cart: {e.__repr__()}")
            raise


async def restore_cart(cart: SUserCart) -> None:
    async with async_session() as session:
        try:
            for item in cart.items:
                await add_update_delete_cart_item_whit_session(
                    session, SCartItemIn(username=cart.username, **item.model_dump())
                )
            await session.commit()
        except Exception as e:
            logger.error(f"error in restore_cart: {e.__repr__()}")
            raise


async def add_update_delete_cart_item_whit_session(
    session: AsyncSession, cart_item: SCartItemIn
) -> SCartItem:
    item = await session.scalar(
        select(MCartItem).filter_by(
            username=cart_item.username, nom_id=cart_item.nom_id
        )
    )
    if item is None:
        if cart_item.quantity <= 0:
            return cart_item
        session.add(MCartItem(**cart_item.model_dump()))
    elif cart_item.quantity <= 0:
        await session.execute(delete(MCartItem).where(MCartItem.id == item.id))
    else:
        await session.execute(
            update(MCartItem)
            .where(MCartItem.id == item.id)
            .values(quantity=cart_item.quantity)
        )
    return cart_item


async def add_update_delete_cart_item(cart_item: SCartItemIn) -> SCartItem:
    async with async_session() as s:
        item = await add_update_delete_cart_item_whit_session(s, cart_item)
        await s.commit()
    return item


async def get_all_cards() -> list[SCartItemDbOut]:
    async with async_session() as session:
        iems_res = await session.scalars(select(MCartItem))
        items = iems_res.all()
        items_out = [SCartItemDbOut.model_validate(item) for item in items]
        return items_out
