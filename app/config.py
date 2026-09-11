import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения — из переменных окружения (docker-compose.yml
    или платформа деплоя), либо локально из .env. Секреты и адреса баз
    не попадают в код."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://shrinkit:shrinkit@localhost:5432/shrinkit"
    redis_url: str = "redis://localhost:6379/0"
    base_url: str = "http://localhost:8000"  # нужен, чтобы собрать полный короткий URL в ответе API
    slug_length: int = 7

    # ссылки неизменяемы, инвалидация не нужна — TTL просто подстраховка
    cache_ttl_seconds: int = 60 * 60 * 24

    # не больше N запросов с одного IP за скользящее окно
    rate_limit_max_requests: int = 5
    rate_limit_window_seconds: int = 60

    def model_post_init(self, __context) -> None:
        # Render сообщает свой реальный домен через RENDER_EXTERNAL_HOSTNAME
        # только во время выполнения — подхватываем его сами, а не полагаемся
        # на то, что вручную вписано в BASE_URL в Dashboard (тот же трюк, что
        # и с ALLOWED_HOSTS в TicketHub).
        render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
        if render_host:
            self.base_url = f"https://{render_host}"


@lru_cache
def get_settings() -> Settings:
    # синглтон — .env читается один раз за процесс
    return Settings()
