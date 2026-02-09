# FASE 1 - Autenticação Forte e JWT Seguro

## 🎯 Objetivo
Implementar autenticação robusta com JWT de curta duração, refresh tokens, rate limiting no login e bloqueio de conta após tentativas falhas.

---

## 📋 Status Atual

### ✅ Já Existe
- JWT básico implementado (`app/services/auth/auth_service.py`)
- Hash de senhas com bcrypt
- Autenticação separada para clientes e admins

### ⚠️ Problemas Identificados
- JWT sem expiração curta (provavelmente longa demais)
- Sem refresh token
- Sem rate limiting no login
- Sem bloqueio após tentativas falhas
- Sem MFA/2FA
- Sem logging de tentativas de login

---

## 🔧 Implementações Necessárias

### 1.1 JWT com Expiração Curta

**Arquivo:** `apps/backend/app/services/auth/auth_service.py`

**Mudanças:**
```python
# Token de acesso: 15 minutos
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Token de refresh: 7 dias
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

**Implementar:**
- Criar função `create_access_token(data: dict, expires_delta: timedelta = None)`
- Criar função `create_refresh_token(data: dict)`
- Adicionar campo `token_type` no payload ("access" ou "refresh")
- Validar tipo de token na verificação

---

### 1.2 Sistema de Refresh Token

**Novo arquivo:** `apps/backend/app/db/models/refresh_token.py`

**Criar tabela:**
```python
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    expires_at = Column(DateTime)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    cliente = relationship("Cliente", back_populates="refresh_tokens")
```

**Nova rota:** `POST /api/v1/auth/refresh`
```python
@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    # Validar refresh token
    # Verificar se não está revogado
    # Gerar novo access token
    # Retornar novo access token
```

---

### 1.3 Rate Limiting no Login

**Novo arquivo:** `apps/backend/app/core/rate_limiter.py`

**Implementar:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Decorador para rotas
@limiter.limit("5/minute")  # 5 tentativas por minuto
async def login(...):
    ...
```

**Aplicar em:**
- `POST /api/v1/auth/login` → 5 req/min
- `POST /api/v1/admin/login` → 5 req/min
- `POST /api/v1/auth/register` → 10 req/min
- `POST /api/v1/auth/reset-password` → 3 req/hour

---

### 1.4 Bloqueio de Conta

**Novo arquivo:** `apps/backend/app/db/models/login_attempt.py`

**Criar tabela:**
```python
class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, index=True)
    ip_address = Column(String)
    success = Column(Boolean)
    attempted_at = Column(DateTime, default=datetime.utcnow)
```

**Adicionar ao modelo Cliente:**
```python
class Cliente(Base):
    # ... campos existentes ...
    
    login_attempts_failed = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
```

**Lógica de bloqueio:**
```python
# Após 5 tentativas falhas consecutivas
if cliente.login_attempts_failed >= 5:
    cliente.locked_until = datetime.utcnow() + timedelta(minutes=30)
    # Enviar email de alerta
    
# Ao fazer login com sucesso
cliente.login_attempts_failed = 0
cliente.locked_until = None
```

---

### 1.5 Logging de Segurança

**Novo arquivo:** `apps/backend/app/services/security/security_logger.py`

**Implementar:**
```python
import logging

security_logger = logging.getLogger("security")

def log_login_attempt(email: str, ip: str, success: bool, reason: str = None):
    if success:
        security_logger.info(f"✅ Login bem-sucedido: {email} | IP: {ip}")
    else:
        security_logger.warning(f"❌ Login falhou: {email} | IP: {ip} | Razão: {reason}")

def log_suspicious_activity(activity: str, ip: str, details: dict):
    security_logger.error(f"🚨 Atividade suspeita: {activity} | IP: {ip} | {details}")
```

**Logar:**
- Todas tentativas de login (sucesso e falha)
- Bloqueios de conta
- Tokens expirados/inválidos
- Tentativas de acesso não autorizado

---

### 1.6 MFA/2FA (Opcional - Fase 1B)

**Se implementar:**

