from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# pool_pre_ping спасает от "мёртвых" соединений, если Postgres перезапускался
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Общий предок ORM-моделей — по нему init_db.py находит все таблицы."""


async def get_db() -> AsyncSession:
    """Одна сессия на запрос, закрывается сама по завершении."""
    async with AsyncSessionLocal() as session:
        yield session
