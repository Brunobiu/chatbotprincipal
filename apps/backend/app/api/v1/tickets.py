from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.core.security import get_current_cliente
from app.db.models.cliente import Cliente
from app.services.tickets.ticket_service import TicketService


router = APIRouter()


# ==================== SCHEMAS ====================

class AnexoSchema(BaseModel):
    nome: str
    url: str
    tipo: str
    tamanho: int


class CriarTicketRequest(BaseModel):
    assunto: str = Field(..., min_length=5, max_length=200)
    mensagem: str = Field(..., min_length=10)
    categoria_id: Optional[int] = None
    anexos: Optional[List[AnexoSchema]] = None


class AdicionarMensagemRequest(BaseModel):
    mensagem: str = Field(..., min_length=1)
    anexos: Optional[List[AnexoSchema]] = None


class CategoriaResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    
    class Config:
        from_attributes = True


class MensagemResponse(BaseModel):
    id: int
    remetente_tipo: str
    remetente_id: Optional[int]
    mensagem: str
    anexos: Optional[List[dict]]
    lida: bool
    created_at: str
    
    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    id: int
    assunto: str
    status: str
    prioridade: str
    categoria: Optional[CategoriaResponse]
    ia_respondeu: bool
    confianca_ia: Optional[float]
    created_at: str
    updated_at: str
    mensagens: Optional[List[MensagemResponse]] = None
    
    class Config:
        from_attributes = True


class ListaTicketsResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
    limit: int
    offset: int


# ==================== ENDPOINTS ====================

@router.get("/categorias", response_model=List[CategoriaResponse])
def listar_categorias(
    db: Session = Depends(get_db)
):
    """Lista categorias de tickets"""
    service = TicketService(db)
    categorias = service.listar_categorias()
    return categorias


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def criar_ticket(
    request: CriarTicketRequest,
    cliente: Cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """Cria um novo ticket"""
    service = TicketService(db)
    
    anexos = [anexo.dict() for anexo in request.anexos] if request.anexos else None
    
    ticket = service.criar_ticket(
        cliente_id=cliente.id,
        assunto=request.assunto,
        mensagem=request.mensagem,
        categoria_id=request.categoria_id,
        anexos=anexos
    )
    
    # Recarregar com relacionamentos
    ticket = service.obter_ticket_cliente(ticket.id, cliente.id)
    
    return TicketResponse(
        id=ticket.id,
        assunto=ticket.assunto,
        status=ticket.status,
        prioridade=ticket.prioridade,
        categoria=CategoriaResponse.from_orm(ticket.categoria) if ticket.categoria else None,
        ia_respondeu=ticket.ia_respondeu,
        confianca_ia=ticket.confianca_ia,
        created_at=ticket.created_at.isoformat(),
        updated_at=ticket.updated_at.isoformat(),
        mensagens=[
            MensagemResponse(
                id=m.id,
                remetente_tipo=m.remetente_tipo,
                remetente_id=m.remetente_id,
                mensagem=m.mensagem,
                anexos=m.anexos,
                lida=m.lida,
                created_at=m.created_at.isoformat()
            ) for m in ticket.mensagens
        ]
    )


@router.get("/", response_model=ListaTicketsResponse)
def listar_tickets(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    cliente: Cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """Lista tickets do cliente"""
    service = TicketService(db)
    tickets, total = service.listar_tickets_cliente(
        cliente_id=cliente.id,
        status=status,
        limit=limit,
        offset=offset
    )
    
    return ListaTicketsResponse(
        tickets=[
            TicketResponse(
                id=t.id,
                assunto=t.assunto,
                status=t.status,
                prioridade=t.prioridade,
                categoria=CategoriaResponse.from_orm(t.categoria) if t.categoria else None,
                ia_respondeu=t.ia_respondeu,
                confianca_ia=t.confianca_ia,
                created_at=t.created_at.isoformat(),
                updated_at=t.updated_at.isoformat(),
                mensagens=None  # Não incluir mensagens na lista
            ) for t in tickets
        ],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
def obter_ticket(
    ticket_id: int,
    cliente: Cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """Obtém detalhes de um ticket"""
    service = TicketService(db)
    ticket = service.obter_ticket_cliente(ticket_id, cliente.id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket não encontrado"
        )
    
    # Marcar mensagens como lidas
    service.marcar_mensagens_lidas(ticket_id, "cliente")
    
    return TicketResponse(
        id=ticket.id,
        assunto=ticket.assunto,
        status=ticket.status,
        prioridade=ticket.prioridade,
        categoria=CategoriaResponse.from_orm(ticket.categoria) if ticket.categoria else None,
        ia_respondeu=ticket.ia_respondeu,
        confianca_ia=ticket.confianca_ia,
        created_at=ticket.created_at.isoformat(),
        updated_at=ticket.updated_at.isoformat(),
        mensagens=[
            MensagemResponse(
                id=m.id,
                remetente_tipo=m.remetente_tipo,
                remetente_id=m.remetente_id,
                mensagem=m.mensagem,
                anexos=m.anexos,
                lida=m.lida,
                created_at=m.created_at.isoformat()
            ) for m in sorted(ticket.mensagens, key=lambda x: x.created_at)
        ]
    )


@router.post("/{ticket_id}/mensagens", response_model=MensagemResponse, status_code=status.HTTP_201_CREATED)
def adicionar_mensagem(
    ticket_id: int,
    request: AdicionarMensagemRequest,
    cliente: Cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """Adiciona mensagem ao ticket"""
    service = TicketService(db)
    
    anexos = [anexo.dict() for anexo in request.anexos] if request.anexos else None
    
    mensagem = service.adicionar_mensagem_cliente(
        ticket_id=ticket_id,
        cliente_id=cliente.id,
        mensagem=request.mensagem,
        anexos=anexos
    )
    
    if not mensagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket não encontrado"
        )
    
    return MensagemResponse(
        id=mensagem.id,
        remetente_tipo=mensagem.remetente_tipo,
        remetente_id=mensagem.remetente_id,
        mensagem=mensagem.mensagem,
        anexos=mensagem.anexos,
        lida=mensagem.lida,
        created_at=mensagem.created_at.isoformat()
    )
