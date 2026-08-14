from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://granero:granero@localhost:5432/granero"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    # 0 (or less) = the session never expires. Set a positive number of minutes
    # to force users to log in again after that time.
    jwt_expire_minutes: int = 0
    admin_email: str = "admin@granero.com"
    admin_password: str = "admin123"
    admin_full_name: str = "Administrador"
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
