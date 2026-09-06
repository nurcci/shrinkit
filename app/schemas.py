import datetime as dt

from pydantic import BaseModel, ConfigDict, HttpUrl


class ShortLinkCreate(BaseModel):
    """Тело запроса POST /links. HttpUrl сам провалидирует, что это похоже на URL,
    ещё до того, как запрос доберётся до кода эндпоинта."""

    target_url: HttpUrl


class ShortLinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # разрешает строить схему прямо из ORM-объекта

    slug: str
    target_url: str
    short_url: str
    created_at: dt.datetime


class StatsOut(BaseModel):
    slug: str
    target_url: str
    total_clicks: int
    created_at: dt.datetime
