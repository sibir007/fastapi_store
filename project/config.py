import os
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

TESTS_CONFIG = os.environ.get("TESTS_CONFIG", False)
ENV_FILE = ".env"

# for load env vars when run out of docker compose
ch = load_dotenv(ENV_FILE)

print(f"TESTS_CONFIG = {TESTS_CONFIG}, load_dotenv: {ch}")

# print(os.environ)


class Settings(BaseSettings):

    TESTS_CONFIG: bool

    REDIS_HOST: str
    REDIS_PORT: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    # ADMINER_PORT: int

    AUTH_API_SCHEME: str
    AUTH_API_HOST: str
    AUTH_API_PORT: str
    AUTH_API_PATH: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ORDER_VALIDITY_SEC: int

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def POSTGRES_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def AUTH_API_URL(self) -> str:
        return f"{self.AUTH_API_SCHEME}://{self.AUTH_API_HOST}:{self.AUTH_API_PORT}/{self.AUTH_API_PATH}"


class TestSettings(Settings):
    
    REDIS_HOST: str = Field(alias="TEST_REDIS_HOST")
    REDIS_PORT: str = Field(alias="TEST_REDIS_PORT")

    POSTGRES_HOST: str = Field(alias="TEST_POSTGRES_HOST")
    POSTGRES_PORT: int = Field(alias="TEST_POSTGRES_PORT")
    POSTGRES_USER: str = Field(alias="TEST_POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(alias="TEST_POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(alias="TEST_POSTGRES_DB")

    AUTH_API_SCHEME: str = Field(alias="TEST_AUTH_API_SCHEME")
    AUTH_API_HOST: str = Field(alias="TEST_AUTH_API_HOST")
    AUTH_API_PORT: str = Field(alias="TEST_AUTH_API_PORT")
    AUTH_API_PATH: str = Field(alias="TEST_AUTH_API_PATH")

    SECRET_KEY: str = Field(alias="TEST_SECRET_KEY")
    ALGORITHM: str = Field(alias="TEST_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(alias="TEST_ACCESS_TOKEN_EXPIRE_MINUTES")
    ORDER_VALIDITY_SEC: int = Field(alias="TEST_ORDER_VALIDITY_SEC")



settings = Settings()  if not TESTS_CONFIG else TestSettings() # type: ignore

print(settings.model_dump_json())