@echo off
echo ========================================
echo LIMPEZA TOTAL - Removendo tudo
echo ========================================

echo Parando containers...
docker-compose down

echo.
echo Removendo volumes manualmente...
docker volume rm chatbotprincipal_postgres_data -f
docker volume rm chatbotprincipal_redis -f
docker volume rm chatbotprincipal_chromadb_data -f
docker volume rm chatbotprincipal_evolution_instances -f

echo.
echo ========================================
echo Reconstruindo e iniciando containers
echo ========================================
docker-compose up --build -d

echo.
echo ========================================
echo Aguardando containers iniciarem...
echo ========================================
timeout /t 20 /nobreak

echo.
echo ========================================
echo Status dos containers:
echo ========================================
docker ps

echo.
echo ========================================
echo Logs do backend (ultimas 50 linhas):
echo ========================================
docker logs bot --tail 50

echo.
echo ========================================
echo Logs da Evolution API (ultimas 30 linhas):
echo ========================================
docker logs evolution_api --tail 30

echo.
echo ========================================
echo PRONTO! Acesse:
echo ========================================
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000/docs
echo Admin Dashboard: http://localhost:3000/admin/login
echo Evolution API: http://localhost:8080
echo ========================================
