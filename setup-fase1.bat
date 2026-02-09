@echo off
REM Script de Setup - FASE 1 (Windows)
REM Configura tudo automaticamente

echo.
echo ========================================
echo   Setup FASE 1 - Autenticacao Forte
echo ========================================
echo.

REM 1. Verificar se .env existe
if not exist .env (
    echo Copiando .env.example para .env...
    copy .env.example .env
    echo OK .env criado!
) else (
    echo OK .env ja existe
)

REM 2. Gerar JWT_SECRET_KEY
echo.
echo Gerando JWT_SECRET_KEY...
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))" > jwt_key.txt
type jwt_key.txt

REM 3. Adicionar JWT_SECRET_KEY no .env (se não existir)
findstr /C:"JWT_SECRET_KEY=" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo JWT_SECRET_KEY ja existe no .env
    echo Chave atual mantida
) else (
    echo. >> .env
    echo # JWT Secret Key ^(FASE 1^) >> .env
    type jwt_key.txt >> .env
    echo OK JWT_SECRET_KEY adicionado ao .env
)
del jwt_key.txt

REM 4. Build Docker
echo.
echo Fazendo build do Docker...
docker-compose build

REM 5. Subir containers
echo.
echo Subindo containers...
docker-compose up -d

REM 6. Aguardar PostgreSQL ficar pronto
echo.
echo Aguardando PostgreSQL ficar pronto...
timeout /t 10 /nobreak >nul

REM 7. Criar bancos de dados
echo.
echo Criando bancos de dados...
docker exec -it postgres psql -U postgres -c "CREATE DATABASE whatsapp_bot;"
docker exec -it postgres psql -U postgres -c "CREATE DATABASE evolution;"
echo OK Bancos criados!

REM 8. Aplicar migrations
echo.
echo Aplicando migrations ^(FASE 1^)...
docker exec -it bot alembic upgrade head
echo OK Migrations aplicadas!

REM 9. Verificar health
echo.
echo Verificando health...
timeout /t 5 /nobreak >nul
curl -s http://localhost:8000/health

echo.
echo ========================================
echo   Setup completo!
echo ========================================
echo.
echo URLs disponiveis:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo Testar login FASE 1:
echo    curl -X POST http://localhost:8000/api/v1/auth-v2/login ^
echo      -H "Content-Type: application/json" ^
echo      -d "{\"email\": \"teste@teste.com\", \"senha\": \"teste123\"}"
echo.
pause
