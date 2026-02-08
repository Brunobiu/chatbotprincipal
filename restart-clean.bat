@echo off
echo ========================================
echo Limpando containers e volumes antigos
echo ========================================
docker-compose down -v

echo.
echo ========================================
echo Reconstruindo e iniciando containers
echo ========================================
docker-compose up --build -d

echo.
echo ========================================
echo Aguardando containers iniciarem...
echo ========================================
timeout /t 15 /nobreak

echo.
echo ========================================
echo Status dos containers:
echo ========================================
docker ps

echo.
echo ========================================
echo Logs do backend (ultimas 30 linhas):
echo ========================================
docker logs bot --tail 30

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
