import hashlib
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.config import get_settings
from app.database import get_db

settings = get_settings()

# Современный способ объявлять FastAPI-зависимости: Depends живёт внутри Annotated,
# а не в значении по умолчанию аргумента. Так линтер (ruff, правило B008) не путает
# вызов Depends() с "опасным" мутабельным дефолтом — и сигнатуру не нужно повторять
# в каждом эндпоинте.
DbSession = Annotated[AsyncSession, Depends(get_db)]

app = FastAPI(
    title="ShrinkIt",
    description="Сократитель ссылок с аналитикой переходов.",
    version="0.1.0",
)


@app.get("/health", tags=["service"])
async def health() -> dict[str, str]:
    """Проверка живости сервиса — её дёргают Docker healthcheck и балансировщик деплоя.
    Никогда не трогает БД: если Postgres прилёг, health всё равно должен ответить,
    чтобы было видно, что упало именно хранилище, а не всё приложение."""
    return {"status": "ok"}


@app.post("/links", response_model=schemas.ShortLinkOut, status_code=201, tags=["links"])
async def create_link(payload: schemas.ShortLinkCreate, db: DbSession):
    link = await crud.create_short_link(db, str(payload.target_url))
    return schemas.ShortLinkOut(
        slug=link.slug,
        target_url=link.target_url,
        short_url=f"{settings.base_url}/{link.slug}",
        created_at=link.created_at,
    )


@app.get("/links/{slug}/stats", response_model=schemas.StatsOut, tags=["links"])
async def stats(slug: str, db: DbSession):
    # Зарегистрирован раньше "/{slug}", хотя такое короткое совпадение здесь
    # и не критично: у него три сегмента пути, а "/{slug}" ловит только один.
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
async def redirect(slug: str, request: Request, db: DbSession):
    link = await crud.get_link_by_slug(db, slug)
    if link is None:
        raise HTTPException(status_code=404, detail="Такой ссылки нет")

    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()  # сырой IP никогда не храним
    await crud.record_click(db, link.id, ip_hash, request.headers.get("user-agent"))

    return RedirectResponse(url=link.target_url, status_code=307)
