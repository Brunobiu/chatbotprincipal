"""
API endpoints para gerenciar conversas e fallback humano
FASE 2: Protegido contra IDOR com OwnershipVerifier
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.db.models.conversa import Conversa, StatusConversa
from app.db.models.mensagem import Mensagem
from app.db.models.cliente import Cliente
from app.services.fallback import FallbackService
from app.services.conversas import ConversaService
from app.core.security import get_current_user
from app.core.ownership import OwnershipVerifier  # FASE 2

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


class ConversaListResponse(BaseModel):
    """Schema para lista de conversas"""
    conversas: List[dict]
    total: int
    pagina: int
    total_paginas: int


@router.get("/conversas", response_model=ConversaListResponse)
def listar_conversas(
    filtro_data_inicio: Optional[str] = Query(None, description="Data início (ISO format)"),
    filtro_data_fim: Optional[str] = Query(None, description="Data fim (ISO format)"),
    filtro_status: Optional[str] = Query(None, description="Status da conversa"),
    pagina: int = Query(1, ge=1, description="Número da página"),
    current_user: Cliente = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista conversas do cliente com filtros e paginação.
    
    - **filtro_data_inicio**: Filtrar conversas a partir desta data
    - **filtro_data_fim**: Filtrar conversas até esta data
    - **filtro_status**: Filtrar por status (ia_ativa, aguardando_humano, humano_respondeu)
    - **pagina**: Número da página (20 conversas por página)
    """
    # Converter strings de data para datetime
    data_inicio = None
    data_fim = None
    
    if filtro_data_inicio:
        try:
            data_inicio = datetime.fromisoformat(filtro_data_inicio.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data_inicio inválido. Use ISO format (YYYY-MM-DD)"
            )
    
    if filtro_data_fim:
        try:
            data_fim = datetime.fromisoformat(filtro_data_fim.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data_fim inválido. Use ISO format (YYYY-MM-DD)"
            )
    
    # Chamar serviço
    resultado = ConversaService.listar_conversas(
        db=db,
        cliente_id=current_user.id,
        filtro_data_inicio=data_inicio,
        filtro_data_fim=data_fim,
        filtro_status=filtro_status,
        pagina=pagina,
        itens_por_pagina=20
    )
    
    return resultado


@router.get("/conversas/{conversa_id}/mensagens")
def obter_mensagens_conversa(
    conversa_id: int,
    current_user: Cliente = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna histórico de mensagens de uma conversa.
    FASE 2: Verifica ownership antes de retornar mensagens
    
    - **conversa_id**: ID da conversa
    """
    # FASE 2: Verificar que a conversa pertence ao cliente
    conversa = OwnershipVerifier.verify_ownership(
        db=db,
        model=Conversa,
        resource_id=conversa_id,
        cliente=current_user
    )
    
    mensagens = ConversaService.obter_historico_conversa(
        db=db,
        conversa_id=conversa_id,
        cliente_id=current_user.id
    )
    
    if not mensagens:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada ou sem mensagens"
        )
    
    return {"mensagens": mensagens}


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
    current_user: Cliente = Depends(get_current_user),  # FASE 2: Adicionar autenticação
    db: Session = Depends(get_db)
):
    """
    Permite que um atendente assuma uma conversa
    FASE 2: Verifica ownership antes de permitir assumir
    """
    # FASE 2: Verificar que a conversa pertence ao cliente autenticado
    conversa = OwnershipVerifier.verify_ownership(
        db=db,
        model=Conversa,
        resource_id=conversa_id,
        cliente=current_user
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
    current_user: Cliente = Depends(get_current_user),  # FASE 2: Usar autenticação
    db: Session = Depends(get_db)
):
    """
    Retorna o histórico completo de mensagens de uma conversa
    FASE 2: Verifica ownership antes de retornar histórico
    Ordenado por data (mais antigas primeiro)
    """
    # FASE 2: Verificar que a conversa pertence ao cliente autenticado
    conversa = OwnershipVerifier.verify_ownership(
        db=db,
        model=Conversa,
        resource_id=conversa_id,
        cliente=current_user
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
