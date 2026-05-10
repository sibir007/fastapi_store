from datetime import datetime
from decimal import Decimal


from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    # username: str | None = None
    scopes: list[str] = []


class SUserBase(BaseModel):
    username: str
    full_name: str | None = None
    email: EmailStr


class SUserIn(SUserBase):
    password: str


class SUserInDB(SUserBase):
    hashed_password: str


class SUserOut(SUserBase):
    permissions: list[str] = []
    disabled: bool = False

    # async def add_nomenclatures(nomenclatures: Iterable[SNomenclatureIn]) -> list[SNomenclatureOut]:
    """class MNomenclature(MBase):
    __tablename__  = "nomenclature"
 
    created: Mapped[timestamp]
    name: Mapped[str_uniq]
    description: Mapped[str | None]
    booked: Mapped[int] = mapped_column(default=0)
    products: Mapped[list["MProduct"]] = relationship("MProduct", back_populates="nomenclature")

    """

class SProducIntBase(BaseModel):
    nom_id: int
    cost_price: Decimal

class SProductIn(SProducIntBase):
    quantity: int

class SProductInDb(SProducIntBase):
    remainder: int


class SProsuctDbOut(BaseModel):
    id: int
    created: datetime
    nom_id: int
    cost_price: Decimal
    remainder: int


class SProsuctDbOutFull(SProsuctDbOut):
    name: str
    description: str | None


class SProductOutPurchaser(BaseModel):
    nom_id: int
    name: str
    description: str
    selling_price: Decimal
    remainder: int


class SNomenclatureIn(BaseModel):
    name: str
    description: str
    products: list[SProsuctDbOutFull] = []

class SNomenclatureOut(SNomenclatureIn):
    id: int
    created: datetime


class AuthUserData(BaseModel):
    username: str
    password: str


class BrokerExeption(BaseModel):
    code: int
    detailes: str


class BorkerResoultBase(BaseModel):
    exeption: BrokerExeption | None = None


class UserBrokerResult(BorkerResoultBase):
    result: SUserOut | None = None


class UserFilter(BaseModel):
    id: int | None = None
    username: str | None = None
    full_name: EmailStr | None = None
    email: str | None = None


class SPermissionIn(BaseModel):
    name: str
    desctription: str | None = None


class SPermissionOut(SPermissionIn):
    id: int
