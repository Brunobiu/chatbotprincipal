#!/bin/bash
set -e

echo "=== Iniciando Bot WhatsApp ==="

# Aguardar o PostgreSQL estar pronto
echo "Aguardando PostgreSQL..."
while ! pg_isready -h postgres -p 5432 -U postgres > /dev/null 2>&1; do
    echo "PostgreSQL não está pronto ainda. Aguardando..."
    sleep 2
done
echo "PostgreSQL está pronto!"

# Rodar migrações do Alembic
echo "Rodando migrações do banco de dados..."
cd /app
alembic upgrade head

# Iniciar a aplicação
echo "Iniciando aplicação..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
