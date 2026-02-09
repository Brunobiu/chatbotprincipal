# FASE 1 - Comandos Rápidos

## 🚀 Setup Inicial

### 1. Aplicar Migration
```bash
cd apps/backend
alembic upgrade head
```

### 2. Gerar JWT Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Adicionar ao .env
```bash
echo "JWT_SECRET_KEY=<cole-a-chave-gerada-aqui>" >> .env
```

## 🧪 Testes Rápidos

### Login Bem-Sucedido
```bash
curl -X POST http://localhost:8000/api/v1/auth-v2/login \
  -H "Content-Type: application/json" \
  -d '{"email": "seu_email@example.com", "senha": "sua_senha"}'
```

### Testar Rate Limiting (5 tentativas)
```bash
for i in {1..6}; do
  echo "Tentativa $i:"
  curl -X POST http://localhost:8000/api/v1/auth-v2/login \
    -H "Content-Type: application/json" \
    -d '{"email": "teste@example.com", "senha": "senha_errada"}'
  echo "\n---"
done
```

### Refresh Token
```bash
# 1. Fazer login e salvar tokens
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth-v2/login \
  -H "Content-Type: application/json" \
  -d '{"email": "seu_email@example.com", "senha": "sua_senha"}')

# 2. Extrair tokens (requer jq)
ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $RESPONSE | jq -r '.refresh_token')

# 3. Usar refresh token
curl -X POST http://localhost:8000/api/v1/auth-v2/refresh \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

### Endpoint /me
```bash
curl -X GET http://localhost:8000/api/v1/auth-v2/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Logout
```bash
curl -X POST http://localhost:8000/api/v1/auth-v2/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## 🔍 Queries SQL Úteis

### Ver Logs de Autenticação
```sql
-- Últimas 10 tentativas
SELECT * FROM logs_autenticacao 
ORDER BY created_at DESC 
LIMIT 10;

-- Tentativas falhas por email
SELECT 
  email_tentativa,
  COUNT(*) as tentativas,
  MAX(created_at) as ultima_tentativa
FROM logs_autenticacao
WHERE NOT sucesso
GROUP BY email_tentativa
ORDER BY tentativas DESC;

-- IPs suspeitos (muitas falhas)
SELECT 
  ip_address,
  COUNT(*) as tentativas,
  COUNT(DISTINCT email_tentativa) as emails_diferentes
FROM logs_autenticacao
WHERE NOT sucesso 
  AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY ip_address
HAVING COUNT(*) > 5
ORDER BY tentativas DESC;
```

### Ver Contas Bloqueadas
```sql
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

-- Desbloquear conta manualmente (emergência)
UPDATE clientes 
SET bloqueado_ate = NULL, tentativas_login_falhas = 0 
WHERE email = 'email@example.com';
```

### Verificar Refresh Tokens Ativos
```sql
SELECT 
  id,
  email,
  refresh_token_expira_em,
  ultimo_login
FROM clientes
WHERE refresh_token_hash IS NOT NULL
  AND refresh_token_expira_em > NOW()
ORDER BY refresh_token_expira_em DESC;
```

## 🐛 Troubleshooting

### Migration não aplica
```bash
# Ver status
alembic current

# Ver histórico
alembic history

# Ver SQL que será executado
alembic upgrade head --sql

# Forçar upgrade
alembic upgrade head
```

### Resetar Rate Limiting (desenvolvimento)
```bash
# Reiniciar servidor (rate limiter está em memória)
# Ctrl+C e rodar novamente:
uvicorn app.main:app --reload
```

### Verificar se rotas estão registradas
```bash
curl http://localhost:8000/docs
# Abrir no navegador e procurar por "auth-v2"
```

### Verificar headers de rate limiting
```bash
curl -v http://localhost:8000/api/v1/auth-v2/login \
  -H "Content-Type: application/json" \
  -d '{"email": "teste@example.com", "senha": "senha123"}' \
  2>&1 | grep -i "x-ratelimit"
```

## 📊 Monitoramento

### Contar tentativas de login (últimas 24h)
```sql
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN sucesso THEN 1 ELSE 0 END) as sucessos,
  SUM(CASE WHEN NOT sucesso THEN 1 ELSE 0 END) as falhas,
  ROUND(100.0 * SUM(CASE WHEN sucesso THEN 1 ELSE 0 END) / COUNT(*), 2) as taxa_sucesso
FROM logs_autenticacao
WHERE created_at > NOW() - INTERVAL '24 hours';
```

### Top 10 IPs com mais requisições
```sql
SELECT 
  ip_address,
  COUNT(*) as requisicoes,
  SUM(CASE WHEN sucesso THEN 1 ELSE 0 END) as sucessos,
  SUM(CASE WHEN NOT sucesso THEN 1 ELSE 0 END) as falhas
FROM logs_autenticacao
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY ip_address
ORDER BY requisicoes DESC
LIMIT 10;
```

### Motivos de falha mais comuns
```sql
SELECT 
  motivo_falha,
  COUNT(*) as ocorrencias
FROM logs_autenticacao
WHERE NOT sucesso
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY motivo_falha
ORDER BY ocorrencias DESC;
```

## 🔧 Configurações Úteis

### Ajustar Rate Limits (main.py)
```python
# Mais permissivo (desenvolvimento)
app.add_middleware(RateLimitMiddleware, max_requests=1000, window_seconds=60)
app.add_middleware(LoginRateLimitMiddleware, max_attempts=50, window_seconds=900)

# Mais restritivo (produção alta segurança)
app.add_middleware(RateLimitMiddleware, max_requests=50, window_seconds=60)
app.add_middleware(LoginRateLimitMiddleware, max_attempts=3, window_seconds=900)
```

### Ajustar Tempo de Expiração (auth_service_v2.py)
```python
# Tokens mais longos (menos seguro, mais conveniente)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Tokens mais curtos (mais seguro, menos conveniente)
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_DAYS = 1
```

## ✅ Checklist Rápido

```bash
# 1. Migration aplicada?
alembic current | grep "023"

# 2. JWT_SECRET_KEY configurado?
grep JWT_SECRET_KEY .env

# 3. Servidor rodando?
curl http://localhost:8000/health

# 4. Rotas auth-v2 disponíveis?
curl http://localhost:8000/docs | grep "auth-v2"

# 5. Rate limiting funcionando?
# (fazer 6 requisições rápidas e verificar 429)

# 6. Logs sendo gravados?
psql -d seu_banco -c "SELECT COUNT(*) FROM logs_autenticacao;"
```

## 🎯 Próximo Passo

Após validar tudo:
```bash
# Marcar FASE 1 como concluída
echo "✅ FASE 1 concluída em $(date)" >> .kiro/security-implementation/PROGRESSO.txt

# Ler FASE 2
cat .kiro/security-implementation/FASE_02_ISOLAMENTO_USUARIOS.md
```
