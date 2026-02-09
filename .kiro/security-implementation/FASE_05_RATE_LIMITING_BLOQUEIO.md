# FASE 5 - Rate Limiting e Bloqueio Inteligente

## 🎯 Objetivo
Implementar rate limiting por IP e usuário, sistema de bloqueio progressivo e detecção de comportamento anômalo.

---

## 📋 Implementações

### 5.1 Rate Limiting com Redis

**Instalar:**
```bash
pip install slowapi redis
```

**Arquivo:** `apps/backend/app/core/rate_limiter.py`

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
import redis
from app.core.config import settings

# Conexão Redis
redis_client = redis.from_url(settings.REDIS_URL)

# Limiter com Redis backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=["100/minute"]  # Limite global padrão
)

# Rate limiter por usuário autenticado
def get_user_id(request: Request) -> str:
    """Extrai user_id do token JWT"""
    try:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return get_remote_address(request)
        
        token = auth_header.replace("Bearer ", "")
        # Decodificar JWT e pegar user_id
        from app.services.auth.auth_service import AuthService
        payload = AuthService.validar_token(token)
        
        if payload:
            return f"user:{payload.get('sub')}"
        
        return get_remote_address(request)
    except:
        return get_remote_address(request)

limiter_by_user = Limiter(
    key_func=get_user_id,
    storage_uri=settings.REDIS_URL
)
```

**Aplicar no app:**
```python
# apps/backend/app/main.py
from app.core.rate_limiter import limiter, RateLimitExceeded, _rate_limit_exceeded_handler

app = FastAPI()

# Adicionar limiter ao app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

**Aplicar em rotas:**
```python
from app.core.rate_limiter import limiter, limiter_by_user

# Por IP
@router.post("/auth/login")
@limiter.limit("5/minute")  # 5 tentativas por minuto por IP
async def login(request: Request, ...):
    ...

# Por usuário autenticado
@router.post("/conversas")
@limiter_by_user.limit("50/minute")  # 50 criações por minuto por usuário
async def create_conversa(request: Request, ...):
    ...

# Múltiplos limites
@router.post("/conhecimento/upload")
@limiter_by_user.limit("5/hour")  # 5 uploads por hora
@limiter.limit("20/hour")  # 20 uploads por hora por IP
async def upload(request: Request, ...):
    ...
```

---

### 5.2 Sistema de Bloqueio de IP

**Novo arquivo:** `apps/backend/app/db/models/blocked_ip.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from app.db.base import Base
from datetime import datetime

class BlockedIP(Base):
    __tablename__ = "blocked_ips"
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(String(45), unique=True, index=True)  # IPv6 suporta até 45 chars
    reason = Column(String(500))
    blocked_at = Column(DateTime, default=datetime.utcnow)
    blocked_until = Column(DateTime, nullable=True)  # None = permanente
    is_permanent = Column(Boolean, default=False)
    attempts_count = Column(Integer, default=1)
    last_attempt = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)  # JSON com detalhes
```

**Novo arquivo:** `apps/backend/app/services/security/ip_blocker.py`

