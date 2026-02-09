# FASE 1 - Testes de Autenticação Forte

## ✅ Checklist de Implementação

- [x] Migration 023 - Campos de segurança no banco
- [x] Modelo LogAutenticacao
- [x] AuthServiceV2 com JWT curto + Refresh Token
- [x] Rate Limiter em memória
- [x] Middlewares de Rate Limiting
- [x] Rotas auth_v2 com segurança aprimorada
- [ ] Aplicar migrations no banco
- [ ] Registrar rotas no main.py
- [ ] Aplicar middlewares no main.py
- [ ] Testes manuais
- [ ] Testes automatizados

## 🧪 Testes Manuais

### 1. Testar Login Bem-Sucedido

```bash
curl -X POST http://localhost:8000/api/v1/auth-v2/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "senha": "senha123"
  }'
```

**Resultado esperado:**
- Status 200
- Retorna `access_token` e `refresh_token`
- `expires_in` = 900 (15 minutos)
- Dados do cliente

### 2. Testar Login com Senha Incorreta

```bash
curl -X POST http://localhost:8000/api/v1/auth-v2/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "senha": "senha_errada"
  }'
```

**Resultado esperado:**
- Status 401
- Mensagem de erro
- Contador de tentativas incrementado no banco

### 3. Testar Bloqueio Após 5 Tentativas

Fazer 5 tentativas de login com senha incorreta:

```bash
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/auth-v2/login \
    -H "Content-Type: application/json" \
    -d '{
      "email": "teste@example.com",
      "senha": "senha_errada"
    }'
  echo "\nTentativa $i"
done
```

**Resultado esperado:**
- Primeiras 4 tentativas: Status 401
- 5ª tentativa: Status 401 + conta bloqueada
- Tentativa 6: Status 401 com mensagem "Conta bloqueada. Tente novamente em X minutos"

### 4. Testar Refresh Token

Primeiro fazer login:

```bash
# 1. Login
RESPONSE=$(curl -X POST http://localhost:8000/api/v1/auth-v2/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "senha": "senha123"
  }')

ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $RESPONSE | jq -r '.refresh_token')

# 2. Usar refresh token para obter novo access token
curl -X POST http://localhost:8000/api/v1/auth-v2/refresh \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"refresh_token\": \"$REFRESH_TOKEN\"
  }"
```

**Resultado esperado:**
- Status 200
- Novo `access_token`
- `expires_in` = 900

### 5. Testar Rate Limiting de Login

Fazer mais de 5 requisições de login em 15 minutos:

```bash
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v1/auth-v2/login \
    -H "Content-Type: application/json" \
    -d '{
      "email": "teste@example.com",
      "senha": "senha123"
    }'
  echo "\nRequisição $i"
done
```

**Resultado esperado:**
- Primeiras 5 requisições: Status 200 ou 401
- 6ª requisição: Status 429 (Too Many Requests)
- Header `Retry-After` presente

### 6. Testar Endpoint /me

```bash
# Usar access token do login
curl -X GET http://localhost:8000/api/v1/auth-v2/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Resultado esperado:**
- Status 200
- Dados do cliente (id, nome, email, telefone, status)

### 7. Testar Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth-v2/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Resultado esperado:**
- Status 200
- Mensagem "Logout realizado com sucesso"
- Refresh token invalidado no banco

### 8. Verificar Logs de Autenticação

Consultar banco de dados:

```sql
SELECT * FROM logs_autenticacao 
ORDER BY created_at DESC 
LIMIT 10;
```

**Resultado esperado:**
- Todas as tentativas de login registradas
- Campos preenchidos: email, ip, user_agent, sucesso, motivo_falha

## 🔍 Verificações no Banco de Dados

### 1. Verificar Campos de Segurança no Cliente

```sql
SELECT 
  id, 
  email, 
  tentativas_login_falhas, 
  bloqueado_ate, 
  ultimo_ip_falha,
  refresh_token_hash,
  refresh_token_expira_em
FROM clientes 
WHERE email = 'teste@example.com';
```

### 2. Verificar Logs de Autenticação

```sql
-- Tentativas de login por email
SELECT 
  email_tentativa,
  COUNT(*) as total,
  SUM(CASE WHEN sucesso THEN 1 ELSE 0 END) as sucessos,
  SUM(CASE WHEN NOT sucesso THEN 1 ELSE 0 END) as falhas
FROM logs_autenticacao
GROUP BY email_tentativa;

-- Tentativas de login por IP
SELECT 
  ip_address,
  COUNT(*) as total,
  SUM(CASE WHEN sucesso THEN 1 ELSE 0 END) as sucessos,
  SUM(CASE WHEN NOT sucesso THEN 1 ELSE 0 END) as falhas
FROM logs_autenticacao
GROUP BY ip_address;

-- Motivos de falha
SELECT 
  motivo_falha,
  COUNT(*) as total
FROM logs_autenticacao
WHERE NOT sucesso
GROUP BY motivo_falha;
```

## 🎯 Critérios de Sucesso

- [ ] Login com credenciais válidas retorna access_token e refresh_token
- [ ] Access token expira em 15 minutos
- [ ] Refresh token expira em 7 dias
- [ ] Senha incorreta incrementa contador de tentativas
- [ ] Conta é bloqueada após 5 tentativas falhas
- [ ] Bloqueio dura 15 minutos
- [ ] Rate limiting bloqueia após 5 requisições de login em 15 min
- [ ] Refresh token gera novo access token
- [ ] Logout invalida refresh token
- [ ] Todas as tentativas são registradas em logs_autenticacao
- [ ] Senhas são hasheadas com bcrypt (cost 12)
- [ ] Refresh tokens são hasheados com SHA-256

## 🚀 Próximos Passos

Após todos os testes passarem:
1. Atualizar frontend para usar novos endpoints
2. Implementar renovação automática de token no frontend
3. Avançar para FASE 2 - Isolamento de Usuários
