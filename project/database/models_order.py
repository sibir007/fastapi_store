from sqlalchemy import ForeignKey

from decimal import Decimal

from project.database.models_base import MBase, timestamp
from project.schemas import OrderStatus


from sqlalchemy.orm import Mapped, mapped_column, relationship

class MOrder(MBase):
    __tablename__ = "orders"
    created_at: Mapped[timestamp]
    username: Mapped[str]
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.WAITING)
    items: Mapped[list["MOrderItem"]] = relationship(
        "MOrderItem",
        back_populates="order",
        lazy="selectin",
        cascade="all, delete",
    )

class MOrderItem(MBase):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    order: Mapped[MOrder] = relationship(
        MOrder,
        back_populates="items",
    )
    nom_id: Mapped[int]
    quantity: Mapped[int]
    byer_price: Mapped[Decimal]

