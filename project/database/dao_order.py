from project.database.dao import BaseDAO
from project.database.models_order import MOrder, MOrderItem
from project.database.session import async_session
from project.schemas import OrderStatus
from project.schemas_orders import SOrderIn, SOrderOut
from sqlalchemy.future import select


class OrderDAO(BaseDAO[MOrder]):
    model = MOrder


async def add_order(order: SOrderIn) -> SOrderOut:
    async with async_session() as session:

        order_items_m = [
            MOrderItem(
                # order_id=order_m.id,
                nom_id=item.nom_id,
                quantity=item.quantity,
                byer_price=item.byer_price,
            )
            for item in order.items
        ]
        order_m = MOrder(username=order.username, items=order_items_m)
        session.add(order_m)
        # await session.flush()
        # session.add_all(order_items_m)
        await session.commit()
        order_out = SOrderOut.model_validate(order_m)
    return order_out


async def cancel_order(order_id: int) -> SOrderOut | None:
    """if order with order_id exist and have status WAITING, set status CANCELED and return order out, else return None
    1. Get order by order_id
    2. If order is None, return None
    3. If order status is not WAITING, return None
    4. Set order status to CANCELED
    5. Commit session
    6. Return order out
    """
    async with async_session() as session:
        order_m = await session.get(MOrder, order_id)
        if order_m is None:
            return order_m
        elif order_m.status == OrderStatus.WAITING:
            order_m.status = OrderStatus.CANCELED
            await session.commit()
            order_out = SOrderOut.model_validate(order_m)
            return order_out
        return None


async def get_order(order_id: int) -> SOrderOut | None:
    async with async_session() as session:
        order_m = await session.get(MOrder, order_id)
        if order_m is None:
            return order_m
        order_out = SOrderOut.model_validate(order_m)
    return order_out


async def get_orders_by_status(
    username: str, status: list[OrderStatus]
) -> list[SOrderOut]:
    async with async_session() as session:
        orders_sc = await session.scalars(
            select(MOrder).where(MOrder.username == username, MOrder.status.in_(status))
        )
        orders_list = orders_sc.all()

        orders_out = [SOrderOut.model_validate(order) for order in orders_list]
    return orders_out


async def get_all_not_canceled_orders(username: str) -> list[SOrderOut]:
    return await get_orders_by_status(
        username, [OrderStatus.WAITING, OrderStatus.COMPLETED, OrderStatus.PAID]
    )


async def get_all_orders(username: str) -> list[SOrderOut]:
    return await get_orders_by_status(
        username,
        [
            OrderStatus.WAITING,
            OrderStatus.COMPLETED,
            OrderStatus.PAID,
            OrderStatus.CANCELED,
        ],
    )


async def get_all_witing_orders(username: str) -> list[SOrderOut]:
    return await get_orders_by_status(username, [OrderStatus.WAITING])


async def get_all_canceled_orders(username: str) -> list[SOrderOut]:
    return await get_orders_by_status(username, [OrderStatus.CANCELED])


async def get_all_completed_orders(username: str) -> list[SOrderOut]:
    return await get_orders_by_status(username, [OrderStatus.COMPLETED])


async def get_all_paid_orders(username: str) -> list[SOrderOut]:
    return await get_orders_by_status(username, [OrderStatus.PAID])


async def _set_order_status(set_status: OrderStatus, order_id: int, initial_order_state: OrderStatus) -> SOrderOut | None:
    async with async_session() as session:
        order_m = await session.get(MOrder, order_id)
            
        if order_m is None:
            return order_m
        if order_m.status != initial_order_state:
            raise ValueError(f"Error order status: {order_m.status}, expected status: {initial_order_state}")
        order_m.status = set_status
        await session.commit()
        order_out = SOrderOut.model_validate(order_m)
    return order_out


async def set_canceled_order_status(order_id: int):
    return await _set_order_status(OrderStatus.CANCELED, order_id, OrderStatus.WAITING)


async def set_paid_order_status(order_id: int):
    return await _set_order_status(OrderStatus.PAID, order_id, OrderStatus.WAITING)


async def set_completed_order_status(order_id: int):
    return await _set_order_status(OrderStatus.COMPLETED, order_id, OrderStatus.PAID)
