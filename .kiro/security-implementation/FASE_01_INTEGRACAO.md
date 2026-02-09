# FASE 1 - Guia de Integração

## 📋 Passos para Integração

### 1. Aplicar Migration no Banco de Dados

```bash
cd apps/backend

# Aplicar migration
alembic upgrade head

# Verificar se foi aplicada
alembic current
```

**Resultado esperado:**
- Migration 023 aplicada
- Tabela `logs_autenticacao` criada
- Campos de segurança adicionados em `clientes`

### 2. Registrar Rotas no main.py

Adicionar as novas rotas de autenticação V2:

```python
# Em apps/backend/app/main.py

from app.api.v1 import auth_v2

# Registrar rotas
app.include_router(
    auth_v2.router,
    prefix="/api/v1/auth-v2",
    tags=["auth-v2"]
)
```

### 3. Aplicar Middlewares no main.py

Adicionar os middlewares de rate limiting:

```python
# Em apps/backend/app/main.py

from app.core.middleware import (
    ErrorHandlerMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    LoginRateLimitMiddleware
)

# Adicionar middlewares (ordem importa!)
app.add_middleware(LoginRateLimitMiddleware, max_attempts=5, window_seconds=900)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
```

**Ordem dos middlewares:**
1. LoginRateLimitMiddleware (mais específico)
2. RateLimitMiddleware (geral)
3. ErrorHandlerMiddleware
4. LoggingMiddleware

### 4. Atualizar .env com Configurações de Segurança

Adicionar/verificar no `.env`:

```env
# JWT Secret (IMPORTANTE: Mudar em produção!)
JWT_SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
LOGIN_RATE_LIMIT_PER_15MIN=5
```

**⚠️ CRÍTICO:** Gerar uma chave secreta forte para produção:

```bash
# Gerar chave aleatória segura
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Testar Localmente

```bash
# Iniciar backend
cd apps/backend
uvicorn app.main:app --reload --port 8000

# Em outro terminal, testar endpoints
curl -X POST http://localhost:8000/api/v1/auth-v2/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu_email@example.com",
    "senha": "sua_senha"
  }'
```

### 6. Atualizar Frontend (Opcional - Manter Compatibilidade)

Por enquanto, manter as rotas antigas funcionando. Depois migrar gradualmente:

**Opção A: Migração Gradual (Recomendado)**
- Manter `/api/v1/auth/login` funcionando
- Adicionar `/api/v1/auth-v2/login` com novos recursos
- Migrar frontend aos poucos

**Opção B: Migração Completa**
- Substituir todas as chamadas de `/api/v1/auth/*` por `/api/v1/auth-v2/*`
- Atualizar lógica de refresh token no frontend
- Adicionar renovação automática de token

## 🔧 Configurações Recomendadas

### Desenvolvimento

```env
JWT_SECRET_KEY=dev-secret-key-not-for-production
RATE_LIMIT_PER_MINUTE=1000  # Mais permissivo
LOGIN_RATE_LIMIT_PER_15MIN=50  # Mais permissivo
```

### Produção

```env
JWT_SECRET_KEY=<chave-gerada-aleatoriamente-32-chars>
RATE_LIMIT_PER_MINUTE=100
LOGIN_RATE_LIMIT_PER_15MIN=5
```

## 📊 Monitoramento

### Queries Úteis para Monitorar Segurança

```sql
-- Tentativas de login falhadas nas últimas 24h
SELECT 
  email_tentativa,
  COUNT(*) as tentativas,
  MAX(created_at) as ultima_tentativa
FROM logs_autenticacao
WHERE NOT sucesso 
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY email_tentativa
ORDER BY tentativas DESC
LIMIT 20;

-- IPs com mais tentativas falhadas
SELECT 
  ip_address,
  COUNT(*) as tentativas,
  COUNT(DISTINCT email_tentativa) as emails_diferentes
FROM logs_autenticacao
WHERE NOT sucesso 
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY ip_address
HAVING COUNT(*) > 10
ORDER BY tentativas DESC;

-- Contas bloqueadas atualmente
SELECT 
  id,
  email,
  tentativas_login_falhas,
  bloqueado_ate,
  ultimo_ip_falha
FROM clientes
WHERE bloqueado_ate > NOW()
ORDER BY bloqueado_ate DESC;
```

## 🚨 Troubleshooting

### Problema: Migration não aplica

```bash
# Verificar status
alembic current

# Ver histórico
alembic history

# Forçar upgrade
alembic upgrade head --sql  # Ver SQL que será executado
alembic upgrade head  # Aplicar
```

### Problema: Rate limiting muito restritivo

Ajustar valores no `main.py`:

```python
# Aumentar limites temporariamente
app.add_middleware(RateLimitMiddleware, max_requests=500, window_seconds=60)
app.add_middleware(LoginRateLimitMiddleware, max_attempts=10, window_seconds=900)
```

### Problema: Token expira muito rápido

Ajustar em `auth_service_v2.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Aumentar para 30 min
```

### Problema: Conta bloqueada não desbloqueia

Verificar no banco:

```sql
-- Ver contas bloqueadas
SELECT id, email, bloqueado_ate FROM clientes WHERE bloqueado_ate IS NOT NULL;

-- Desbloquear manualmente (emergência)
UPDATE clientes 
SET bloqueado_ate = NULL, tentativas_login_falhas = 0 
WHERE email = 'email@example.com';
```

## ✅ Checklist de Integração

- [ ] Migration 023 aplicada com sucesso
- [ ] Tabela `logs_autenticacao` existe no banco
- [ ] Campos de segurança existem em `clientes`
- [ ] Rotas `/api/v1/auth-v2/*` registradas
- [ ] Middlewares de rate limiting aplicados
- [ ] JWT_SECRET_KEY configurado no .env
- [ ] Testes manuais passando
- [ ] Logs de autenticação sendo gravados
- [ ] Rate limiting funcionando
- [ ] Bloqueio de conta funcionando
- [ ] Refresh token funcionando

## 🎯 Próximos Passos

Após integração completa:
1. Monitorar logs por 24-48h
2. Ajustar rate limits se necessário
3. Documentar para o time
4. Avançar para FASE 2 - Isolamento de Usuários
