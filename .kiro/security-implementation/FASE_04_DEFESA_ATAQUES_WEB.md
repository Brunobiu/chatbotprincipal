# FASE 4 - Defesa Contra Ataques Web

## 🎯 Objetivo
Proteger contra XSS, CSRF, Clickjacking e outros ataques comuns da web.

---

## 📋 Implementações

### 4.1 Headers de Segurança

**Arquivo:** `apps/backend/app/main.py`

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Forçar HTTPS em produção
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Headers de segurança
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Previne clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Previne MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # XSS Protection (legacy, mas não faz mal)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # HSTS - Force HTTPS por 1 ano
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://js.stripe.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://api.stripe.com; "
        "frame-src https://js.stripe.com; "
        "object-src 'none'; "
        "base-uri 'self';"
    )
    
    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions Policy
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=(), "
        "payment=(), usb=(), magnetometer=(), gyroscope=()"
    )
    
    return response
```

---

### 4.2 Proteção CSRF

**Novo arquivo:** `apps/backend/app/core/csrf.py`

```python
from fastapi import HTTPException, status, Request
import secrets
import hmac
import hashlib
from datetime import datetime, timedelta

class CSRFProtection:
    """Proteção contra CSRF"""
    
    SECRET_KEY = settings.JWT_SECRET_KEY
    
    @staticmethod
    def generate_token() -> str:
        """Gera token CSRF"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        random_part = secrets.token_urlsafe(32)
        
        # Token = timestamp + random + signature
        message = f"{timestamp}:{random_part}"
        signature = hmac.new(
            CSRFProtection.SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{message}:{signature}"
    
    @staticmethod
    def verify_token(token: str) -> bool:
        """Verifica token CSRF"""
        try:
            parts = token.split(":")
            if len(parts) != 3:
                return False
            
            timestamp, random_part, signature = parts
            
            # Verificar se não expirou (1 hora)
            token_time = datetime.fromtimestamp(int(timestamp))
            if datetime.utcnow() - token_time > timedelta(hours=1):
                return False
            
            # Verificar assinatura
            message = f"{timestamp}:{random_part}"
            expected_signature = hmac.new(
                CSRFProtection.SECRET_KEY.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        
        except Exception:
            return False

# Dependency para rotas que precisam CSRF
async def verify_csrf_token(request: Request):
    """Verifica token CSRF no header"""
    token = request.headers.get("X-CSRF-Token")
    
    if not token or not CSRFProtection.verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token CSRF inválido ou expirado"
        )
```

**Aplicar em rotas sensíveis:**
```python
from app.core.csrf import verify_csrf_token

@router.post("/billing/cancel", dependencies=[Depends(verify_csrf_token)])
async def cancel_subscription(...):
    ...

@router.delete("/instancias/{id}", dependencies=[Depends(verify_csrf_token)])
async def delete_instancia(...):
    ...
```

**Endpoint para obter token:**
```python
@router.get("/auth/csrf-token")
async def get_csrf_token():
    return {"csrf_token": CSRFProtection.generate_token()}
```

---

### 4.3 Sanitização de Inputs (XSS)

**Novo arquivo:** `apps/backend/app/core/sanitizer.py`

```python
import bleach
from typing import Optional

class HTMLSanitizer:
    """Sanitiza HTML para prevenir XSS"""
    
    # Tags permitidas (muito restritivo)
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a']
    ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}
    
    @staticmethod
    def sanitize(html: str) -> str:
        """Remove tags e atributos perigosos"""
        if not html:
            return ""
        
        return bleach.clean(
            html,
            tags=HTMLSanitizer.ALLOWED_TAGS,
            attributes=HTMLSanitizer.ALLOWED_ATTRIBUTES,
            strip=True
        )
    
    @staticmethod
    def strip_all_tags(html: str) -> str:
        """Remove TODAS as tags HTML"""
        if not html:
            return ""
        
        return bleach.clean(html, tags=[], strip=True)

class JavaScriptSanitizer:
    """Detecta tentativas de injeção de JavaScript"""
    
    DANGEROUS_PATTERNS = [
        '<script',
        'javascript:',
        'onerror=',
        'onload=',
        'onclick=',
        'onmouseover=',
        '<iframe',
        '<object',
        '<embed',
    ]
    
    @staticmethod
    def is_safe(text: str) -> bool:
        """Verifica se texto não contém JS malicioso"""
        text_lower = text.lower()
        
        for pattern in JavaScriptSanitizer.DANGEROUS_PATTERNS:
            if pattern in text_lower:
                return False
        
        return True
    
    @staticmethod
    def sanitize(text: str) -> str:
        """Remove padrões perigosos"""
        if not JavaScriptSanitizer.is_safe(text):
            raise ValueError("Input contém código potencialmente malicioso")
        
        return text
```

**Aplicar em models:**
```python
from app.core.sanitizer import HTMLSanitizer, JavaScriptSanitizer

class ConhecimentoCreate(BaseModel):
    titulo: str
    conteudo: str
    
    @validator('titulo')
    def sanitize_titulo(cls, v):
        # Remove todas tags
        return HTMLSanitizer.strip_all_tags(v)
    
    @validator('conteudo')
    def sanitize_conteudo(cls, v):
        # Permite algumas tags, remove perigosas
        return HTMLSanitizer.sanitize(v)
```

---

### 4.4 Validação de Upload de Arquivos

**Novo arquivo:** `apps/backend/app/core/file_validator.py`

```python
from fastapi import UploadFile, HTTPException, status
import magic
import os

class FileValidator:
    """Valida uploads de arquivos"""
    
    # Tipos MIME permitidos
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'text/plain',
        'text/markdown',
        'application/json',
        'image/jpeg',
        'image/png',
        'image/gif',
    }
    
    # Extensões permitidas
    ALLOWED_EXTENSIONS = {
        '.pdf', '.txt', '.md', '.json', '.jpg', '.jpeg', '.png', '.gif'
    }
    
    # Tamanho máximo: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @staticmethod
    async def validate(file: UploadFile) -> None:
        """Valida arquivo enviado"""
        
        # 1. Verificar extensão
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in FileValidator.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extensão {ext} não permitida"
            )
        
        # 2. Ler conteúdo
        content = await file.read()
        await file.seek(0)  # Reset para uso posterior
        
        # 3. Verificar tamanho
        if len(content) > FileValidator.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo muito grande (máx 10MB)"
            )
        
        # 4. Verificar MIME type real (não confiar na extensão)
        mime = magic.from_buffer(content, mime=True)
        if mime not in FileValidator.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo {mime} não permitido"
            )
        
        # 5. Verificar se não é executável
        if content.startswith(b'MZ') or content.startswith(b'\x7fELF'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivos executáveis não são permitidos"
            )
```

**Usar em rotas de upload:**
```python
from app.core.file_validator import FileValidator

@router.post("/conhecimento/upload")
async def upload_conhecimento(
    file: UploadFile,
    db: Session = Depends(get_db),
    cliente: Cliente = Depends(get_current_cliente)
):
    # Validar arquivo
    await FileValidator.validate(file)
    
    # Processar arquivo...
```

---

### 4.5 CORS Seguro

**Arquivo:** `apps/backend/app/main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

# CORS restritivo
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),  # Apenas origens específicas
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Métodos específicos
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],  # Headers específicos
    max_age=3600,  # Cache preflight por 1 hora
)
```

---

## 🧪 Testes

### Teste 1: Headers de Segurança
```python
def test_security_headers():
    response = client.get("/")
    
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in response.headers
    assert "Strict-Transport-Security" in response.headers
```

### Teste 2: XSS Protection
```python
def test_xss_protection():
    malicious_input = "<script>alert('xss')</script>"
    
    response = client.post("/api/v1/conhecimento", json={
        "titulo": malicious_input,
        "conteudo": "test"
    })
    
    # Deve sanitizar ou rejeitar
    if response.status_code == 200:
        conhecimento = response.json()
        assert "<script>" not in conhecimento["titulo"]
```

### Teste 3: CSRF Protection
```python
def test_csrf_protection():
    # Tentar deletar sem token CSRF
    response = client.delete("/api/v1/instancias/1")
    
    # Deve retornar 403
    assert response.status_code == 403
```

### Teste 4: Upload Malicioso
```python
def test_malicious_upload():
    # Tentar enviar arquivo executável
    files = {"file": ("malware.exe", b"MZ\x90\x00", "application/octet-stream")}
    
    response = client.post("/api/v1/conhecimento/upload", files=files)
    
    # Deve rejeitar
    assert response.status_code == 400
```

---

## 📝 Checklist

- [ ] Adicionar headers de segurança
- [ ] Implementar proteção CSRF
- [ ] Criar sanitizadores (HTML/JS)
- [ ] Aplicar sanitização em todos inputs
- [ ] Implementar validação de upload
- [ ] Configurar CORS restritivo
- [ ] Testar headers
- [ ] Testar XSS
- [ ] Testar CSRF
- [ ] Testar upload malicioso

---

**Status:** 🔴 Não iniciado  
**Prioridade:** ALTA  
**Tempo estimado:** 5-6 horas  
**Depende de:** FASE 3 concluída
