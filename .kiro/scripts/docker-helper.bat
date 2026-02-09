@echo off
REM Script helper para gerenciar Docker no Windows

if "%1"=="" goto help
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="logs" goto logs
if "%1"=="restart" goto restart
if "%1"=="clean" goto clean
goto help

:build
echo === Construindo imagens Docker ===
docker-compose build
goto end

:up
echo === Subindo todos os servicos ===
docker-compose up -d
echo.
echo === Servicos rodando ===
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo Evolution API: http://localhost:8080
echo ChromaDB: http://localhost:8001
echo.
echo Para ver logs: docker-helper.bat logs
goto end

:down
echo === Parando todos os servicos ===
docker-compose down
goto end

:logs
if "%2"=="" (
    echo === Mostrando logs de todos os servicos ===
    docker-compose logs -f
) else (
    echo === Mostrando logs do servico %2 ===
    docker-compose logs -f %2
)
goto end

:restart
echo === Reiniciando servicos ===
docker-compose restart
goto end

:clean
echo === ATENCAO: Isso vai remover TODOS os containers, volumes e imagens ===
set /p confirm="Tem certeza? (s/n): "
if /i "%confirm%"=="s" (
    docker-compose down -v
    docker system prune -a -f
    echo === Limpeza completa realizada ===
) else (
    echo === Operacao cancelada ===
)
goto end

:help
echo.
echo === Docker Helper - Comandos Disponiveis ===
echo.
echo docker-helper.bat build       - Constroi as imagens Docker
echo docker-helper.bat up          - Sobe todos os servicos
echo docker-helper.bat down        - Para todos os servicos
echo docker-helper.bat logs        - Mostra logs de todos os servicos
echo docker-helper.bat logs [nome] - Mostra logs de um servico especifico
echo docker-helper.bat restart     - Reinicia todos os servicos
echo docker-helper.bat clean       - Remove tudo (containers, volumes, imagens)
echo.
echo Exemplos:
echo   docker-helper.bat up
echo   docker-helper.bat logs frontend
echo   docker-helper.bat logs bot
echo.
goto end

:end
