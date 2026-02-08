from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.admin import Admin
from app.services.relatorios.relatorio_service import RelatorioService


router = APIRouter()


# ==================== ENDPOINTS ====================

@router.get("/clientes")
def relatorio_clientes(
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Gera relatório de clientes"""
    service = RelatorioService(db)
    
    inicio = datetime.fromisoformat(data_inicio) if data_inicio else None
    fim = datetime.fromisoformat(data_fim) if data_fim else None
    
    relatorio = service.relatorio_clientes(
        data_inicio=inicio,
        data_fim=fim,
        status=status
    )
    
    return JSONResponse(content=relatorio)


@router.get("/uso-openai")
def relatorio_uso_openai(
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    cliente_id: Optional[int] = Query(None),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Gera relatório de uso OpenAI"""
    service = RelatorioService(db)
    
    inicio = datetime.fromisoformat(data_inicio) if data_inicio else None
    fim = datetime.fromisoformat(data_fim) if data_fim else None
    
    relatorio = service.relatorio_uso_openai(
        data_inicio=inicio,
        data_fim=fim,
        cliente_id=cliente_id
    )
    
    return JSONResponse(content=relatorio)


@router.get("/tickets")
def relatorio_tickets(
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Gera relatório de tickets"""
    service = RelatorioService(db)
    
    inicio = datetime.fromisoformat(data_inicio) if data_inicio else None
    fim = datetime.fromisoformat(data_fim) if data_fim else None
    
    relatorio = service.relatorio_tickets(
        data_inicio=inicio,
        data_fim=fim,
        status=status
    )
    
    return JSONResponse(content=relatorio)


@router.get("/conversas")
def relatorio_conversas(
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    cliente_id: Optional[int] = Query(None),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Gera relatório de conversas"""
    service = RelatorioService(db)
    
    inicio = datetime.fromisoformat(data_inicio) if data_inicio else None
    fim = datetime.fromisoformat(data_fim) if data_fim else None
    
    relatorio = service.relatorio_conversas(
        data_inicio=inicio,
        data_fim=fim,
        cliente_id=cliente_id
    )
    
    return JSONResponse(content=relatorio)


@router.get("/geral")
def relatorio_geral(
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Gera relatório geral do sistema"""
    service = RelatorioService(db)
    
    inicio = datetime.fromisoformat(data_inicio) if data_inicio else None
    fim = datetime.fromisoformat(data_fim) if data_fim else None
    
    relatorio = service.relatorio_geral(
        data_inicio=inicio,
        data_fim=fim
    )
    
    return JSONResponse(content=relatorio)
