from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Cloud ToDo API"
    env: Literal["local", "test", "dev", "prod"] = "local"
    api_key: str = Field(default="dev-api-key", min_length=8)
    database_url: str = "postgresql+psycopg://todo:todo@localhost:5432/todo"
    cors_origins: str = "http://localhost:5173,http://localhost:8080,http://localhost:8000"
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
