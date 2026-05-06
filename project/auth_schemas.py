from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    # username: str | None = None
    scopes: list[str] = []


class UserBase(BaseModel):
    username: str
    full_name: str | None = None
    email: EmailStr


class UserIn(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


class UserOut(UserBase):
    permissions: list[str] = []
    disabled: bool = False


class AuthUserData(BaseModel):
    username: str
    password: str


class BrokerExeption(BaseModel):
    code: int
    detailes: str


class BorkerResoultBase(BaseModel):
    exeption: BrokerExeption | None = None


class UserBrokerResult(BorkerResoultBase):
    result: UserOut | None = None

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