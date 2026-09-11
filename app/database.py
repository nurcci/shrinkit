from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()


def _prepare_database_url(raw: str) -> tuple[str, dict]:
    """asyncpg не понимает sslmode/channel_binding — это параметры
    psycopg2/libpq, которые в connection string кладут такие провайдеры,
    как Neon. Вырезаем их из URL и просим SSL через connect_args, иначе
    create_async_engine падает с "unexpected keyword argument". Заодно
    подставляем +asyncpg в схему, если её забыли указать вручную."""
    if raw.startswith("postgresql://"):
        raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)
    parts = urlsplit(raw)
    query = parse_qs(parts.query)
    needs_ssl = "sslmode" in query or "channel_binding" in query
    query.pop("sslmode", None)
    query.pop("channel_binding", None)
    clean_url = urlunsplit(parts._replace(query=urlencode(query, doseq=True)))
    return clean_url, ({"ssl": "require"} if needs_ssl else {})


_url, _connect_args = _prepare_database_url(settings.database_url)

# pool_pre_ping спасает от "мёртвых" соединений, если Postgres перезапускался
engine = create_async_engine(_url, pool_pre_ping=True, connect_args=_connect_args)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Общий предок ORM-моделей — по нему init_db.py находит все таблицы."""


async def get_db() -> AsyncSession:
    """Одна сессия на запрос, закрывается сама по завершении."""
    async with AsyncSessionLocal() as session:
        yield session
