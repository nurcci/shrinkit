"""Разовая инициализация схемы БД.

Не вызывается автоматически при старте — создание/изменение таблиц
отдельная контролируемая операция, а не побочный эффект запуска
сервиса (в реальном проекте это была бы Alembic-миграция). Запускается
вручную:

    docker compose exec api python -m app.init_db
"""

import asyncio

from app import models  # noqa: F401 — импорт регистрирует модели в Base.metadata
from app.database import Base, engine


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы созданы (или уже существовали).")


if __name__ == "__main__":
    asyncio.run(init_db())
