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
    redis_url: str = "redis://localhost:6379/0"
    base_url: str = "http://localhost:8000"  # нужен, чтобы собрать полный короткий URL в ответе API
    slug_length: int = 7

    # Ссылки неизменяемы после создания (нет эндпоинта на редактирование),
    # поэтому инвалидация кэша нам не нужна — TTL тут просто подстраховка
    # на случай, если запись когда-нибудь всё же понадобится удалить.
    cache_ttl_seconds: int = 60 * 60 * 24

    # Sliding-window rate limit на создание ссылок: не больше N запросов
    # с одного IP за скользящее окно в window_seconds.
    rate_limit_max_requests: int = 5
    rate_limit_window_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    # lru_cache превращает функцию в синглтон: .env читается один раз за процесс,
    # а не при каждом обращении к настройкам.
    return Settings()
