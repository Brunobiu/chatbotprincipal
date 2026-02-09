"""
Rotas de Gerenciamento de APIs de IA
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import base64

from app.db.session import get_db
from app.db.models.ia_configuracao import IAConfiguracao

router = APIRouter()


class ConfigResponse(BaseModel):
    """Response de configuração"""
    provedor: str
    modelo: str
    ativo: bool
    configurado: bool
    api_key_masked: str | None


class AddKeyRequest(BaseModel):
    """Request para adicionar API key"""
    provedor: str
    api_key: str
    modelo: str


class SetActiveRequest(BaseModel):
    """Request para ativar provedor"""
    provedor: str


class ChangeModelRequest(BaseModel):
    """Request para trocar modelo"""
    provedor: str
    modelo: str


# Modelos disponíveis por provedor
MODELOS_DISPONIVEIS = {
    'openai': ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
    'anthropic': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
    'google': ['gemini-pro', 'gemini-ultra'],
    'xai': ['grok-beta', 'grok-1'],
    'ollama': ['llama2', 'mistral', 'codellama', 'neural-chat', 'starling-lm']
}


def encrypt_key(key: str) -> str:
    """Criptografia simples (base64) - em produção usar Fernet"""
    return base64.b64encode(key.encode()).decode()


def decrypt_key(encrypted: str) -> str:
    """Descriptografia simples"""
    return base64.b64decode(encrypted.encode()).decode()


def mask_key(key: str) -> str:
    """Mascara API key"""
    if len(key) < 8:
        return "••••"
    return f"{key[:3]}...••••"


@router.get("/config", response_model=list[ConfigResponse])
def get_config(db: Session = Depends(get_db)):
    """
    Lista todas as configurações de IA
    """
    configs = db.query(IAConfiguracao).all()
    
    return [
        {
            'provedor': c.provedor,
            'modelo': c.modelo,
            'ativo': c.ativo,
            'configurado': c.configurado,
            'api_key_masked': mask_key(decrypt_key(c.api_key_encrypted)) if c.api_key_encrypted else None
        }
        for c in configs
    ]


@router.post("/add-key")
def add_key(request: AddKeyRequest, db: Session = Depends(get_db)):
    """
    Adiciona/atualiza API key
    """
    # Validar provedor
    if request.provedor not in MODELOS_DISPONIVEIS:
        raise HTTPException(400, "Provedor inválido")
    
    # Validar modelo
    if request.modelo not in MODELOS_DISPONIVEIS[request.provedor]:
        raise HTTPException(400, "Modelo inválido para este provedor")
    
    # Buscar configuração
    config = db.query(IAConfiguracao).filter_by(provedor=request.provedor).first()
    
    if not config:
        raise HTTPException(404, "Configuração não encontrada")
    
    # Atualizar
    config.api_key_encrypted = encrypt_key(request.api_key)
    config.modelo = request.modelo
    config.configurado = True
    config.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {'message': 'API key adicionada com sucesso'}


@router.delete("/remove-key")
def remove_key(provedor: str, db: Session = Depends(get_db)):
    """
    Remove API key
    """
    config = db.query(IAConfiguracao).filter_by(provedor=provedor).first()
    
    if not config:
        raise HTTPException(404, "Configuração não encontrada")
    
    config.api_key_encrypted = None
    config.configurado = False
    config.ativo = False
    config.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {'message': 'API key removida'}


@router.put("/set-active")
def set_active(request: SetActiveRequest, db: Session = Depends(get_db)):
    """
    Ativa um provedor (desativa os outros)
    """
    # Verificar se está configurado
    config = db.query(IAConfiguracao).filter_by(provedor=request.provedor).first()
    
    if not config:
        raise HTTPException(404, "Configuração não encontrada")
    
    if not config.configurado:
        raise HTTPException(400, "Provedor não configurado. Adicione uma API key primeiro.")
    
    # Desativar todos
    db.query(IAConfiguracao).update({'ativo': False})
    
    # Ativar o escolhido
    config.ativo = True
    config.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {'message': f'{request.provedor.title()} ativado como modelo principal'}


@router.put("/change-model")
def change_model(request: ChangeModelRequest, db: Session = Depends(get_db)):
    """
    Troca modelo de um provedor
    """
    # Validar modelo
    if request.modelo not in MODELOS_DISPONIVEIS.get(request.provedor, []):
        raise HTTPException(400, "Modelo inválido")
    
    config = db.query(IAConfiguracao).filter_by(provedor=request.provedor).first()
    
    if not config:
        raise HTTPException(404, "Configuração não encontrada")
    
    config.modelo = request.modelo
    config.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {'message': f'Modelo alterado para {request.modelo}'}


@router.get("/modelos-disponiveis")
def get_modelos_disponiveis():
    """
    Lista modelos disponíveis por provedor
    """
    return MODELOS_DISPONIVEIS
