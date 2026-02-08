from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.admin import Admin
from app.services.tickets.ticket_service import TicketService


router = APIRouter()


# ==================== SCHEMAS ====================

class AnexoSchema(BaseModel):
    nome: str
    url: str
    tipo: str
    tamanho: int


class AdicionarMensagemRequest(BaseModel):
    mensagem: str = Field(..., min_length=1)
    anexos: Optional[List[AnexoSchema]] = None


class AtualizarStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(aberto|em_andamento|aguardando_cliente|resolvido|fechado)$")


class AtribuirTicketRequest(BaseModel):
    admin_id: int


class ClienteSimples(BaseModel):
    id: int
    nome: str
    email: str
    
    class Config:
        from_attributes = True


class AdminSimples(BaseModel):
    id: int
    nome: str
    email: str
    
    class Config:
        from_attributes = True


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
    cliente: ClienteSimples
    assunto: str
    status: str
    prioridade: str
    categoria: Optional[CategoriaResponse]
    atribuido_admin: Optional[AdminSimples]
    ia_respondeu: bool
    confianca_ia: Optional[float]
    created_at: str
    updated_at: str
    resolvido_em: Optional[str]
    mensagens: Optional[List[MensagemResponse]] = None
    
    class Config:
        from_attributes = True


class ListaTicketsResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
    limit: int
    offset: int


class EstatisticasResponse(BaseModel):
    total: int
    abertos: int
    em_andamento: int
    aguardando_cliente: int
    resolvidos: int
    nao_lidos: int


# ==================== ENDPOINTS ====================

@router.get("/estatisticas", response_model=EstatisticasResponse)
def obter_estatisticas(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de tickets"""
    service = TicketService(db)
    stats = service.obter_estatisticas_admin()
    return EstatisticasResponse(**stats)


@router.get("/", response_model=ListaTicketsResponse)
def listar_tickets(
    status: Optional[str] = None,
    categoria_id: Optional[int] = None,
    prioridade: Optional[str] = None,
    busca: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista todos os tickets (admin)"""
    service = TicketService(db)
    tickets, total = service.listar_tickets_admin(
        status=status,
        categoria_id=categoria_id,
        prioridade=prioridade,
        busca=busca,
        limit=limit,
        offset=offset
    )
    
    return ListaTicketsResponse(
        tickets=[
            TicketResponse(
                id=t.id,
                cliente=ClienteSimples.from_orm(t.cliente),
                assunto=t.assunto,
                status=t.status,
                prioridade=t.prioridade,
                categoria=CategoriaResponse.from_orm(t.categoria) if t.categoria else None,
                atribuido_admin=AdminSimples.from_orm(t.atribuido_admin) if t.atribuido_admin else None,
                ia_respondeu=t.ia_respondeu,
                confianca_ia=t.confianca_ia,
                created_at=t.created_at.isoformat(),
                updated_at=t.updated_at.isoformat(),
                resolvido_em=t.resolvido_em.isoformat() if t.resolvido_em else None,
                mensagens=None
            ) for t in tickets
        ],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
def obter_ticket(
    ticket_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Obtém detalhes de um ticket"""
    service = TicketService(db)
    ticket = service.obter_ticket_admin(ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket não encontrado"
        )
    
    # Marcar mensagens como lidas
    service.marcar_mensagens_lidas(ticket_id, "admin")
    
    return TicketResponse(
        id=ticket.id,
        cliente=ClienteSimples.from_orm(ticket.cliente),
        assunto=ticket.assunto,
        status=ticket.status,
        prioridade=ticket.prioridade,
        categoria=CategoriaResponse.from_orm(ticket.categoria) if ticket.categoria else None,
        atribuido_admin=AdminSimples.from_orm(ticket.atribuido_admin) if ticket.atribuido_admin else None,
        ia_respondeu=ticket.ia_respondeu,
        confianca_ia=ticket.confianca_ia,
        created_at=ticket.created_at.isoformat(),
        updated_at=ticket.updated_at.isoformat(),
        resolvido_em=ticket.resolvido_em.isoformat() if ticket.resolvido_em else None,
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
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin adiciona mensagem ao ticket"""
    service = TicketService(db)
    
    anexos = [anexo.dict() for anexo in request.anexos] if request.anexos else None
    
    mensagem = service.adicionar_mensagem_admin(
        ticket_id=ticket_id,
        admin_id=admin.id,
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


@router.put("/{ticket_id}/status", response_model=TicketResponse)
def atualizar_status(
    ticket_id: int,
    request: AtualizarStatusRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Atualiza status do ticket"""
    service = TicketService(db)
    ticket = service.atualizar_status_ticket(
        ticket_id=ticket_id,
        status=request.status,
        admin_id=admin.id
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket não encontrado"
        )
    
    return TicketResponse(
        id=ticket.id,
        cliente=ClienteSimples.from_orm(ticket.cliente),
        assunto=ticket.assunto,
        status=ticket.status,
        prioridade=ticket.prioridade,
        categoria=CategoriaResponse.from_orm(ticket.categoria) if ticket.categoria else None,
        atribuido_admin=AdminSimples.from_orm(ticket.atribuido_admin) if ticket.atribuido_admin else None,
        ia_respondeu=ticket.ia_respondeu,
        confianca_ia=ticket.confianca_ia,
        created_at=ticket.created_at.isoformat(),
        updated_at=ticket.updated_at.isoformat(),
        resolvido_em=ticket.resolvido_em.isoformat() if ticket.resolvido_em else None,
        mensagens=None
    )


@router.post("/{ticket_id}/atribuir", response_model=TicketResponse)
def atribuir_ticket(
    ticket_id: int,
    request: AtribuirTicketRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Atribui ticket a um admin"""
    service = TicketService(db)
    ticket = service.atribuir_ticket(
        ticket_id=ticket_id,
        admin_id=request.admin_id
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket não encontrado"
        )
    
    return TicketResponse(
        id=ticket.id,
        cliente=ClienteSimples.from_orm(ticket.cliente),
        assunto=ticket.assunto,
        status=ticket.status,
        prioridade=ticket.prioridade,
        categoria=CategoriaResponse.from_orm(ticket.categoria) if ticket.categoria else None,
        atribuido_admin=AdminSimples.from_orm(ticket.atribuido_admin) if ticket.atribuido_admin else None,
        ia_respondeu=ticket.ia_respondeu,
        confianca_ia=ticket.confianca_ia,
        created_at=ticket.created_at.isoformat(),
        updated_at=ticket.updated_at.isoformat(),
        resolvido_em=ticket.resolvido_em.isoformat() if ticket.resolvido_em else None,
        mensagens=None
    )
