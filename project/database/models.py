from datetime import datetime
import enum
from decimal import Decimal
from typing import Any
import uuid
from sqlalchemy import Column, ForeignKey, Table, func, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing_extensions import Annotated


intpk = Annotated[int, mapped_column(primary_key=True)]
timestamp = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.UTC_TIMESTAMP()),
]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class MStatus(enum.Enum):
    PENDING = "pending"
    RECEIVED = "received"
    COMPLETED = "completed"


class MBase(AsyncAttrs, DeclarativeBase):
    id: Mapped[intpk]
    # created_at: Mapped[timestamp]

    def to_dict(self, exclude_none: bool = False) -> dict[Any, Any]:
        """
        Преобразует объект модели в словарь.

        Args:
            exclude_none (bool): Исключать ли None значения из результата

        Returns:
            dict: Словарь с данными объекта
        """

        result = {}

        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)

            # Преобразование специальных типов данных
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)

            # Добавляем значение в результат
            if not exclude_none or value is not None:
                result[column.key] = value

        return result # type: ignore


class MProduct(MBase):
    __tablename__ = "products"

    description: Mapped[str | None]
    cost_price: Mapped[Decimal] = mapped_column(nullable=False)

    @property
    def user_price(self):
        return (self.cost_price * Decimal("1.2")).quantize(Decimal("0.01"))


user_permission_association_table = Table(
    "users_permissions_association_table",
    MBase.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),  # type: ignore
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),  # type: ignore
)


class MUser(MBase):
    __tablename__ = "users"

    username: Mapped[str_uniq]
    full_name: Mapped[str | None]
    email: Mapped[str_uniq]
    hashed_password: Mapped[str]
    disabled: Mapped[bool] = mapped_column(default=False)
    permissions: Mapped[list["MPermission"]] = relationship(
        secondary=user_permission_association_table, back_populates="users"
    )

class Permission(enum.Enum):
    USER_READ = "read user"
    USER_UPDATE = "update user"
    USER_PERMISSIONS_UPDATE = "update user permissions"
    PRODUCT_CREATE = "create product"
    PRODUCT_UPDATE = "update product"

class MPermission(MBase):
    __tablename__ = "permissions"

    name: Mapped[Permission] = mapped_column(unique=True, nullable=False)
    desctription: Mapped[str | None]

    users: Mapped[list[MUser]] = relationship(
        secondary=user_permission_association_table, back_populates="permissions"
    )
