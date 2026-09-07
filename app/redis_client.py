from collections.abc import AsyncGenerator

import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()

# Один пул соединений на процесс — переиспользуется всеми запросами,
# а не создаётся заново на каждый (аналог движка SQLAlchemy в database.py).
redis_pool = redis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """FastAPI-зависимость: клиент Redis из общего пула соединений."""
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.aclose()
