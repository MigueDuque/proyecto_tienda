#!/bin/sh
set -e

echo "Esperando base de datos y aplicando migraciones..."
alembic upgrade head

echo "Ejecutando seed de datos demo..."
python -m scripts.seed

echo "Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
