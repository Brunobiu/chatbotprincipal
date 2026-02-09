"""
Exemplo de como integrar a FASE 1 no main.py

Copie e adapte as seções relevantes para o seu main.py
"""

# ============================================
# IMPORTS NECESSÁRIOS
# ============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Imports da FASE 1
from app.api.v1 import auth_v2
from app.core.middleware import (
    ErrorHandlerMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    LoginRateLimitMiddleware
)

# ============================================
# CRIAR APP
# ============================================

app = FastAPI(
    title="WhatsApp AI Bot API",
    description="API para gerenciamento de bot WhatsApp com IA",
    version="1.0.0"
)

# ============================================
# MIDDLEWARES (ORDEM IMPORTA!)
# ============================================

# 1. CORS (primeiro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Ajustar conforme necessário
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Rate Limiting de Login (mais específico primeiro)
app.add_middleware(
    LoginRateLimitMiddleware,
    max_attempts=5,        # 5 tentativas de login
    window_seconds=900     # em 15 minutos (900 segundos)
)

# 3. Rate Limiting Global
app.add_middleware(
    RateLimitMiddleware,
    max_requests=100,      # 100 requisições
    window_seconds=60      # por minuto
)

# 4. Error Handler
app.add_middleware(ErrorHandlerMiddleware)

# 5. Logging
app.add_middleware(LoggingMiddleware)

# ============================================
# ROTAS
# ============================================

# Rotas de autenticação V2 (FASE 1)
app.include_router(
    auth_v2.router,
    prefix="/api/v1/auth-v2",
    tags=["auth-v2"]
)

# Suas outras rotas existentes...
# from app.api.v1 import auth, conversas, tickets, etc
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# ...

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return {
        "status": "ok",
        "message": "API is running",
        "security": {
            "fase_1": "implemented",
            "rate_limiting": "enabled",
            "jwt_v2": "enabled"
        }
    }

# ============================================
# STARTUP EVENT (OPCIONAL)
# ============================================

@app.on_event("startup")
async def startup_event():
    """Executado quando a aplicação inicia"""
    print("🚀 API iniciada com sucesso!")
    print("✅ FASE 1 - Autenticação Forte: ATIVA")
    print("✅ Rate Limiting: ATIVO")
    print("✅ Login Rate Limiting: ATIVO")
    print("⚠️  Lembre-se de configurar JWT_SECRET_KEY no .env")

# ============================================
# EXEMPLO DE USO
# ============================================

"""
Para rodar:

1. Aplicar migration:
   cd apps/backend
   alembic upgrade head

2. Configurar .env:
   JWT_SECRET_KEY=<sua-chave-secreta-aqui>

3. Iniciar servidor:
   uvicorn app.main:app --reload --port 8000

4. Testar:
   curl -X POST http://localhost:8000/api/v1/auth-v2/login \
     -H "Content-Type: application/json" \
     -d '{"email": "teste@example.com", "senha": "senha123"}'

5. Verificar health:
   curl http://localhost:8000/health
"""

# ============================================
# CONFIGURAÇÕES RECOMENDADAS
# ============================================

"""
Desenvolvimento (.env):
JWT_SECRET_KEY=dev-secret-key-not-for-production
RATE_LIMIT_PER_MINUTE=1000
LOGIN_RATE_LIMIT_PER_15MIN=50

Produção (.env):
JWT_SECRET_KEY=<chave-gerada-aleatoriamente>
RATE_LIMIT_PER_MINUTE=100
LOGIN_RATE_LIMIT_PER_15MIN=5

Gerar chave segura:
python -c "import secrets; print(secrets.token_urlsafe(32))"
"""
