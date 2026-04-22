from datetime import timedelta, datetime, timezone

from typing import Any


from fastapi import HTTPException, status
from pwdlib import PasswordHash
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from project.auth_schemas import AuthResoult, UserBase, UserInDB


type DB = dict[str, dict[str, str | bool]]

fake_users_db: DB = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Chains",
        "email": "alicechains@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$g2/AV1zwopqUntPKJavBFw$BwpRGDCyUHLvHICnwijyX8ROGoiUPwNKZ7915MeYfCE",
        "disabled": True,
    },
}



password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


async def get_user(username: str) -> UserInDB | None:
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict) # type: ignore
    return None



async def authenticate_user(username: str, password: str) -> AuthResoult:
    user = await get_user(username)
    if not user:

        return AuthResoult(error='Incorrect username or password')
    if user.disabled:
        return AuthResoult(error='User is disabled')
    if not verify_password(password, user.hashed_password):
        return AuthResoult(error='Incorrect username or password')
    return AuthResoult(user=user)


def create_access_token(data: dict[str, Any], expires_delta: timedelta, secret_key: str, algorithm: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, secret_key, algorithm=algorithm)  # type: ignore
    return encoded_jwt

def get_current_user_by_token(token: str) -> UserBase:

    authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # type: ignore
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        scope: str = payload.get("scope", "")
        token_scopes = scope.split(" ")

    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    user: UserBase = UserBase(username=username, scopes=token_scopes) # type: ignore

    return user


