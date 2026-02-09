# FASE 3 - Proteção do Banco de Dados

## 🎯 Objetivo
Garantir que TODAS as queries sejam seguras contra SQL Injection e que dados sensíveis sejam criptografados.

---

## 📋 Implementações

### 3.1 Auditoria de Queries

**Buscar queries vulneráveis:**
```bash
# Procurar por concatenação de strings em queries
grep -r "f\"SELECT" apps/backend/
grep -r "f'SELECT" apps/backend/
grep -r ".format(" apps/backend/app/services/
```

**Padrões vulneráveis:**
```python
# ❌ NUNCA FAZER
query = f"SELECT * FROM users WHERE email = '{email}'"
query = "SELECT * FROM users WHERE id = " + str(user_id)
db.execute(f"DELETE FROM {table_name} WHERE id = {id}")
```

**Padrões seguros:**
```python
# ✅ SEMPRE USAR
# SQLAlchemy ORM (preferido)
user = db.query(User).filter(User.email == email).first()

# Raw SQL com parâmetros
db.execute("SELECT * FROM users WHERE email = :email", {"email": email})
```

---

### 3.2 Validação e Sanitização de Inputs

**Novo arquivo:** `apps/backend/app/core/validators.py`

```python
from pydantic import BaseModel, validator, EmailStr
import re

class EmailValidator:
    @staticmethod
    def validate(email: str) -> str:
        # Pydantic EmailStr já valida formato
        if len(email) > 255:
            raise ValueError("Email muito longo")
        return email.lower().strip()

class StringValidator:
    @staticmethod
    def sanitize(text: str, max_length: int = 500) -> str:
        """Remove caracteres perigosos"""
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Limita tamanho
        text = text[:max_length]
        
        # Remove caracteres de controle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()

class SQLSafeValidator:
    """Valida que string não contém padrões de SQL injection"""
    
    DANGEROUS_PATTERNS = [
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(--)",
        r"(;.*DROP)",
        r"(;.*DELETE)",
        r"(;.*UPDATE)",
        r"(UNION.*SELECT)",
        r"(\/\*.*\*\/)",
    ]
    
    @staticmethod
    def validate(text: str) -> str:
        text_upper = text.upper()
        
        for pattern in SQLSafeValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                raise ValueError("Input contém padrão suspeito")
        
        return text
```

**Aplicar em todos os Pydantic models:**
```python
from app.core.validators import StringValidator, SQLSafeValidator

class ConversaCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    
    @validator('titulo')
    def validate_titulo(cls, v):
        v = StringValidator.sanitize(v, max_length=200)
        v = SQLSafeValidator.validate(v)
        return v
    
    @validator('descricao')
    def validate_descricao(cls, v):
        if v:
            v = StringValidator.sanitize(v, max_length=1000)
        return v
```

---

### 3.3 Criptografia de Dados Sensíveis

**Novo arquivo:** `apps/backend/app/core/encryption.py`

```python
from cryptography.fernet import Fernet
from app.core.config import settings
import base64

class DataEncryption:
    """Criptografia de dados sensíveis"""
    
    def __init__(self):
        # Chave deve estar em .env
        key = settings.ENCRYPTION_KEY.encode()
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Criptografa string"""
        if not data:
            return ""
        
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Descriptografa string"""
        if not encrypted_data:
            return ""
        
        decoded = base64.b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(decoded)
        return decrypted.decode()

# Instância global
encryptor = DataEncryption()
```

**Adicionar ao .env:**
```bash
# Gerar chave: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-generated-key-here
```

**Campos para criptografar:**
- Email (opcional, mas recomendado para GDPR)
- Telefone
- Dados de API keys de clientes
- Qualquer PII (Personally Identifiable Information)

**Exemplo de uso:**
```python
from app.core.encryption import encryptor

# Ao salvar
cliente.telefone_encrypted = encryptor.encrypt(telefone)

# Ao ler
telefone = encryptor.decrypt(cliente.telefone_encrypted)
```

---

### 3.4 Prepared Statements em Raw Queries

**Se precisar usar raw SQL:**

```python
# ✅ CORRETO - Parâmetros nomeados
result = db.execute(
    text("SELECT * FROM conversas WHERE cliente_id = :cliente_id AND status = :status"),
    {"cliente_id": cliente_id, "status": status}
)

# ✅ CORRETO - Parâmetros posicionais
result = db.execute(
    text("SELECT * FROM conversas WHERE cliente_id = ? AND status = ?"),
    (cliente_id, status)
)

# ❌ NUNCA
result = db.execute(
    f"SELECT * FROM conversas WHERE cliente_id = {cliente_id}"
)
```

---

### 3.5 Auditoria de Queries Sensíveis

**Novo arquivo:** `apps/backend/app/core/query_logger.py`

```python
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

query_logger = logging.getLogger("queries")

@event.listens_for(Engine, "before_cursor_execute")
def log_queries(conn, cursor, statement, parameters, context, executemany):
    """Log todas queries que tocam tabelas sensíveis"""
    
    sensitive_tables = [
        "clientes",
        "refresh_tokens",
        "instancias_whatsapp",
        "configuracoes_bot"
    ]
    
    statement_upper = statement.upper()
    
    for table in sensitive_tables:
        if table.upper() in statement_upper:
            query_logger.info(f"Query sensível: {statement[:200]}")
            break
```

---

## 🧪 Testes

### Teste 1: SQL Injection Básico
```python
def test_sql_injection_basic():
    # Tentar injetar SQL no campo email
    malicious_email = "test@test.com' OR '1'='1"
    
    response = client.post("/api/v1/auth/login", json={
        "email": malicious_email,
        "senha": "any"
    })
    
    # Não deve retornar todos usuários
    # Deve retornar erro de validação ou 401
    assert response.status_code in [400, 401, 422]
```

### Teste 2: Validação de Input
```python
def test_input_validation():
    # String muito longa
    long_string = "A" * 10000
    
    response = client.post("/api/v1/conversas", json={
        "titulo": long_string
    })
    
    # Deve rejeitar
    assert response.status_code == 422
```

### Teste 3: Criptografia
```python
def test_encryption():
    from app.core.encryption import encryptor
    
    original = "dados sensíveis"
    encrypted = encryptor.encrypt(original)
    decrypted = encryptor.decrypt(encrypted)
    
    assert encrypted != original
    assert decrypted == original
```

---

## 📝 Checklist

- [ ] Auditar todas queries (grep por concatenação)
- [ ] Criar `validators.py`
- [ ] Aplicar validação em todos Pydantic models
- [ ] Criar `encryption.py`
- [ ] Gerar chave de criptografia
- [ ] Identificar campos sensíveis para criptografar
- [ ] Criar migration para campos criptografados
- [ ] Criar `query_logger.py`
- [ ] Testar SQL injection
- [ ] Testar validação de inputs
- [ ] Testar criptografia

---

## 🚨 Pontos Críticos

1. **NUNCA concatenar strings em queries**
2. **SEMPRE validar inputs antes de usar**
3. **Criptografar dados sensíveis at-rest**
4. **Usar ORM sempre que possível**
5. **Logar queries sensíveis para auditoria**

---

**Status:** 🔴 Não iniciado  
**Prioridade:** CRÍTICA  
**Tempo estimado:** 4-5 horas  
**Depende de:** FASE 2 concluída
