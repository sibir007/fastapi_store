

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






