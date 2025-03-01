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
    IS_DEVELOPMENT: bool = ENVIRONMENT == Environment.DEVELOPMENT
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

    # oauth client credentials
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_OAUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_OAUTH_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_OAUTH_SCOPES: str = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
    OAUTH_DEFAULT_PASSWORD: str = "00000000"
    OAUTH_TOKEN_ALGORITHM: str = "RS256"

    # smtp details
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    # default superuser details
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str

    # storage
    LOCAL_STORAGE_PATH: str
    AWS_BUCKET_NAME: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_REGION: str

    # broker
    BROKER_URL: str

    # compose cors allowed origins
    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        return self.CLIENT_ORIGINS.split(",")

    # specify env file location in development
    _env = ".env" if ENVIRONMENT == Environment.DEVELOPMENT else None

    model_config = SettingsConfigDict(env_file=_env)


AppConfig = Settings()  # type: ignore
