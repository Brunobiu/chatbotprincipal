"""
Endpoints de Chat Suporte
Task 11.6
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.db.models.cliente import Cliente
from app.services.auth.auth_service import AuthService
from app.services.chat_suporte.chat_suporte_service import ChatSuporteService


router = APIRouter()


# Schemas
class EnviarMensagemRequest(BaseModel):
    mensagem: str


class MensagemResponse(BaseModel):
    id: int
    remetente_tipo: str
    mensagem: str
    confianca: float | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RespostaSuporteResponse(BaseModel):
    resposta: str
    confianca: float
    deve_abrir_ticket: bool


@router.post("/mensagem", response_model=RespostaSuporteResponse)
def enviar_mensagem(
    request: EnviarMensagemRequest,
    db: Session = Depends(get_db),
    current_cliente: Cliente = Depends(AuthService.get_current_cliente)
):
    """
    Envia mensagem no chat suporte e recebe resposta automática da IA
    """
    try:
        resultado = ChatSuporteService.enviar_mensagem(
            db=db,
            cliente_id=current_cliente.id,
            mensagem=request.mensagem
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar mensagem: {str(e)}")


@router.get("/historico", response_model=List[MensagemResponse])
def obter_historico(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_cliente: Cliente = Depends(AuthService.get_current_cliente)
):
    """
    Retorna histórico de mensagens do chat suporte
    """
    mensagens = ChatSuporteService.obter_historico(
        db=db,
        cliente_id=current_cliente.id,
        limit=limit
    )
    return mensagens


@router.delete("/historico")
def limpar_historico(
    db: Session = Depends(get_db),
    current_cliente: Cliente = Depends(AuthService.get_current_cliente)
):
    """
    Limpa histórico de mensagens do chat suporte
    """
    sucesso = ChatSuporteService.limpar_historico(
        db=db,
        cliente_id=current_cliente.id
    )
    
    if sucesso:
        return {"message": "Histórico limpo com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao limpar histórico")
