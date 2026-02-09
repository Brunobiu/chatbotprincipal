# 🚀 FASE 1 - APLICAR AGORA

## ✅ Código Integrado no main.py

O código da FASE 1 foi **100% integrado** no `main.py`:

- ✅ Middlewares de Rate Limiting aplicados
- ✅ Rotas `/api/v1/auth-v2/*` registradas
- ✅ Logs de segurança ativados
- ✅ Health check atualizado

## 📋 Próximo Passo: Aplicar Migration

### Opção 1: Via Docker (Recomendado se usar Docker)

```bash
# Entrar no container do backend
docker exec -it <nome-container-backend> bash

# Aplicar migration
alembic upgrade head

# Sair
exit
```

### Opção 2: Via Python Local

```bash
cd apps/backend

# Ativar ambiente virtual (se usar)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Aplicar migration
alembic upgrade head
```

### Opção 3: Via Python Direto

```bash
cd apps/backend
python -m alembic upgrade head
```

### Opção 4: SQL Manual (Se nada funcionar)

Execute este SQL diretamente no PostgreSQL:

```sql
-- Migration 023: Adicionar campos de segurança

-- 1. Adicionar campos na tabela clientes
ALTER TABLE clientes 
ADD COLUMN tentativas_login_falhas INTEGER NOT NULL DEFAULT 0,
ADD COLUMN bloqueado_ate TIMESTAMP,
ADD COLUMN ultimo_ip_falha VARCHAR(45),
ADD COLUMN refresh_token_hash VARCHAR(255),
ADD COLUMN refresh_token_expira_em TIMESTAMP;

-- 2. Criar índice
CREATE INDEX ix_clientes_bloqueado_ate ON clientes(bloqueado_ate);

-- 3. Criar tabela de logs de autenticação
CREATE TABLE logs_autenticacao (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER,
    email_tentativa VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent VARCHAR(500),
    sucesso BOOLEAN NOT NULL,
    motivo_falha VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 4. Criar índices
CREATE INDEX ix_logs_autenticacao_cliente_id ON logs_autenticacao(cliente_id);
CREATE INDEX ix_logs_autenticacao_email_tentativa ON logs_autenticacao(email_tentativa);
CREATE INDEX ix_logs_autenticacao_ip_address ON logs_autenticacao(ip_address);
CREATE INDEX ix_logs_autenticacao_created_at ON logs_autenticacao(created_at);
CREATE INDEX ix_logs_autenticacao_sucesso ON logs_autenticacao(sucesso);

-- 5. Atualizar versão do alembic (se usar alembic)
INSERT INTO alembic_version (version_num) VALUES ('023');
```

## 🔐 Configurar JWT_SECRET_KEY

Adicione no arquivo `.env`:

```bash
# Gerar chave segura (execute no terminal):
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copie a chave gerada e adicione no .env:
JWT_SECRET_KEY=<cole-a-chave-aqui>
```

Ou use esta chave temporária (MUDAR EM PRODUÇÃO):

```env
JWT_SECRET_KEY=dev-secret-key-for-testing-change-in-production-min-32-chars
```

## 🧪 Testar

### 1. Iniciar servidor

```bash
cd apps/backend
uvicorn app.main:app --reload --port 8000
```

### 2. Verificar health check

```bash
curl http://localhost:8000/health
```

**Resultado esperado:**
```json
{
  "status": "ok",
  "service": "whatsapp-ai-bot",
  "security": {
    "fase_1": "active",
    "rate_limiting": "enabled",
    "jwt_v2": "enabled",
    "login_protection": "enabled"
  }
}
```

### 3. Testar login V2

```bash
curl -X POST http://localhost:8000/api/v1/auth-v2/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu_email@example.com",
    "senha": "sua_senha"
  }'
```

**Resultado esperado:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "abc123...",
  "token_type": "bearer",
  "expires_in": 900,
  "cliente": {
    "id": 1,
    "nome": "Nome",
    "email": "email@example.com",
    "status": "ativo"
  }
}
```

### 4. Testar rate limiting

Faça 6 requisições rápidas de login:

```bash
for i in {1..6}; do
  echo "Tentativa $i:"
  curl -X POST http://localhost:8000/api/v1/auth-v2/login \
    -H "Content-Type: application/json" \
    -d '{"email": "teste@example.com", "senha": "senha_errada"}'
  echo "\n---"
done
```

**Resultado esperado:**
- Primeiras 5: Status 401 (senha incorreta)
- 6ª requisição: Status 429 (Too Many Requests)

## ✅ Checklist Final

- [ ] Migration 023 aplicada
- [ ] Tabela `logs_autenticacao` existe
- [ ] Campos de segurança em `clientes` existem
- [ ] JWT_SECRET_KEY configurado no .env
- [ ] Servidor inicia sem erros
- [ ] Health check retorna `fase_1: active`
- [ ] Login V2 funciona
- [ ] Rate limiting funciona
- [ ] Logs de autenticação sendo gravados

## 🎯 Verificar no Banco

```sql
-- Ver estrutura da tabela clientes
\d clientes

-- Ver estrutura da tabela logs_autenticacao
\d logs_autenticacao

-- Ver logs de autenticação
SELECT * FROM logs_autenticacao ORDER BY created_at DESC LIMIT 10;
```

## 🚨 Problemas Comuns

### Migration não aplica

```bash
# Ver status atual
alembic current

# Ver histórico
alembic history

# Forçar para versão específica
alembic upgrade 023
```

### Erro de conexão com banco

Verifique o `.env`:
```env
DATABASE_URL=postgresql://usuario:senha@host:porta/banco
```

### Servidor não inicia

Verifique se todas as dependências estão instaladas:
```bash
pip install -r requirements.txt
```

## 📚 Documentação Completa

- [Testes Completos](./FASE_01_TESTES.md)
- [Comandos Rápidos](./FASE_01_COMANDOS_RAPIDOS.md)
- [Checklist](./FASE_01_CHECKLIST.md)

---

**Status:** ✅ Código integrado - Aguardando aplicação da migration  
**Próximo:** Aplicar migration e testar
