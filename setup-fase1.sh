#!/bin/bash

# Script de Setup - FASE 1
# Configura tudo automaticamente

echo "🚀 Setup FASE 1 - Autenticação Forte"
echo "===================================="
echo ""

# 1. Verificar se .env existe
if [ ! -f .env ]; then
    echo "📋 Copiando .env.example para .env..."
    cp .env.example .env
    echo "✅ .env criado!"
else
    echo "✅ .env já existe"
fi

# 2. Gerar JWT_SECRET_KEY
echo ""
echo "🔐 Gerando JWT_SECRET_KEY..."
JWT_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "Chave gerada: $JWT_KEY"

# 3. Adicionar JWT_SECRET_KEY no .env (se não existir)
if grep -q "JWT_SECRET_KEY=" .env; then
    echo "⚠️  JWT_SECRET_KEY já existe no .env"
    echo "   Chave atual mantida"
else
    echo "" >> .env
    echo "# JWT Secret Key (FASE 1)" >> .env
    echo "JWT_SECRET_KEY=$JWT_KEY" >> .env
    echo "✅ JWT_SECRET_KEY adicionado ao .env"
fi

# 4. Build Docker
echo ""
echo "🐳 Fazendo build do Docker..."
docker-compose build

# 5. Subir containers
echo ""
echo "🚀 Subindo containers..."
docker-compose up -d

# 6. Aguardar PostgreSQL ficar pronto
echo ""
echo "⏳ Aguardando PostgreSQL ficar pronto..."
sleep 10

# 7. Criar bancos de dados
echo ""
echo "🗄️  Criando bancos de dados..."
docker exec -it postgres psql -U postgres -c "CREATE DATABASE IF NOT EXISTS whatsapp_bot;"
docker exec -it postgres psql -U postgres -c "CREATE DATABASE IF NOT EXISTS evolution;"
echo "✅ Bancos criados!"

# 8. Aplicar migrations
echo ""
echo "📊 Aplicando migrations (FASE 1)..."
docker exec -it bot alembic upgrade head
echo "✅ Migrations aplicadas!"

# 9. Verificar health
echo ""
echo "🏥 Verificando health..."
sleep 5
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "✅ Setup completo!"
echo ""
echo "🌐 URLs disponíveis:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🧪 Testar login FASE 1:"
echo '   curl -X POST http://localhost:8000/api/v1/auth-v2/login \'
echo '     -H "Content-Type: application/json" \'
echo '     -d '"'"'{"email": "teste@teste.com", "senha": "teste123"}'"'"
echo ""
