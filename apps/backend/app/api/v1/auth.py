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
from app.services.perfil.perfil_service import PerfilService


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


class TrocarSenhaRequest(BaseModel):
    """Schema para request de trocar senha"""
    senha_atual: str
    senha_nova: str


class TrocarSenhaResponse(BaseModel):
    """Schema para response de trocar senha"""
    message: str


class EditarPerfilRequest(BaseModel):
    """Schema para request de editar perfil"""
    nome: str | None = None
    telefone: str | None = None
    email: EmailStr | None = None
    senha_confirmacao: str


class EditarPerfilResponse(BaseModel):
    """Schema para response de editar perfil"""
    id: int
    nome: str
    email: str
    telefone: str | None
    status: str
    message: str


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


@router.post("/trocar-senha", response_model=TrocarSenhaResponse)
def trocar_senha(
    request: TrocarSenhaRequest,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Endpoint para trocar senha do cliente autenticado
    
    Requer token JWT válido no header Authorization: Bearer <token>
    Valida senha atual antes de permitir troca
    """
    # Verificar se a senha atual está correta
    if not AuthService.verificar_senha(request.senha_atual, cliente.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Validar senha nova (mínimo 6 caracteres)
    if len(request.senha_nova) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha nova deve ter no mínimo 6 caracteres"
        )
    
    # Atualizar senha
    from datetime import datetime
    cliente.senha_hash = ClienteService.hash_senha(request.senha_nova)
    cliente.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Senha alterada com sucesso"
    }


@router.put("/perfil", response_model=EditarPerfilResponse)
def editar_perfil(
    request: EditarPerfilRequest,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Endpoint para editar perfil do cliente autenticado
    
    Requer token JWT válido no header Authorization: Bearer <token>
    Valida senha antes de permitir edição
    Permite editar: nome, telefone, email
    Valida que email é único
    """
    try:
        cliente_atualizado = PerfilService.editar_perfil(
            db=db,
            cliente_id=cliente.id,
            nome=request.nome,
            telefone=request.telefone,
            email=request.email,
            senha_confirmacao=request.senha_confirmacao
        )
        
        return {
            "id": cliente_atualizado.id,
            "nome": cliente_atualizado.nome,
            "email": cliente_atualizado.email,
            "telefone": cliente_atualizado.telefone,
            "status": cliente_atualizado.status.value,
            "message": "Perfil atualizado com sucesso"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
