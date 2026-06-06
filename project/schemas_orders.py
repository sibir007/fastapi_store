from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from project.schemas import OrderStatus


class SOrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nom_id: int
    quantity: int
    byer_price: Decimal


class SOrderId(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # username: str
    id: int


class SOrderIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    items: list[SOrderItem]


class SOrderOut(SOrderIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    status: OrderStatus


    @property
    def total_price(self) -> Decimal:
        return sum(it.quantity*it.byer_price for it in self.items)  # type: ignore