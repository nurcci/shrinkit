# ShrinkIt

![CI](https://github.com/nurcci/shrinkit/actions/workflows/ci.yml/badge.svg)

Сократитель ссылок с аналитикой переходов: короткий код, редирект,
счётчик кликов на каждую ссылку.

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
