import enum

from sqlalchemy.orm import Mapped, mapped_column, relationship

from decimal import Decimal

from project.database.models_base import MBase, str_uniq


from sqlalchemy import Column, ForeignKey, Table

from project.database.models_order import timestamp

user_permission_association_table = Table(
    "users_permissions_association_table",
    MBase.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),  # type: ignore
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),  # type: ignore
)


class Permission(enum.Enum):
    USER_READ = "read user"
    USER_UPDATE = "update user"
    USER_PERMISSIONS_UPDATE = "update user permissions"
    PRODUCT_CREATE = "create product"
    PRODUCT_UPDATE = "update product"


class MUser(MBase):
    __tablename__ = "users"

    username: Mapped[str_uniq]
    full_name: Mapped[str | None]
    email: Mapped[str_uniq]
    hashed_password: Mapped[str]
    disabled: Mapped[bool] = mapped_column(default=False)
    balance: Mapped[Decimal] = mapped_column(default=0)
    permissions: Mapped[list["MPermission"]] = relationship(
        secondary=user_permission_association_table,
        back_populates="users",
        lazy="selectin",
        cascade="all, delete",
    )


class MPermission(MBase):
    __tablename__ = "permissions"

    name: Mapped[Permission] = mapped_column(unique=True, nullable=False)
    desctription: Mapped[str | None]

    users: Mapped[list[MUser]] = relationship(
        secondary=user_permission_association_table,
        back_populates="permissions",
        cascade="all, delete",
    )

class MPayment(MBase):
    __tablename__ = "payments"


    created: Mapped[timestamp]
    username: Mapped[str]
    order_id: Mapped[int]
    sale_id: Mapped[int]
    ammount: Mapped[Decimal]