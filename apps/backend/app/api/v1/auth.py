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


class RegisterRequest(BaseModel):
    """Schema para request de cadastro"""
    nome: str
    email: EmailStr
    senha: str
    aceitar_termos: bool


class RegisterResponse(BaseModel):
    """Schema para response de cadastro"""
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


class TrialStatusResponse(BaseModel):
    """Schema para response de trial status"""
    subscription_status: str
    trial_ends_at: str | None
    days_remaining: int | None
    is_expired: bool


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
    from datetime import datetime
    
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
    
    # Verificar trial expirado
    if cliente.subscription_status == 'trial' and cliente.trial_ends_at:
        if datetime.utcnow() > cliente.trial_ends_at:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Trial expirado. Assine um plano para continuar."
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


@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Endpoint de cadastro
    
    Cria novo cliente com trial de 7 dias grátis
    """
    from datetime import datetime, timedelta
    import bcrypt
    from app.db.models.cliente import Cliente, ClienteStatus
    
    # Validar termos
    if not request.aceitar_termos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você deve aceitar os termos de uso"
        )
    
    # Validar senha (mínimo 8 caracteres)
    if len(request.senha) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha deve ter no mínimo 8 caracteres"
        )
    
    # Verificar se email já existe
    cliente_existente = db.query(Cliente).filter_by(email=request.email).first()
    if cliente_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Hash da senha
    senha_hash = bcrypt.hashpw(request.senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Criar cliente com trial
    now = datetime.utcnow()
    trial_ends = now + timedelta(days=7)
    
    cliente = Cliente(
        nome=request.nome,
        email=request.email,
        senha_hash=senha_hash,
        status=ClienteStatus.ATIVO,
        trial_starts_at=now,
        trial_ends_at=trial_ends,
        subscription_status='trial',
        created_at=now,
        updated_at=now
    )
    
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    
    # Criar token JWT
    token = AuthService.criar_token_acesso(cliente.id, cliente.email)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "email": cliente.email,
            "status": cliente.status.value,
            "trial_ends_at": trial_ends.isoformat()
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


@router.get("/trial-status", response_model=TrialStatusResponse)
def get_trial_status(cliente = Depends(get_current_cliente)):
    """
    Endpoint para pegar status do trial
    """
    from datetime import datetime
    
    days_remaining = None
    is_expired = False
    
    if cliente.subscription_status == 'trial' and cliente.trial_ends_at:
        now = datetime.utcnow()
        if now > cliente.trial_ends_at:
            is_expired = True
            days_remaining = 0
        else:
            delta = cliente.trial_ends_at - now
            days_remaining = delta.days
    
    return {
        "subscription_status": cliente.subscription_status,
        "trial_ends_at": cliente.trial_ends_at.isoformat() if cliente.trial_ends_at else None,
        "days_remaining": days_remaining,
        "is_expired": is_expired
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
