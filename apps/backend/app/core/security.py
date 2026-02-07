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
