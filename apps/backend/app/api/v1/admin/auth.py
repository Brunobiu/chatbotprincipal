"""
Endpoints de autenticação para administradores.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.services.admin.auth_service import AdminAuthService
from app.core.config import settings

router = APIRouter()
security = HTTPBearer()


# Pydantic Models
class AdminLoginRequest(BaseModel):
    email: str
    senha: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: "AdminResponse"


class AdminResponse(BaseModel):
    id: int
    nome: str
    email: str
    role: str
    tema: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dependency para obter IP do cliente
def get_client_ip(request: Request) -> str:
    """Extrai IP do cliente da requisição"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# Dependency para obter User-Agent
def get_user_agent(request: Request) -> Optional[str]:
    """Extrai User-Agent da requisição"""
    return request.headers.get("User-Agent")


# Dependency para autenticação
def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Valida token JWT e retorna admin autenticado"""
    token = credentials.credentials
    
    auth_service = AdminAuthService(db)
    admin = auth_service.verify_token(token)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    return admin


@router.post("/login", response_model=AdminLoginResponse)
def login(
    request: Request,
    login_data: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login para administradores.
    
    - Valida credenciais
    - Bloqueia IP após 5 tentativas falhadas em 15 minutos
    - Retorna JWT com role=admin
    """
    ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    auth_service = AdminAuthService(db)
    
    # Verificar se IP está bloqueado
    if auth_service.check_ip_blocked(ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="IP bloqueado temporariamente devido a múltiplas tentativas de login falhadas"
        )
    
    # Autenticar
    admin = auth_service.authenticate(
        email=login_data.email,
        password=login_data.senha,
        ip=ip,
        user_agent=user_agent
    )
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Gerar token
    token = auth_service.generate_token(admin)
    
    return AdminLoginResponse(
        access_token=token,
        token_type="bearer",
        admin=AdminResponse.from_orm(admin)
    )


@router.get("/me", response_model=AdminResponse)
def get_me(
    current_admin = Depends(get_current_admin)
):
    """
    Retorna dados do perfil do administrador autenticado.
    
    Requer: Token JWT válido com role=admin
    """
    return AdminResponse.from_orm(current_admin)


@router.post("/logout")
def logout(
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Logout do administrador (invalida sessão no Redis se disponível).
    
    Requer: Token JWT válido com role=admin
    """
    # TODO: Invalidar token no Redis quando implementado
    return {"message": "Logout realizado com sucesso"}