```python
from sqlalchemy.orm import Session
from app.db.models.blocked_ip import BlockedIP
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("security")

class IPBlocker:
    """Gerencia bloqueio de IPs"""
    
    @staticmethod
    def is_blocked(db: Session, ip: str) -> tuple[bool, str]:
        """
        Verifica se IP está bloqueado
        
        Returns:
            (is_blocked, reason)
        """
        blocked = db.query(BlockedIP).filter(
            BlockedIP.ip_address == ip
        ).first()
        
        if not blocked:
            return False, ""
        
        # Bloqueio permanente
        if blocked.is_permanent:
            return True, blocked.reason
        
        # Bloqueio temporário expirado
        if blocked.blocked_until and datetime.utcnow() > blocked.blocked_until:
            db.delete(blocked)
            db.commit()
            return False, ""
        
        return True, blocked.reason
    
    @staticmethod
    def block_ip(
        db: Session,
        ip: str,
        reason: str,
        duration_minutes: int = None,
        details: dict = None
    ):
        """
        Bloqueia IP
        
        Args:
            duration_minutes: None = permanente
        """
        blocked = db.query(BlockedIP).filter(
            BlockedIP.ip_address == ip
        ).first()
        
        if blocked:
            # Já bloqueado, incrementar contador
            blocked.attempts_count += 1
            blocked.last_attempt = datetime.utcnow()
            
            # Se já tem muitas tentativas, tornar permanente
            if blocked.attempts_count >= 10:
                blocked.is_permanent = True
                blocked.blocked_until = None
                logger.error(f"🚨 IP {ip} bloqueado PERMANENTEMENTE após {blocked.attempts_count} tentativas")
        else:
            # Novo bloqueio
            blocked_until = None
            is_permanent = False
            
            if duration_minutes:
                blocked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
            else:
                is_permanent = True
            
            blocked = BlockedIP(
                ip_address=ip,
                reason=reason,
                blocked_until=blocked_until,
                is_permanent=is_permanent,
                details=str(details) if details else None
            )
            db.add(blocked)
            
            logger.warning(
                f"🔒 IP {ip} bloqueado por {duration_minutes or 'PERMANENTE'} minutos. "
                f"Razão: {reason}"
            )
        
        db.commit()
    
    @staticmethod
    def unblock_ip(db: Session, ip: str):
        """Remove bloqueio de IP"""
        blocked = db.query(BlockedIP).filter(
            BlockedIP.ip_address == ip
        ).first()
        
        if blocked:
            db.delete(blocked)
            db.commit()
            logger.info(f"✅ IP {ip} desbloqueado")
```

**Middleware de bloqueio:**
```python
# apps/backend/app/core/middleware.py

from app.services.security.ip_blocker import IPBlocker

class IPBlockMiddleware(BaseHTTPMiddleware):
    """Bloqueia IPs na lista negra"""
    
    async def dispatch(self, request: Request, call_next):
        # Pegar IP real (considerar proxy)
        ip = request.client.host
        
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        
        # Verificar se está bloqueado
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        try:
            is_blocked, reason = IPBlocker.is_blocked(db, ip)
            
            if is_blocked:
                logger.warning(f"🚫 Tentativa de acesso de IP bloqueado: {ip}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "status": "error",
                        "message": "Acesso negado",
                        "detail": "Seu IP foi bloqueado devido a atividade suspeita"
                    }
                )
        finally:
            db.close()
        
        response = await call_next(request)
        return response
```

---

### 5.3 Detecção de Comportamento Anômalo

**Novo arquivo:** `apps/backend/app/services/security/anomaly_detector.py`

```python
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL)

class AnomalyDetector:
    """Detecta comportamento suspeito"""
    
    @staticmethod
    def track_request(ip: str, endpoint: str):
        """Rastreia requisições por IP"""
        key = f"requests:{ip}"
        
        # Adicionar timestamp
        redis_client.lpush(key, f"{endpoint}:{datetime.utcnow().timestamp()}")
        
        # Manter apenas últimos 100 requests
        redis_client.ltrim(key, 0, 99)
        
        # Expirar em 1 hora
        redis_client.expire(key, 3600)
    
    @staticmethod
    def is_suspicious(ip: str) -> tuple[bool, str]:
        """
        Detecta padrões suspeitos
        
        Returns:
            (is_suspicious, reason)
        """
        key = f"requests:{ip}"
        requests = redis_client.lrange(key, 0, -1)
        
        if not requests:
            return False, ""
        
        # Converter para lista de (endpoint, timestamp)
        parsed = []
        for req in requests:
            req_str = req.decode('utf-8')
            endpoint, timestamp = req_str.split(":")
            parsed.append((endpoint, float(timestamp)))
        
        # Regra 1: Mais de 50 requests em 1 minuto
        one_min_ago = datetime.utcnow().timestamp() - 60
        recent = [r for r in parsed if r[1] > one_min_ago]
        
        if len(recent) > 50:
            return True, "Muitas requisições em curto período"
        
        # Regra 2: Tentando acessar muitos endpoints diferentes (scanning)
        unique_endpoints = set([r[0] for r in parsed])
        if len(unique_endpoints) > 20:
            return True, "Scanning de endpoints"
        
        # Regra 3: Muitas requisições 404 (path traversal)
        # (precisa ser implementado com tracking de status codes)
        
        return False, ""
    
    @staticmethod
    def check_and_block(db: Session, ip: str):
        """Verifica anomalia e bloqueia se necessário"""
        is_suspicious, reason = AnomalyDetector.is_suspicious(ip)
        
        if is_suspicious:
            from app.services.security.ip_blocker import IPBlocker
            
            # Bloqueio progressivo
            # 1ª vez: 15 minutos
            # 2ª vez: 1 hora
            # 3ª+ vez: permanente
            
            IPBlocker.block_ip(
                db=db,
                ip=ip,
                reason=reason,
                duration_minutes=15,
                details={"detected_by": "anomaly_detector"}
            )
```

