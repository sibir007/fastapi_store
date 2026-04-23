from datetime import datetime
import enum
from decimal import Decimal
from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing_extensions import Annotated


intpk = Annotated[int, mapped_column(primary_key=True)]
timestamp = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.UTC_TIMESTAMP()),
]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]




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


    
user_permission_association_table = Table(
    "association_table",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True), # type: ignore
    Column("permission_id", ForeignKey("permission.id"), primary_key=True), # type: ignore
)


class User(Base):
    __tablename__ = "user"

    username: Mapped[str_uniq]
    full_name: Mapped[str | None]
    email: Mapped[str_uniq]
    hashed_password: Mapped[str]
    disabled: Mapped[bool] = mapped_column(default=False)
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=user_permission_association_table, back_populates="users"
    )


class Permission(Base):
    __tablename__ = "permission"

    permission: Mapped[str_uniq]

    users: Mapped[list[User]] = relationship(
        secondary=user_permission_association_table, back_populates="scopes"
    )