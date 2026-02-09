"""
Rotas de autenticação V2 com segurança aprimorada (FASE 1)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth.auth_service_v2 import AuthServiceV2
from app.services.clientes.cliente_service import ClienteService


router = APIRouter()
security = HTTPBearer()


# Schemas
class LoginRequest(BaseModel):
    """Schema para request de login"""
    email: EmailStr
    senha: str


class LoginResponse(BaseModel):
    """Schema para response de login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutos em segundos
    cliente: dict


class RefreshTokenRequest(BaseModel):
    """Schema para request de refresh token"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Schema para response de refresh token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900


class MeResponse(BaseModel):
    """Schema para response de /me"""
    id: int
    nome: str
    email: str
    telefone: str | None
    status: str


# Dependency para pegar cliente autenticado
def get_current_cliente(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency que valida o token JWT e retorna o cliente autenticado
    """
    token = credentials.credentials
    payload = AuthServiceV2.validar_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    cliente_id = int(payload.get("sub"))
    cliente = ClienteService.buscar_por_id(db, cliente_id)
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cliente não encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verificar se conta está bloqueada
    bloqueado, motivo = AuthServiceV2.verificar_conta_bloqueada(cliente)
    if bloqueado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=motivo
        )
    
    return cliente


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    """
    Endpoint de login com segurança aprimorada
    
    - Valida credenciais
    - Registra tentativas de login
    - Bloqueia conta após múltiplas falhas
    - Retorna access token (15 min) e refresh token (7 dias)
    """
    cliente, access_token, refresh_token = AuthServiceV2.autenticar(
        db, request.email, request.senha, req
    )
    
    if not cliente or not access_token or not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos, ou conta bloqueada",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": AuthServiceV2.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "email": cliente.email,
            "status": cliente.status.value
        }
    }


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(
    request: RefreshTokenRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Endpoint para renovar access token usando refresh token
    
    - Valida refresh token
    - Retorna novo access token (15 min)
    - Refresh token continua válido
    """
    # Extrair cliente_id do access token expirado (não valida expiração)
    try:
        import jwt
        from app.core.config import settings
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": False}  # Não verificar expiração
        )
        cliente_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Gerar novo access token
    new_access_token = AuthServiceV2.refresh_access_token(
        db, request.refresh_token, cliente_id
    )
    
    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": AuthServiceV2.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=MeResponse)
def get_me(cliente = Depends(get_current_cliente)):
    """
    Endpoint para pegar dados do cliente autenticado
    
    Requer token JWT válido no header Authorization: Bearer <token>
    """
    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "email": cliente.email,
        "telefone": cliente.telefone,
        "status": cliente.status.value
    }


@router.post("/logout")
def logout(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Endpoint para logout
    
    - Invalida refresh token do cliente
    - Cliente precisa fazer login novamente
    """
    # Invalidar refresh token
    cliente.refresh_token_hash = None
    cliente.refresh_token_expira_em = None
    db.commit()
    
    return {"message": "Logout realizado com sucesso"}
