#!/bin/sh
# Прод-запуск для бесплатного деплоя (см. README → «Деплой»).
set -e

echo "==> Создаю таблицы (если их ещё нет)"
python -m app.init_db

echo "==> Запускаю uvicorn"
exec uvicorn app.main:app --host 0.0.0.0 --port 10000 --workers 1
