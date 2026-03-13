#!/bin/bash
set -e

echo "Прогон миграций Alembic..."
alembic upgrade head

echo "Запуск FastAPI сервера..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload