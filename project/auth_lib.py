from datetime import timedelta, datetime, timezone

from typing import Any


from fastapi import HTTPException, status
from pwdlib import PasswordHash
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from project.auth_schemas import TokenData, UserFilter
from project.database.dao import UserDAO
from project.database.models import MUser
from sqlalchemy.ext.asyncio import AsyncSession

type DB = dict[str, dict[str, str | bool | list[str]]]

fake_users_db: DB = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
        "permissions": ["user:read", "user:write"],
    },
    "john": {
        "username": "john",
        "full_name": "John",
        "email": "john@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
        "permissions": [],
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Chains",
        "email": "alicechains@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$g2/AV1zwopqUntPKJavBFw$BwpRGDCyUHLvHICnwijyX8ROGoiUPwNKZ7915MeYfCE",
        "disabled": True,
        "permissions": [],
    },
}


password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


async def get_user_by_name(session: AsyncSession, username: str) -> MUser | None:

    user_dao: UserDAO = UserDAO(session)
    user: MUser | None = await user_dao.find_one_or_none(filters=UserFilter(username=username))  # type: ignore
    return user  # type: ignore


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta, secret_key: str, algorithm: str
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, secret_key, algorithm=algorithm)  # type: ignore
    return encoded_jwt


def verifi_token(token: str, secret_key: str, algorithm: str) -> TokenData:

    authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])  # type: ignore
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        scope: str = payload.get("scope", "")
        token_scopes = scope.split(" ")

    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    token_data: TokenData = TokenData(username=username, scopes=token_scopes)  # type: ignore

    return token_data


# async def register_user(user:)
