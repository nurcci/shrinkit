import time

from redis.asyncio import Redis

from app.config import get_settings

settings = get_settings()


async def is_allowed(redis_client: Redis, key: str) -> bool:
    """Sliding-window лимитер поверх отсортированного множества Redis:
    не больше rate_limit_max_requests за последние rate_limit_window_seconds.

    Почему не классический token bucket на Lua-скрипте (EVAL): fakeredis,
    которым гоняются тесты, не поддерживает EVAL без отдельной Lua-прослойки —
    тащить её ради одного счётчика было бы лишней хрупкой зависимостью.
    Атомарность здесь даёт не Lua, а Redis-транзакция (MULTI/EXEC): весь
    пайплайн ниже либо выполняется целиком, либо не выполняется вовсе.
    """
    now = time.time()
    window = settings.rate_limit_window_seconds

    async with redis_client.pipeline(transaction=True) as pipe:
        pipe.zremrangebyscore(key, 0, now - window)  # выбросить события старше окна
        pipe.zadd(key, {str(now): now})              # засчитать текущий запрос
        pipe.zcard(key)                               # сколько запросов осталось в окне
        pipe.expire(key, window)                      # не хранить ключ вечно, если IP затих
        _, _, count, _ = await pipe.execute()

    return count <= settings.rate_limit_max_requests
