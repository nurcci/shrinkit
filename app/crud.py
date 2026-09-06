import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.config import get_settings
from app.slug import generate_slug

settings = get_settings()


async def create_short_link(db: AsyncSession, target_url: str) -> models.ShortLink:
    for _ in range(5):  # 5 попыток на случай редкой коллизии слага
        slug = generate_slug(settings.slug_length)
        taken = await db.scalar(select(models.ShortLink.id).where(models.ShortLink.slug == slug))
        if taken is None:
            break
    else:
        raise RuntimeError("Не удалось подобрать свободный slug — увеличьте slug_length")

    link = models.ShortLink(slug=slug, target_url=target_url)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def get_link_by_slug(db: AsyncSession, slug: str) -> models.ShortLink | None:
    return await db.scalar(select(models.ShortLink).where(models.ShortLink.slug == slug))


async def record_click(
    db: AsyncSession, link_id: uuid.UUID, ip_hash: str | None, user_agent: str | None
) -> None:
    db.add(models.ClickEvent(link_id=link_id, ip_hash=ip_hash, user_agent=user_agent))
    await db.commit()


async def get_stats(db: AsyncSession, slug: str) -> tuple[models.ShortLink, int] | None:
    link = await get_link_by_slug(db, slug)
    if link is None:
        return None
    total = await db.scalar(
        select(func.count(models.ClickEvent.id)).where(models.ClickEvent.link_id == link.id)
    )
    return link, total or 0
