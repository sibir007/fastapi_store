from datetime import timedelta, datetime, timezone

from typing import Annotated, Any


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from pwdlib import PasswordHash
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from project.config import settings

from project.schemas_auth import TokenData

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.AUTH_API_URL,
    scopes={
        "me": "Read information about the current user.",
        "items": "Read items.",
        "cart": "Create, read, update cart.",
        "orders": "Create, read orders.",
        "payment": "Create payment for order.",
        "admin_permissions": "Insert administrator permissions into the token if the user has them",
    },
)


password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


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


async def verifiy_and_get_token_data(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
) -> TokenData:

    token_data: TokenData = verifi_token(
        token, secret_key=SECRET_KEY, algorithm=ALGORITHM
    )
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={
                    "WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'
                },
            )
    return token_data


async def get_token_username(
    token_data: Annotated[TokenData, Depends(verifiy_and_get_token_data)],
) -> str:
    return token_data.username


