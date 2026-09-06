from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# pool_pre_ping проверяет соединение перед использованием — спасает от "battery died"
# ошибок, если Postgres перезапускался, а пул держал протухшее соединение.
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Общий предок всех ORM-моделей. SQLAlchemy собирает метаданные таблиц
    (Base.metadata) по всем классам-наследникам — это то, что использует
    init_db.py для создания таблиц."""


async def get_db() -> AsyncSession:
    """FastAPI-зависимость (Depends): открывает одну сессию на запрос
    и гарантированно закрывает её по завершении, даже если внутри было исключение."""
    async with AsyncSessionLocal() as session:
        yield session
