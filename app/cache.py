import json

from redis.asyncio import Redis

from app import models
from app.config import get_settings

settings = get_settings()


def _cache_key(slug: str) -> str:
    return f"link:{slug}"


async def get_cached_link(redis_client: Redis, slug: str) -> dict | None:
    """None — промах, идём в Postgres."""
    raw = await redis_client.get(_cache_key(slug))
    return json.loads(raw) if raw else None


async def set_cached_link(redis_client: Redis, link: models.ShortLink) -> None:
    payload = json.dumps({"id": str(link.id), "target_url": link.target_url})
    await redis_client.set(_cache_key(link.slug), payload, ex=settings.cache_ttl_seconds)
