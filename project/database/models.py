from datetime import datetime
import enum
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing_extensions import Annotated


intpk = Annotated[int, mapped_column(primary_key=True)]
timestamp = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.UTC_TIMESTAMP()),
]

class Status(enum.Enum):
    PENDING = "pending"
    RECEIVED = "received"
    COMPLETED = "completed"

class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[intpk]
    # created_at: Mapped[timestamp]


class Product(Base):
    __tablename__ = 'product'

    description: Mapped[str | None]
    cost_price: Mapped[Decimal] = mapped_column(nullable=False)

    @property
    def user_price(self):
        return (self.cost_price * Decimal("1.2")).quantize(Decimal("0.01"))


