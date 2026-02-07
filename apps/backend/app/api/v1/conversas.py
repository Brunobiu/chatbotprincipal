"""
API endpoints para gerenciar conversas e fallback humano
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.db.models.conversa import Conversa, StatusConversa
from app.db.models.mensagem import Mensagem
from app.db.models.cliente import Cliente
from app.services.fallback import FallbackService

router = APIRouter()


# Schemas Pydantic
class ConversaAguardandoResponse(BaseModel):
    """Schema para conversa aguardando humano"""
    id: int
    cliente_id: int
    cliente_nome: str
    numero_whatsapp: str
    status: str
    motivo_fallback: str
    tempo_espera_minutos: int
    ultima_mensagem: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssumirConversaRequest(BaseModel):
    """Schema para assumir conversa"""
    atendente_email: EmailStr


class MensagemHistoricoResponse(BaseModel):
    """Schema para mensagem no histórico"""
    id: int
    remetente: str
    conteudo: str
    tipo: str
    confidence_score: float | None
    fallback_triggered: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/conversas/aguardando-humano", response_model=List[ConversaAguardandoResponse])
def listar_conversas_aguardando(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """
    Lista todas as conversas aguardando atendimento humano
    Ordenadas por tempo de espera (mais antigas primeiro)
    """
    # Buscar cliente
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Buscar conversas aguardando do cliente
    conversas = db.query(Conversa).filter(
        Conversa.cliente_id == cliente_id,
        Conversa.status == "aguardando_humano"
    ).order_by(Conversa.created_at.asc()).all()
    
    resultado = []
    for conversa in conversas:
        # Calcular tempo de espera
        tempo_espera = datetime.utcnow() - conversa.created_at
        tempo_espera_minutos = int(tempo_espera.total_seconds() / 60)
        
        # Buscar última mensagem
        ultima_msg = db.query(Mensagem).filter(
            Mensagem.conversa_id == conversa.id
        ).order_by(Mensagem.created_at.desc()).first()
        
        resultado.append(ConversaAguardandoResponse(
            id=conversa.id,
            cliente_id=conversa.cliente_id,
            cliente_nome=cliente.nome,
            numero_whatsapp=conversa.numero_whatsapp,
            status=conversa.status,
            motivo_fallback=conversa.motivo_fallback or "desconhecido",
            tempo_espera_minutos=tempo_espera_minutos,
            ultima_mensagem=ultima_msg.conteudo if ultima_msg else "",
            created_at=conversa.created_at
        ))
    
    return resultado


@router.post("/conversas/{conversa_id}/assumir")
def assumir_conversa(
    conversa_id: int,
    request: AssumirConversaRequest,
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """
    Permite que um atendente assuma uma conversa
    """
    # Buscar conversa
    conversa = db.query(Conversa).filter(
        Conversa.id == conversa_id,
        Conversa.cliente_id == cliente_id
    ).first()
    
    if not conversa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )
    
    if conversa.status != "aguardando_humano":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversa não está aguardando atendimento humano"
        )
    
    # Assumir conversa
    FallbackService.assumir_conversa(
        db=db,
        conversa_id=conversa_id,
        atendente_email=request.atendente_email
    )
    
    return {
        "status": "success",
        "message": f"Conversa assumida por {request.atendente_email}",
        "conversa_id": conversa_id
    }


@router.get("/conversas/{conversa_id}/historico", response_model=List[MensagemHistoricoResponse])
def obter_historico_conversa(
    conversa_id: int,
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """
    Retorna o histórico completo de mensagens de uma conversa
    Ordenado por data (mais antigas primeiro)
    """
    # Buscar conversa
    conversa = db.query(Conversa).filter(
        Conversa.id == conversa_id,
        Conversa.cliente_id == cliente_id
    ).first()
    
    if not conversa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )
    
    # Buscar mensagens
    mensagens = db.query(Mensagem).filter(
        Mensagem.conversa_id == conversa_id
    ).order_by(Mensagem.created_at.asc()).all()
    
    return [
        MensagemHistoricoResponse(
            id=msg.id,
            remetente=msg.remetente,
            conteudo=msg.conteudo,
            tipo=msg.tipo,
            confidence_score=msg.confidence_score,
            fallback_triggered=msg.fallback_triggered,
            created_at=msg.created_at
        )
        for msg in mensagens
    ]
