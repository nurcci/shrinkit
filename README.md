# ShrinkIt

![CI](https://github.com/nurcci/shrinkit/actions/workflows/ci.yml/badge.svg)

Сократитель ссылок с аналитикой переходов. Пет-проект №1 из плана трудоустройства
backend-разработчиком — учебный, но собран как настоящий сервис: контейнеризация,
тесты, CI/CD.

## Статус
Недели 1-3 — каркас, Redis-кэш и rate limiting, CI на GitHub Actions.

## Стек
Python, FastAPI, SQLAlchemy (async), PostgreSQL, Redis, Docker / Docker Compose,
Pytest, ruff, GitHub Actions.

## Запуск локально

    docker compose up -d --build
    docker compose exec api python -m app.init_db   # один раз — создаёт таблицы

Swagger-документация: http://localhost:8001/docs

## Тесты

    pip install -r requirements-dev.txt
    pytest -v
