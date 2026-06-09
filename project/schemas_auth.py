from datetime import datetime
from decimal import Decimal
from typing import Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, Field, PlainSerializer

# class SUsername(BaseModel):
#     username: str


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


class SUserWithoutPermission(SUserBase):
    model_config = ConfigDict(from_attributes=True)

    balance: float
    disabled: bool = False


class SUserOut(SUserWithoutPermission):
    model_config = ConfigDict(from_attributes=True)

    permissions: list[str] = []


class AuthUserData(BaseModel):
    username: str
    password: str


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


class STopupOut(BaseModel):
    topup: Annotated[
        Decimal,
        PlainSerializer(float, when_used="json"),
        Field(
            description="The ammount of topup, with 2 decimal places",
        ),
    ]
    balance: Annotated[
        Decimal,
        PlainSerializer(float, when_used="json"),
        Field(
            description="The balance past the topup, with 2 decimal places",
        ),
    ]


class STopupIn(BaseModel):
    ammount: Annotated[
        Decimal,
        PlainSerializer(float, when_used="json"),
        Field(
            description="The ammount to topup, with 2 decimal places",
        ),
    ]


class STopup(STopupIn):
    username: str


class SPaymentIn(BaseModel):
    order_id: int
    username: str


class SPaymentInDB(SPaymentIn):
    ammount: Annotated[
        Decimal,
        PlainSerializer(float, when_used="json"),
        Field(
            description="The ammount of payment, with 2 decimal places",
        ),
    ]

    sale_id: int


class SPaymentOut(SPaymentInDB):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created: datetime