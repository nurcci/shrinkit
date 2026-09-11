"""Инициализация схемы БД. Локально — разовая контролируемая операция,
а не побочный эффект запуска (в реальном проекте это была бы Alembic-
миграция):

    docker compose exec api python -m app.init_db

В проде (bin/start-prod.sh) вызывается при каждом старте контейнера —
create_all идемпотентна (создаёт только то, чего ещё нет), а на
бесплатном тарифе Render нет Shell, чтобы дёрнуть это вручную."""

import asyncio

from app import models  # noqa: F401 — импорт регистрирует модели в Base.metadata
from app.database import Base, engine


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы созданы (или уже существовали).")


if __name__ == "__main__":
    asyncio.run(init_db())
