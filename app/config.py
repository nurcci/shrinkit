from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Централизованная конфигурация приложения.

    Значения читаются из переменных окружения (их задаёт docker-compose.yml
    или платформа деплоя) — либо, локально без Docker, из файла .env.
    Так секреты и адреса баз никогда не попадают в код.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://shrinkit:shrinkit@localhost:5432/shrinkit"
    base_url: str = "http://localhost:8000"  # нужен, чтобы собрать полный короткий URL в ответе API
    slug_length: int = 7


@lru_cache
def get_settings() -> Settings:
    # lru_cache превращает функцию в синглтон: .env читается один раз за процесс,
    # а не при каждом обращении к настройкам.
    return Settings()
