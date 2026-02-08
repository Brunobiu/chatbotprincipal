from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.admin import Admin
from app.services.notificacoes.notificacao_service import NotificacaoService


router = APIRouter()


# ==================== SCHEMAS ====================

class NotificacaoResponse(BaseModel):
    id: int
    tipo: str
    titulo: str
    mensagem: str
    prioridade: str
    lida: bool
    data: dict
    created_at: str
    
    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.get("")
def listar_notificacoes(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    apenas_nao_lidas: bool = Query(False),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista notificações do admin"""
    service = NotificacaoService(db)
    notificacoes, total = service.listar_notificacoes(
        admin_id=admin.id,
        limit=limit,
        offset=offset,
        apenas_nao_lidas=apenas_nao_lidas
    )
    
    return {
        "notificacoes": [
            NotificacaoResponse(
                id=n.id,
                tipo=n.tipo,
                titulo=n.titulo,
                mensagem=n.mensagem,
                prioridade=n.prioridade,
                lida=n.lida,
                data=n.data or {},
                created_at=n.created_at.isoformat()
            ) for n in notificacoes
        ],
        "total": total,
        "nao_lidas": service.contar_nao_lidas(admin.id),
        "limit": limit,
        "offset": offset
    }


@router.get("/nao-lidas/count")
def contar_nao_lidas(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Conta notificações não lidas"""
    service = NotificacaoService(db)
    count = service.contar_nao_lidas(admin.id)
    
    return {"count": count}


@router.put("/{notificacao_id}/ler")
def marcar_como_lida(
    notificacao_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Marca uma notificação como lida"""
    service = NotificacaoService(db)
    sucesso = service.marcar_como_lida(notificacao_id, admin.id)
    
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    return {"message": "Notificação marcada como lida"}


@router.put("/ler-todas")
def marcar_todas_como_lidas(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Marca todas as notificações como lidas"""
    service = NotificacaoService(db)
    count = service.marcar_todas_como_lidas(admin.id)
    
    return {
        "message": f"{count} notificações marcadas como lidas",
        "count": count
    }
