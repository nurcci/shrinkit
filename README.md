# ShrinkIt

Сократитель ссылок с аналитикой переходов. Пет-проект №1 из плана трудоустройства
backend-разработчиком — учебный, но собран как настоящий сервис: контейнеризация,
тесты, CI/CD.

## Статус
Неделя 1 — каркас и базовые данные.

## Стек
Python, FastAPI, SQLAlchemy (async), PostgreSQL, Docker / Docker Compose.

## Запуск локально

    docker compose up -d --build
    docker compose exec api python -m app.init_db   # один раз — создаёт таблицы

Swagger-документация: http://localhost:8000/docs

## Тесты

    pip install -r requirements-dev.txt
    pytest
