"""
Rotas de autenticação (login, me)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth.auth_service import AuthService
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
    token_type: str = "bearer"
    cliente: dict


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
    payload = AuthService.validar_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    cliente_id = int(payload.get("sub"))
    cliente = ClienteService.buscar_por_id(db, cliente_id)
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cliente não encontrado"
        )
    
    return cliente


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint de login
    
    Recebe email e senha, retorna token JWT se credenciais válidas
    """
    cliente = AuthService.autenticar(db, request.email, request.senha)
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Criar token JWT
    token = AuthService.criar_token_acesso(cliente.id, cliente.email)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "email": cliente.email,
            "status": cliente.status.value
        }
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
