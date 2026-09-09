import hashlib
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.cache import get_cached_link, set_cached_link
from app.config import get_settings
from app.database import get_db
from app.rate_limit import is_allowed
from app.redis_client import get_redis

settings = get_settings()

# Depends живёт внутри Annotated, а не в значении по умолчанию аргумента —
# так ruff/B008 не ругается на "вызов функции в дефолте".
DbSession = Annotated[AsyncSession, Depends(get_db)]
RedisSession = Annotated[Redis, Depends(get_redis)]

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="ShrinkIt",
    description="Сократитель ссылок с аналитикой переходов.",
    version="0.2.0",
)

# веб-интерфейс поверх JSON API ниже: форма создаёт ссылку через fetch к /links
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


async def enforce_rate_limit(request: Request, redis_client: RedisSession) -> None:
    """Страж перед POST /links — самому эндпоинту не нужно знать про лимиты."""
    client_ip = request.client.host if request.client else "unknown"
    allowed = await is_allowed(redis_client, f"ratelimit:create_link:{client_ip}")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Слишком много ссылок с этого адреса — попробуйте позже",
        )


@app.get("/health", tags=["service"])
async def health() -> dict[str, str]:
    """Проверка живости — Docker healthcheck и балансировщик деплоя. Не трогает
    БД/Redis, чтобы было видно, что упало именно хранилище, а не всё приложение."""
    return {"status": "ok"}


@app.post(
    "/links",
    response_model=schemas.ShortLinkOut,
    status_code=201,
    tags=["links"],
    dependencies=[Depends(enforce_rate_limit)],
)
async def create_link(payload: schemas.ShortLinkCreate, db: DbSession, redis_client: RedisSession):
    link = await crud.create_short_link(db, str(payload.target_url))
    # write-through: кэшируем сразу, чтобы и первый переход попал в кэш
    await set_cached_link(redis_client, link)
    return schemas.ShortLinkOut(
        slug=link.slug,
        target_url=link.target_url,
        short_url=f"{settings.base_url}/{link.slug}",
        created_at=link.created_at,
    )


@app.get("/links/{slug}/stats", response_model=schemas.StatsOut, tags=["links"])
async def stats(slug: str, db: DbSession):
    # читаем из Postgres, не из кэша — total_clicks должен быть свежим
    result = await crud.get_stats(db, slug)
    if result is None:
        raise HTTPException(status_code=404, detail="Такой ссылки нет")
    link, total_clicks = result
    return schemas.StatsOut(
        slug=link.slug,
        target_url=link.target_url,
        total_clicks=total_clicks,
        created_at=link.created_at,
    )


@app.get("/{slug}", tags=["links"])
async def redirect(slug: str, request: Request, db: DbSession, redis_client: RedisSession):
    cached = await get_cached_link(redis_client, slug)
    if cached is not None:
        link_id = uuid.UUID(cached["id"])
        target_url = cached["target_url"]
    else:
        link = await crud.get_link_by_slug(db, slug)
        if link is None:
            raise HTTPException(status_code=404, detail="Такой ссылки нет")
        await set_cached_link(redis_client, link)
        link_id = link.id
        target_url = link.target_url

    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()  # сырой IP никогда не храним
    await crud.record_click(db, link_id, ip_hash, request.headers.get("user-agent"))

    return RedirectResponse(url=target_url, status_code=307)
