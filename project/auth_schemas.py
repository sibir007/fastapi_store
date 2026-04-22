from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


class UserBase(BaseModel):
    username: str
    scopes: list[str] = []


class User(UserBase):
    email: str | None = None
    disabled: bool = False


class UserInDB(User):
    hashed_password: str

class AuthUserData(BaseModel):
    username: str
    password: str


class AuthResoult(BaseModel):
    user: UserInDB | None = None
    error: str | None = None
