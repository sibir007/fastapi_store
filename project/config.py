# import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# for load env vars when run out of docker compose
ch = load_dotenv(".env")

print(f'load_dotenv: {ch}')

# print(os.environ)

class Settings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    # ADMINER_PORT: int

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def POSTGRES_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
                    

settings = Settings() # type: ignore

