"""
Rotas para configurações do bot
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.api.v1.auth import get_current_cliente
from app.services.configuracoes import ConfiguracaoService


router = APIRouter()


# Schemas
class ConfiguracaoResponse(BaseModel):
    """Schema para response de configuração"""
    tom: str
    mensagem_saudacao: str
    mensagem_fallback: str
    mensagem_espera: str
    mensagem_retorno_24h: str
    
    class Config:
        from_attributes = True


class ConfiguracaoUpdateRequest(BaseModel):
    """Schema para request de atualização"""
    tom: Optional[str] = None
    mensagem_saudacao: Optional[str] = None
    mensagem_fallback: Optional[str] = None
    mensagem_espera: Optional[str] = None
    mensagem_retorno_24h: Optional[str] = None


@router.get("/config", response_model=ConfiguracaoResponse)
def get_configuracao(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Retorna configurações do bot do cliente autenticado
    Se não existir, cria com valores padrão
    """
    config = ConfiguracaoService.buscar_ou_criar(db, cliente.id)
    
    return {
        "tom": config.tom.value,
        "mensagem_saudacao": config.mensagem_saudacao,
        "mensagem_fallback": config.mensagem_fallback,
        "mensagem_espera": config.mensagem_espera,
        "mensagem_retorno_24h": config.mensagem_retorno_24h
    }


@router.put("/config", response_model=ConfiguracaoResponse)
def update_configuracao(
    request: ConfiguracaoUpdateRequest,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Atualiza configurações do bot do cliente autenticado
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"💾 Salvando configurações para cliente {cliente.id}")
    logger.info(f"   Tom: {request.tom}")
    logger.info(f"   Saudação: {request.mensagem_saudacao[:50] if request.mensagem_saudacao else 'None'}...")
    logger.info(f"   Fallback: {request.mensagem_fallback[:50] if request.mensagem_fallback else 'None'}...")
    
    try:
        config = ConfiguracaoService.atualizar(
            db=db,
            cliente_id=cliente.id,
            tom=request.tom,
            mensagem_saudacao=request.mensagem_saudacao,
            mensagem_fallback=request.mensagem_fallback,
            mensagem_espera=request.mensagem_espera,
            mensagem_retorno_24h=request.mensagem_retorno_24h
        )
        
        logger.info(f"✅ Configurações salvas com sucesso para cliente {cliente.id}")
        
        return {
            "tom": config.tom.value,
            "mensagem_saudacao": config.mensagem_saudacao,
            "mensagem_fallback": config.mensagem_fallback,
            "mensagem_espera": config.mensagem_espera,
            "mensagem_retorno_24h": config.mensagem_retorno_24h
        }
    except Exception as e:
        logger.error(f"❌ Erro ao salvar configurações: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar configurações: {str(e)}"
        )
