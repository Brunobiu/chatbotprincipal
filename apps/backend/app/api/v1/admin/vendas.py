"""
Endpoints de Gestão de Vendas e Assinaturas
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.admin import Admin
from app.services.vendas import VendaService


router = APIRouter()


@router.get("/transacoes")
def listar_transacoes(
    status: Optional[str] = Query(None, description="Filtrar por status (succeeded, pending, failed)"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    limite: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Lista todas as transações com filtros opcionais
    """
    # Converter strings de data para datetime
    dt_inicio = None
    dt_fim = None
    
    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        except ValueError:
            pass
    
    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
        except ValueError:
            pass
    
    return VendaService.listar_transacoes(
        db=db,
        status=status,
        data_inicio=dt_inicio,
        data_fim=dt_fim,
        cliente_id=cliente_id,
        limite=limite,
        offset=offset
    )


@router.get("/assinaturas")
def listar_assinaturas(
    status: Optional[str] = Query(None, description="Filtrar por status (active, canceled, past_due)"),
    limite: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Lista todas as assinaturas com filtros opcionais
    """
    return VendaService.listar_assinaturas(
        db=db,
        status=status,
        limite=limite,
        offset=offset
    )


@router.post("/assinaturas/{assinatura_id}/cancelar")
def cancelar_assinatura(
    assinatura_id: str,
    imediato: bool = Query(False, description="Cancelar imediatamente ou no fim do período"),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Cancela uma assinatura
    """
    return VendaService.cancelar_assinatura(
        db=db,
        assinatura_id=assinatura_id,
        imediato=imediato
    )


@router.post("/assinaturas/{assinatura_id}/reativar")
def reativar_assinatura(
    assinatura_id: str,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Reativa uma assinatura cancelada (antes do fim do período)
    """
    return VendaService.reativar_assinatura(
        db=db,
        assinatura_id=assinatura_id
    )


@router.post("/transacoes/{charge_id}/reembolsar")
def reembolsar_transacao(
    charge_id: str,
    valor: Optional[float] = Query(None, description="Valor do reembolso (deixe vazio para reembolso total)"),
    motivo: Optional[str] = Query(None, description="Motivo do reembolso"),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Reembolsa uma transação (total ou parcial)
    """
    return VendaService.reembolsar_transacao(
        db=db,
        charge_id=charge_id,
        valor=valor,
        motivo=motivo
    )


@router.get("/clientes/{cliente_id}/historico")
def obter_historico_cliente(
    cliente_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtém histórico completo de pagamentos de um cliente
    """
    return VendaService.obter_historico_cliente(
        db=db,
        cliente_id=cliente_id
    )
