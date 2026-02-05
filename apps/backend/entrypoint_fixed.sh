#!/bin/bash
set -e

echo "=== Iniciando Bot WhatsApp (fixed entrypoint) ==="

# Aguardar o PostgreSQL estar pronto
echo "Aguardando PostgreSQL..."
while ! pg_isready -h postgres -p 5432 -U postgres > /dev/null 2>&1; do
    echo "PostgreSQL não está pronto ainda. Aguardando..."
    sleep 2
done
echo "PostgreSQL está pronto!"

# Ir para o diretório do backend (onde estão alembic.ini e o package app)
cd /app/apps/backend

# Rodar migrações do Alembic via módulo python (garante PYTHONPATH)
echo "Rodando migrações do banco de dados..."
python -m alembic upgrade head

# Iniciar a aplicação apontando explicitamente para app.main dentro de apps/backend
echo "Iniciando aplicação..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir /app/apps/backend

