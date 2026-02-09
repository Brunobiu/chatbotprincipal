# ✅ Configuração Docker Verificada

## 🔍 ANÁLISE COMPLETA

Verifiquei todo o `docker-compose.yml` e `.env.example`. Aqui está o status:

---

## 🌐 PORTAS CONFIGURADAS

### ✅ Corretas (Batem com seus links)

| Serviço | Porta | URL | Status |
|---------|-------|-----|--------|
| **Frontend** | 3000 | http://localhost:3000 | ✅ OK |
| **Backend** | 8000 | http://localhost:8000 | ✅ OK |
| **Evolution API** | 8080 | http://localhost:8080 | ✅ OK |
| **PostgreSQL** | 5432 | localhost:5432 | ✅ OK |
| **Redis** | 6379 | localhost:6379 | ✅ OK |
| **ChromaDB** | 8001 | http://localhost:8001 | ✅ OK |

**Todas as portas estão corretas!** 🎉

---

## 🔑 CREDENCIAIS DO BANCO

### PostgreSQL (docker-compose.yml)

```yaml
POSTGRES_PASSWORD=postgres
```

### Strings de Conexão (.env.example)

```env
# Bot/Backend
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/whatsapp_bot

# Evolution API
DATABASE_CONNECTION_URI=postgresql://postgres:postgres@postgres:5432/evolution?schema=public
```

**Análise:**
- ✅ Usuário: `postgres`
- ✅ Senha: `postgres`
- ✅ Host: `postgres` (nome do container)
- ✅ Porta: `5432`
- ✅ Banco Bot: `whatsapp_bot`
- ✅ Banco Evolution: `evolution`

**Status:** ✅ Tudo correto!

---

## 🔐 CREDENCIAIS DE TESTE

### Cliente Teste (Você informou)
```
Email: teste@teste.com
Senha: teste123
```

### Admin (Você informou)
```
Email: brunobiuu
Senha: santana7996@
```

### Evolution API
```
API Key: sua_chave_aqui (precisa configurar no .env)
```

---

## ⚠️ O QUE PRECISA CONFIGURAR NO .env

### 1. JWT_SECRET_KEY (FASE 1 - OBRIGATÓRIO)

**Adicionar no `.env`:**

```bash
# Gerar chave segura:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Adicionar no .env:
JWT_SECRET_KEY=<cole-a-chave-gerada-aqui>
```

**Exemplo:**
```env
JWT_SECRET_KEY=xK9mP2nQ5rT8wY1zA4bC7dE0fG3hJ6kL9mN2pQ5sT8vW
```

### 2. OpenAI API Key

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### 3. Evolution API Key

```env
AUTHENTICATION_API_KEY=sua_chave_evolution_aqui
```

### 4. Stripe Keys (se usar pagamentos)

```env
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
STRIPE_PRICE_LOOKUP_KEY=price_xxxxxxxxxxxxx
```

---

## 📋 CHECKLIST DE CONFIGURAÇÃO

### Antes de Subir o Docker

- [ ] Copiar `.env.example` para `.env`
- [ ] Configurar `OPENAI_API_KEY`
- [ ] Configurar `AUTHENTICATION_API_KEY` (Evolution)
- [ ] Configurar `JWT_SECRET_KEY` (FASE 1)
- [ ] Configurar `STRIPE_SECRET_KEY` (se usar)
- [ ] Verificar `DATABASE_URL` (já está correto)

### Comandos

```bash
# 1. Copiar .env
cp .env.example .env

# 2. Editar .env e adicionar as chaves
# (use seu editor favorito)

# 3. Gerar JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 4. Adicionar no .env:
# JWT_SECRET_KEY=<chave-gerada>
```

---

## 🚀 SUBIR O DOCKER

### 1. Build e Start

```bash
# Build das imagens
docker-compose build

# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 2. Verificar se Subiu

```bash
# Ver containers rodando
docker ps

# Deve mostrar:
# - evolution_api
# - postgres
# - redis
# - chromadb
# - bot
# - frontend
```

### 3. Aplicar Migrations (FASE 1)

```bash
# Entrar no container do backend
docker exec -it bot bash

# Aplicar migrations
alembic upgrade head

# Sair
exit
```

### 4. Criar Bancos de Dados

```bash
# Entrar no PostgreSQL
docker exec -it postgres psql -U postgres

# Criar bancos
CREATE DATABASE whatsapp_bot;
CREATE DATABASE evolution;

# Sair
\q
```

---

## 🧪 TESTAR TUDO

### 1. Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Deve retornar:
# {
#   "status": "ok",
#   "security": {
#     "fase_1": "active",
#     ...
#   }
# }

# Backend + DB
curl http://localhost:8000/health/db

# Evolution API
curl http://localhost:8080/manager

# ChromaDB
curl http://localhost:8001/api/v1/heartbeat
```

### 2. Frontend

Abrir no navegador:
- http://localhost:3000 (Landing)
- http://localhost:3000/login (Login)
- http://localhost:3000/dashboard (Dashboard)

### 3. Backend API Docs

- http://localhost:8000/docs (Swagger)
- http://localhost:8000/redoc (Redoc)

### 4. Testar Login FASE 1

```bash
curl -X POST http://localhost:8000/api/v1/auth-v2/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@teste.com",
    "senha": "teste123"
  }'
```

---

## 🔍 VERIFICAR LOGS

```bash
# Todos os serviços
docker-compose logs -f

# Apenas backend
docker-compose logs -f bot

# Apenas frontend
docker-compose logs -f frontend

# Apenas Evolution API
docker-compose logs -f evolution-api

# Apenas PostgreSQL
docker-compose logs -f postgres
```

---

## 🐛 TROUBLESHOOTING

### Container não sobe

```bash
# Ver erro específico
docker-compose logs <nome-container>

# Exemplo:
docker-compose logs bot
```

### Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Entrar no PostgreSQL
docker exec -it postgres psql -U postgres

# Listar bancos
\l

# Verificar se whatsapp_bot existe
# Se não, criar:
CREATE DATABASE whatsapp_bot;
```

### Erro de migration

```bash
# Entrar no container
docker exec -it bot bash

# Ver status
alembic current

# Ver histórico
alembic history

# Aplicar migration específica
alembic upgrade 023

# Ou todas
alembic upgrade head
```

### Porta já em uso

```bash
# Ver o que está usando a porta
# Windows:
netstat -ano | findstr :8000

# Matar processo (substitua PID)
taskkill /PID <numero> /F

# Ou mudar porta no docker-compose.yml:
ports:
  - "8001:8000"  # Usar 8001 ao invés de 8000
```

---

## ✅ RESUMO

**Configuração Docker:** ✅ Perfeita!
- Todas as portas corretas
- Credenciais do banco corretas
- Estrutura de volumes OK

**O que falta:**
1. Configurar `.env` com as chaves
2. Gerar `JWT_SECRET_KEY` (FASE 1)
3. Subir o Docker
4. Aplicar migrations
5. Testar

**Próximo passo:** Configure o `.env` e suba o Docker!

---

**Dúvidas?** Me chame que eu ajudo! 🚀
