# ShrinkIt

![CI](https://github.com/nurcci/shrinkit/actions/workflows/ci.yml/badge.svg)

Сократитель ссылок с аналитикой переходов: короткий код, редирект,
счётчик кликов на каждую ссылку.

**Живое демо:** _скоро_ _(бесплатный тариф засыпает после простоя —
первый запрос может занять ~30-60 секунд)_

## Стек

Python, FastAPI, SQLAlchemy (async), PostgreSQL, Redis, Docker / Docker
Compose, Pytest, ruff, GitHub Actions.

## Как это устроено

`POST /links` создаёт короткую ссылку — случайный код (7 символов,
база62, с проверкой на коллизию перед записью). `GET /{slug}` делает
редирект и попутно пишет клик (хэш IP, без хранения самого адреса) для
статистики. `GET /links/{slug}/stats` отдаёт число переходов.

Редирект сначала смотрит в Redis (cache-aside, TTL сутки), и только при
промахе идёт в Postgres — на популярных ссылках это снимает почти всю
нагрузку с базы. Создание ссылок ограничено sliding-window рейт-лимитом
на IP через Redis (`ZSET` + `MULTI/EXEC`, без Lua — тестовый fakeredis
её не поддерживает).

Веб-интерфейс (`/`) — форма «вставь ссылку, получи короткую» с
копированием и историей в localStorage поверх того же API. Сам API
отдельно документирован через Swagger — `/docs`.

## Запуск локально

    docker compose up -d --build
    docker compose exec api python -m app.init_db   # один раз — создаёт таблицы

Сайт: http://localhost:8001

Swagger: http://localhost:8001/docs

## Тесты

    pip install -r requirements-dev.txt
    pytest -v

## Деплой

Бесплатно, без карты, тремя сервисами:

- **Render** (`render.yaml`) — один веб-процесс на uvicorn
  (`bin/start-prod.sh`), Docker-рантайм из того же `Dockerfile`, что и
  локально.
- **Neon** — PostgreSQL, бесплатно навсегда. asyncpg не понимает
  `sslmode`/`channel_binding` из строки подключения Neon — `app/database.py`
  вырезает их сам и переводит в SSL через `connect_args`, так что
  connection string можно вставлять как есть.
- **Upstash** — Redis, бесплатно навсегда. Нужен TLS-адрес
  (`rediss://...`), не обычный `redis://`.

Порядок:

1. Neon: создать проект → скопировать connection string.
2. Upstash: создать Redis-базу → собрать `rediss://` адрес из TLS-данных
   в дашборде.
3. Render: New → Blueprint → подключить репозиторий — Render сам
   найдёт `render.yaml`.
4. В Render Dashboard → Environment задать `DATABASE_URL` и `REDIS_URL`.
5. Deploy. Домен и адрес API (`BASE_URL`) подхватываются сами через
   `RENDER_EXTERNAL_HOSTNAME` — вписывать вручную не нужно.

Бесплатный веб-сервис Render засыпает после 15 минут простоя и
просыпается ~30-60 секунд на первый запрос.