**Aplicar em middleware:**
```python
class AnomalyDetectionMiddleware(BaseHTTPMiddleware):
    """Detecta e bloqueia comportamento anômalo"""
    
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        endpoint = request.url.path
        
        # Rastrear requisição
        AnomalyDetector.track_request(ip, endpoint)
        
        # Verificar se é suspeito
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        try:
            AnomalyDetector.check_and_block(db, ip)
        finally:
            db.close()
        
        response = await call_next(request)
        return response
```

---

### 5.4 CAPTCHA em Ações Sensíveis

**Instalar:**
```bash
pip install python-recaptcha
```

**Arquivo:** `apps/backend/app/core/captcha.py`

```python
from recaptcha import verify_recaptcha
from fastapi import HTTPException, status
from app.core.config import settings

class CaptchaVerifier:
    """Verifica Google reCAPTCHA"""
    
    @staticmethod
    async def verify(token: str, ip: str) -> bool:
        """Verifica token do reCAPTCHA"""
        try:
            result = await verify_recaptcha(
                secret=settings.RECAPTCHA_SECRET_KEY,
                response=token,
                remoteip=ip
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Erro ao verificar CAPTCHA: {e}")
            return False

# Dependency para rotas
async def require_captcha(
    request: Request,
    captcha_token: str = None
):
    """Requer CAPTCHA válido"""
    if not captcha_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token CAPTCHA não fornecido"
        )
    
    ip = request.client.host
    is_valid = await CaptchaVerifier.verify(captcha_token, ip)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CAPTCHA inválido"
        )
```

**Aplicar em rotas:**
```python
from app.core.captcha import require_captcha

@router.post("/auth/register", dependencies=[Depends(require_captcha)])
async def register(...):
    ...

@router.post("/auth/reset-password", dependencies=[Depends(require_captcha)])
async def reset_password(...):
    ...
```

---

## 🧪 Testes

### Teste 1: Rate Limiting
```python
def test_rate_limiting():
    # Fazer 6 requisições rápidas
    for i in range(6):
        response = client.post("/api/v1/auth/login", json={
            "email": "test@test.com",
            "senha": "wrong"
        })
    
    # 6ª deve retornar 429
    assert response.status_code == 429
```

### Teste 2: Bloqueio de IP
```python
def test_ip_blocking():
    from app.services.security.ip_blocker import IPBlocker
    
    # Bloquear IP
    IPBlocker.block_ip(db, "1.2.3.4", "Teste", duration_minutes=5)
    
    # Verificar bloqueio
    is_blocked, reason = IPBlocker.is_blocked(db, "1.2.3.4")
    assert is_blocked
```

---

## 📝 Checklist

- [ ] Instalar slowapi e configurar
- [ ] Implementar rate limiting por IP
- [ ] Implementar rate limiting por usuário
- [ ] Criar modelo BlockedIP
- [ ] Implementar IPBlocker
- [ ] Criar middleware de bloqueio
- [ ] Implementar AnomalyDetector
- [ ] Configurar CAPTCHA (opcional)
- [ ] Testar rate limiting
- [ ] Testar bloqueio de IP

---

**Status:** 🔴 Não iniciado  
**Prioridade:** ALTA  
**Tempo estimado:** 4-5 horas  
**Depende de:** FASE 4 concluída
