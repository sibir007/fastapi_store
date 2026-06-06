
from project.database.models import timestamp
from project.database.models_base import MBase, str_uniq


from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from decimal import Decimal


class MNomenclature(MBase):
    __tablename__ = "nomenclature"

    created: Mapped[timestamp]
    name: Mapped[str_uniq]
    description: Mapped[str | None]
    booked: Mapped[int] = mapped_column(default=0)
    markup: Mapped[Decimal] = mapped_column(default=Decimal("0.2"))
    # markup: Mapped[Decimal | None] = mapped_column(default=0.2)
    products: Mapped[list["MProduct"]] = relationship(
        "MProduct",
        back_populates="nomenclature",
        lazy="selectin",
        cascade="all, delete",
    )


class MProduct(MBase):
    __tablename__ = "products"

    created: Mapped[timestamp]

    # created: Mapped[timestamp]
    nom_id: Mapped[int] = mapped_column(
        ForeignKey("nomenclature.id", ondelete="CASCADE"), nullable=False
    )
    nomenclature: Mapped[MNomenclature] = relationship(
        MNomenclature,
        back_populates="products",
        lazy="selectin",
    )
    cost_price: Mapped[Decimal]
    remainder: Mapped[int]

    @property
    def user_price(self):
        return (self.cost_price * Decimal("1.2")).quantize(Decimal("0.01"))


class MSale(MBase):
    __tablename__ = "sales"
    created: Mapped[timestamp]
    order_id: Mapped[int]
    items: Mapped[list["MSaleItem"]] = relationship(
        "MSaleItem",
        back_populates="sale",
        lazy="selectin",
        cascade="all, delete",
    )


class MSaleItem(MBase):
    __tablename__ = "sale_items"

    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id", ondelete="CASCADE")
    )
    sale: Mapped[MSale] = relationship(
        MSale,
        back_populates="items",
    )
    nom_id: Mapped[int]
    quantity: Mapped[int]
    byer_price: Mapped[Decimal]