**Novo modelo:**
```python
class MFASecret(Base):
    __tablename__ = "mfa_secrets"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), unique=True)
    secret = Column(String)  # Criptografado
    enabled = Column(Boolean, default=False)
    backup_codes = Column(JSON)  # Lista de códigos de backup
```

**Biblioteca:** `pyotp` para TOTP

**Fluxo:**
1. Cliente ativa MFA no dashboard
2. Sistema gera QR code
3. Cliente escaneia com Google Authenticator
4. No login, pede código 2FA após senha

---

## 🧪 Testes Necessários

### Teste 1: JWT Expira em 15 Minutos
```python
# Criar token
token = create_access_token({"sub": "1"})

# Aguardar 16 minutos (ou mockar tempo)
# Tentar usar token
# Deve retornar 401 Unauthorized
```

### Teste 2: Refresh Token Funciona
```python
# Login → recebe access_token + refresh_token
# Aguardar access_token expirar
# Chamar /auth/refresh com refresh_token
# Deve retornar novo access_token válido
```

### Teste 3: Rate Limiting Bloqueia
```python
# Fazer 6 tentativas de login em 1 minuto
# 6ª tentativa deve retornar 429 Too Many Requests
```

### Teste 4: Conta Bloqueia Após 5 Falhas
```python
# Fazer 5 logins com senha errada
# 6ª tentativa deve retornar "Conta bloqueada por 30 minutos"
# Verificar que locked_until está setado
```

### Teste 5: Login com Sucesso Reseta Contador
```python
# Fazer 3 logins com senha errada
# Fazer 1 login com senha correta
# Verificar que login_attempts_failed = 0
```

---

## 📝 Checklist de Implementação

### Backend
- [ ] Atualizar `auth_service.py` com expiração curta
- [ ] Criar modelo `RefreshToken`
- [ ] Criar rota `/auth/refresh`
- [ ] Instalar e configurar `slowapi` para rate limiting
- [ ] Aplicar rate limiting em rotas de auth
- [ ] Criar modelo `LoginAttempt`
- [ ] Adicionar campos `login_attempts_failed` e `locked_until` em Cliente
- [ ] Implementar lógica de bloqueio no login
- [ ] Criar `security_logger.py`
- [ ] Adicionar logs em todas tentativas de login
- [ ] Criar migration para novas tabelas

### Testes
- [ ] Teste de expiração de JWT
- [ ] Teste de refresh token
- [ ] Teste de rate limiting
- [ ] Teste de bloqueio de conta
- [ ] Teste de reset de contador

### Documentação
- [ ] Atualizar README com novo fluxo de auth
- [ ] Documentar endpoints de refresh
- [ ] Documentar rate limits

---

## 🚨 Pontos de Atenção

### 1. Não Quebrar Autenticação Existente
- Manter compatibilidade com tokens antigos durante migração
- Implementar período de transição se necessário

### 2. Refresh Token Seguro
- Armazenar apenas hash do refresh token no banco
- Nunca expor refresh token em logs
- Revogar refresh tokens antigos ao criar novos

### 3. Rate Limiting Distribuído
- Se usar múltiplos workers, usar Redis para compartilhar contadores
- Já temos Redis configurado, usar ele

### 4. Bloqueio de Conta
- Enviar email quando conta for bloqueada
- Permitir desbloqueio via email (link seguro)
- Admin pode desbloquear manualmente

---

## 📊 Métricas de Sucesso

Após implementação, validar:

✅ **JWT expira em exatamente 15 minutos**  
✅ **Refresh token funciona por 7 dias**  
✅ **Rate limiting bloqueia após limite**  
✅ **Conta bloqueia após 5 tentativas falhas**  
✅ **Todos logins são logados**  
✅ **Nenhum teste existente quebrou**

---

## 🔄 Próximos Passos

Após completar esta fase:
1. Validar todos os testes
2. Fazer code review
3. Testar manualmente no ambiente de dev
4. Marcar fase como concluída
5. **Aguardar aprovação antes de ir para FASE 2**

---

**Status:** 🔴 Não iniciado  
**Prioridade:** CRÍTICA  
**Tempo estimado:** 4-6 horas
