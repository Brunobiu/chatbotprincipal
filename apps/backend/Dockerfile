FROM python:3.13

# Definir diretório de trabalho para o backend (dentro do contexto de build apps/backend)
WORKDIR /app/apps/backend

# Instalar dependências do sistema e utilitários (inclui dos2unix)
RUN apt-get update && apt-get install -y postgresql-client dos2unix && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Garantir que o pacote backend seja encontrado pelo Python
ENV PYTHONPATH=/app/apps/backend

# Copiar código e configurações (relativos ao contexto apps/backend)
COPY app/ ./app/
COPY alembic.ini .
COPY entrypoint_fixed.sh .
# Converter possíveis CRLF para LF e garantir permissão executável
RUN dos2unix entrypoint_fixed.sh && chmod +x entrypoint_fixed.sh

EXPOSE 8000

CMD ["/bin/bash", "/app/apps/backend/entrypoint_fixed.sh"]
