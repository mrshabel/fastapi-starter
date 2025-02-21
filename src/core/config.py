from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"
    PRODUCTION = "PRODUCTION"


class Settings(BaseSettings):
    # core
    PROJECT_TITLE: str = "FastAPI Starter"
    PROJECT_DESCRIPTION: str = "A FastAPI starter template for developing APIs"
    PROJECT_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    # database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20

    # security
    CLIENT_ORIGINS: str
    ALLOWED_METHODS: list[str] = ["GET", "POST", "DELETE", "PATCH", "PUT", "OPTIONS"]
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_HOURS: int
    OTP_EXPIRE_MINUTES: int = 10

    # compose cors allowed origins
    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        return self.CLIENT_ORIGINS.split(",")

    # specify env file location in development
    _env = ".env" if ENVIRONMENT == Environment.DEVELOPMENT else None

    model_config = SettingsConfigDict(env_file=_env)


AppConfig = Settings()
