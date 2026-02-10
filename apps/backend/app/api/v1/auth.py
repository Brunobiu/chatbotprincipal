"""
Rotas de autenticação (login, me)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
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
    device_fingerprint: str = None  # Fingerprint do navegador (opcional)
    telefone: str = None  # Telefone para verificação SMS (opcional - FASE 4)


class SendSMSRequest(BaseModel):
    """Schema para envio de SMS"""
    telefone: str


class VerifySMSRequest(BaseModel):
    """Schema para verificação de SMS"""
    telefone: str
    codigo: str


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
    telefone_cadastro: str | None = None
    nome_empresa: str | None = None
    status: str
    foto_perfil: str | None = None


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
def register(request: RegisterRequest, db: Session = Depends(get_db), client_ip: str = Header(None, alias="X-Real-IP")):
    """
    Endpoint de cadastro
    
    Cria novo cliente com trial de 7 dias grátis
    Proteção anti-abuso: valida e-mail temporário e limite de IPs
    """
    from datetime import datetime, timedelta
    import bcrypt
    from app.db.models.cliente import Cliente, ClienteStatus
    from app.utils.blocked_email_domains import is_disposable_email
    from fastapi import Request
    
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
    
    # PROTEÇÃO 1: Bloquear e-mails temporários
    if is_disposable_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "TEMP_EMAIL_BLOCKED",
                "message": "E-mails temporários não são permitidos. Use um e-mail válido."
            }
        )
    
    # Verificar se email já existe
    cliente_existente = db.query(Cliente).filter_by(email=request.email).first()
    if cliente_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # PROTEÇÃO 2: Limitar cadastros por IP (máx 2 em 30 dias)
    if client_ip:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        contas_mesmo_ip = db.query(Cliente).filter(
            Cliente.ip_cadastro == client_ip,
            Cliente.created_at >= thirty_days_ago
        ).count()
        
        if contas_mesmo_ip >= 2:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "IP_LIMIT_EXCEEDED",
                    "message": "Limite de cadastros atingido. Tente novamente mais tarde."
                }
            )
    
    # PROTEÇÃO 3: Bloquear device fingerprint com trial ativo
    if request.device_fingerprint:
        cliente_mesmo_device = db.query(Cliente).filter(
            Cliente.device_fingerprint == request.device_fingerprint,
            Cliente.subscription_status == 'trial'
        ).first()
        
        if cliente_mesmo_device:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "DEVICE_ALREADY_USED",
                    "message": "Este dispositivo já possui um trial ativo."
                }
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
        ip_cadastro=client_ip,  # Salvar IP do cadastro
        device_fingerprint=request.device_fingerprint,  # Salvar fingerprint
        telefone_cadastro=request.telefone if request.telefone else None,  # Salvar telefone
        telefone_verificado=0,  # Não verificado por padrão
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
        "telefone_cadastro": cliente.telefone_cadastro,
        "nome_empresa": cliente.nome_empresa,
        "status": cliente.status.value,
        "foto_perfil": cliente.foto_perfil
    }


@router.post("/send-sms-code")
def send_sms_code(request: SendSMSRequest, db: Session = Depends(get_db)):
    """
    Envia código de verificação por SMS
    FASE 4: Proteção Anti-Abuso
    """
    from app.services.sms.sms_service import SMSService
    
    result = SMSService.enviar_codigo(db, request.telefone)
    
    if not result["success"]:
        if result.get("code") == "PHONE_ALREADY_USED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "PHONE_ALREADY_USED",
                    "message": result["message"]
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result


@router.post("/verify-sms-code")
def verify_sms_code(request: VerifySMSRequest, db: Session = Depends(get_db)):
    """
    Verifica código SMS
    FASE 4: Proteção Anti-Abuso
    """
    from app.services.sms.sms_service import SMSService
    
    result = SMSService.verificar_codigo(db, request.telefone, request.codigo)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result


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




@router.post("/sms/send")
async def enviar_sms(
    request: SendSMSRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para enviar código de verificação por SMS
    
    Envia código de 6 dígitos válido por 10 minutos
    Limite: 1 SMS a cada 2 minutos por telefone
    """
    from app.services.sms_service import sms_service
    
    resultado = await sms_service.enviar_sms(request.telefone, db)
    
    if not resultado["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado["message"]
        )
    
    return resultado


@router.post("/sms/verify")
async def verificar_sms(
    request: VerifySMSRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para verificar código SMS
    
    Valida código de 6 dígitos
    Máximo 3 tentativas por código
    Código expira em 10 minutos
    """
    from app.services.sms_service import sms_service
    
    resultado = await sms_service.verificar_codigo(request.telefone, request.codigo, db)
    
    if not resultado["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado["message"]
        )
    
    return resultado



class AtualizarPerfilRequest(BaseModel):
    """Schema para atualizar perfil"""
    nome: str
    email: EmailStr
    telefone: str | None = None
    nome_empresa: str | None = None


class FotoPerfilRequest(BaseModel):
    """Schema para atualizar foto de perfil"""
    foto_base64: str


@router.put("/perfil")
async def atualizar_perfil(
    request: AtualizarPerfilRequest,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """Atualizar dados do perfil do cliente"""
    try:
        # Atualizar dados
        cliente.nome = request.nome
        cliente.email = request.email
        if request.telefone:
            cliente.telefone_cadastro = request.telefone
        if request.nome_empresa:
            cliente.nome_empresa = request.nome_empresa
        
        db.commit()
        db.refresh(cliente)
        
        return {
            "id": cliente.id,
            "nome": cliente.nome,
            "email": cliente.email,
            "telefone": cliente.telefone,
            "telefone_cadastro": cliente.telefone_cadastro,
            "nome_empresa": cliente.nome_empresa,
            "status": cliente.status.value,
            "foto_perfil": cliente.foto_perfil
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar perfil: {str(e)}"
        )


@router.put("/foto-perfil")
async def atualizar_foto_perfil(
    request: FotoPerfilRequest,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """Atualizar foto de perfil do cliente"""
    try:
        # Salvar foto (base64)
        cliente.foto_perfil = request.foto_base64
        
        db.commit()
        db.refresh(cliente)
        
        return {
            "id": cliente.id,
            "nome": cliente.nome,
            "email": cliente.email,
            "telefone": cliente.telefone,
            "telefone_cadastro": cliente.telefone_cadastro,
            "status": cliente.status.value,
            "foto_perfil": cliente.foto_perfil
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar foto: {str(e)}"
        )
