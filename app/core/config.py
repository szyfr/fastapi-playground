from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # App
    APP_NAME: str = "FastAPI MVC"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/db"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # M2M
    M2M_SECRET: str = "m2m-secret-change-in-production"
    M2M_ALGORITHM: str = "HS256"


settings = Settings()
