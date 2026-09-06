import datetime as dt
import uuid

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ShortLink(Base):
    """Одна короткая ссылка: slug -> куда редиректить."""

    __tablename__ = "short_links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    target_url: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    clicks: Mapped[list["ClickEvent"]] = relationship(
        back_populates="link", cascade="all, delete-orphan"
    )


class ClickEvent(Base):
    """Один переход по короткой ссылке. Строк тут будет на порядки больше,
    чем в short_links, поэтому сразу ставим составной индекс под будущую агрегацию."""

    __tablename__ = "click_events"
    __table_args__ = (Index("ix_click_events_link_created", "link_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    link_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("short_links.id", ondelete="CASCADE")
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(256), nullable=True)

    link: Mapped["ShortLink"] = relationship(back_populates="clicks")
