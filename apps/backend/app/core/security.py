"""
Módulo de segurança da aplicação
Contém funções para validação de API keys e autenticação
"""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from typing import Optional

from app.core.config import settings


# Header para API Key do webhook WhatsApp
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_webhook_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Valida API Key do webhook WhatsApp
    Se WEBHOOK_API_KEY não estiver configurado, permite acesso (modo desenvolvimento)
    """
    # Se não configurou API key, permite (modo dev)
    if not settings.WEBHOOK_API_KEY:
        return "dev-mode"
    
    # Se configurou, valida
    if not api_key or api_key != settings.WEBHOOK_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )
    
    return api_key


def verify_evolution_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Valida API Key da Evolution API
    """
    if not api_key or api_key != settings.EVOLUTION_AUTHENTICATION_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing Evolution API Key"
        )
    
    return api_key


# Funções de hash de senha com bcrypt
import bcrypt


def hash_senha(senha: str) -> str:
    """
    Cria hash bcrypt da senha.
    
    Args:
        senha: Senha em texto plano
        
    Returns:
        Hash bcrypt da senha
    """
    senha_bytes = senha.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(senha_bytes, salt)
    return hashed.decode('utf-8')


def verify_senha(senha: str, senha_hash: str) -> bool:
    """
    Verifica se a senha corresponde ao hash.
    
    Args:
        senha: Senha em texto plano
        senha_hash: Hash bcrypt da senha
        
    Returns:
        True se a senha corresponde, False caso contrário
    """
    senha_bytes = senha.encode('utf-8')
    senha_hash_bytes = senha_hash.encode('utf-8')
    return bcrypt.checkpw(senha_bytes, senha_hash_bytes)


# Alias para compatibilidade
get_password_hash = hash_senha
verify_password = verify_senha


# Autenticação Admin JWT
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from sqlalchemy.orm import Session

security_bearer = HTTPBearer()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(lambda: None)  # Será injetado pelo FastAPI
):
    """
    Valida token JWT e retorna admin autenticado.
    
    IMPORTANTE: Esta função precisa ser usada com Depends(get_db) no endpoint.
    
    Args:
        credentials: Credenciais HTTP Bearer
        db: Sessão do banco de dados
        
    Returns:
        Admin autenticado
        
    Raises:
        HTTPException: Se token inválido ou expirado
    """
    from app.services.admin.auth_service import AdminAuthService
    
    # Importação circular fix - get_db precisa ser injetado
    if db is None:
        from app.db.session import get_db as _get_db
        db = next(_get_db())
    
    token = credentials.credentials
    
    auth_service = AdminAuthService(db)
    admin = auth_service.verify_token(token)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    return admin



def get_current_cliente(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(lambda: None)  # Será injetado pelo FastAPI
):
    """
    Valida token JWT e retorna cliente autenticado.
    
    IMPORTANTE: Esta função precisa ser usada com Depends(get_db) no endpoint.
    
    Args:
        credentials: Credenciais HTTP Bearer
        db: Sessão do banco de dados
        
    Returns:
        Cliente autenticado
        
    Raises:
        HTTPException: Se token inválido ou expirado
    """
    from app.services.auth.auth_service import AuthService
    from app.services.clientes.cliente_service import ClienteService
    
    # Importação circular fix - get_db precisa ser injetado
    if db is None:
        from app.db.session import get_db as _get_db
        db = next(_get_db())
    
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
