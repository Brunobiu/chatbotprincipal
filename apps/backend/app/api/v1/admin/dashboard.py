"""
Endpoints do dashboard administrativo.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta

from app.db.session import get_db
from app.db.models.cliente import Cliente, ClienteStatus
from app.api.v1.admin.auth import get_current_admin

router = APIRouter()


# Pydantic Models
class DashboardMetrics(BaseModel):
    total_clientes: int
    clientes_ativos: int
    clientes_suspensos: int
    clientes_pendentes: int
    novos_hoje: int
    novos_semana: int
    novos_mes: int
    cancelamentos_mes: int
    mrr: float
    ticket_medio: float
    taxa_conversao: float


class VendaDiaria(BaseModel):
    data: str
    quantidade: int
    receita: float


class ReceitaMensal(BaseModel):
    mes: str
    receita: float


class ClienteRecente(BaseModel):
    id: int
    nome: str
    email: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    metrics: DashboardMetrics
    vendas_diarias: List[VendaDiaria]
    receita_mensal: List[ReceitaMensal]
    clientes_recentes: List[ClienteRecente]


@router.get("/metrics", response_model=DashboardResponse)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Retorna métricas principais do dashboard administrativo.
    
    Inclui:
    - Total de clientes por status
    - Novos clientes (hoje, semana, mês)
    - Cancelamentos do mês
    - MRR (Monthly Recurring Revenue)
    - Ticket médio
    - Taxa de conversão
    - Gráfico de vendas diárias (últimos 30 dias)
    - Gráfico de receita mensal (últimos 6 meses)
    - Lista dos últimos 5 clientes cadastrados
    """
    
    # Datas de referência
    hoje = datetime.utcnow().date()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = hoje.replace(day=1)
    trinta_dias_atras = hoje - timedelta(days=30)
    seis_meses_atras = hoje - timedelta(days=180)
    
    # Total de clientes por status
    total_clientes = db.query(func.count(Cliente.id)).scalar() or 0
    clientes_ativos = db.query(func.count(Cliente.id)).filter(
        Cliente.status == ClienteStatus.ATIVO
    ).scalar() or 0
    clientes_suspensos = db.query(func.count(Cliente.id)).filter(
        Cliente.status == ClienteStatus.SUSPENSO
    ).scalar() or 0
    clientes_pendentes = db.query(func.count(Cliente.id)).filter(
        Cliente.status == ClienteStatus.PENDENTE
    ).scalar() or 0
    
    # Novos clientes
    novos_hoje = db.query(func.count(Cliente.id)).filter(
        func.date(Cliente.created_at) == hoje
    ).scalar() or 0
    
    novos_semana = db.query(func.count(Cliente.id)).filter(
        func.date(Cliente.created_at) >= inicio_semana
    ).scalar() or 0
    
    novos_mes = db.query(func.count(Cliente.id)).filter(
        func.date(Cliente.created_at) >= inicio_mes
    ).scalar() or 0
    
    # Cancelamentos do mês (clientes que ficaram suspensos/inativos no mês)
    cancelamentos_mes = db.query(func.count(Cliente.id)).filter(
        and_(
            Cliente.status.in_([ClienteStatus.SUSPENSO, ClienteStatus.INATIVO]),
            func.date(Cliente.updated_at) >= inicio_mes
        )
    ).scalar() or 0
    
    # MRR (assumindo R$ 2,00 por cliente ativo - ajustar conforme seu plano)
    # TODO: Buscar valor real do plano quando tiver tabela de planos
    preco_mensal = 2.00
    mrr = clientes_ativos * preco_mensal
    
    # Ticket médio
    ticket_medio = preco_mensal if clientes_ativos > 0 else 0.0
    
    # Taxa de conversão (clientes ativos / total de clientes)
    taxa_conversao = (clientes_ativos / total_clientes * 100) if total_clientes > 0 else 0.0
    
    # Vendas diárias (últimos 30 dias)
    vendas_diarias_query = db.query(
        func.date(Cliente.created_at).label('data'),
        func.count(Cliente.id).label('quantidade')
    ).filter(
        and_(
            func.date(Cliente.created_at) >= trinta_dias_atras,
            Cliente.status == ClienteStatus.ATIVO
        )
    ).group_by(
        func.date(Cliente.created_at)
    ).order_by(
        func.date(Cliente.created_at)
    ).all()
    
    vendas_diarias = [
        VendaDiaria(
            data=str(venda.data),
            quantidade=venda.quantidade,
            receita=venda.quantidade * preco_mensal
        )
        for venda in vendas_diarias_query
    ]
    
    # Receita mensal (últimos 6 meses)
    receita_mensal_query = db.query(
        extract('year', Cliente.created_at).label('ano'),
        extract('month', Cliente.created_at).label('mes'),
        func.count(Cliente.id).label('quantidade')
    ).filter(
        and_(
            func.date(Cliente.created_at) >= seis_meses_atras,
            Cliente.status == ClienteStatus.ATIVO
        )
    ).group_by(
        extract('year', Cliente.created_at),
        extract('month', Cliente.created_at)
    ).order_by(
        extract('year', Cliente.created_at),
        extract('month', Cliente.created_at)
    ).all()
    
    receita_mensal = [
        ReceitaMensal(
            mes=f"{int(rec.ano)}-{int(rec.mes):02d}",
            receita=rec.quantidade * preco_mensal
        )
        for rec in receita_mensal_query
    ]
    
    # Últimos 5 clientes cadastrados
    clientes_recentes = db.query(Cliente).order_by(
        Cliente.created_at.desc()
    ).limit(5).all()
    
    return DashboardResponse(
        metrics=DashboardMetrics(
            total_clientes=total_clientes,
            clientes_ativos=clientes_ativos,
            clientes_suspensos=clientes_suspensos,
            clientes_pendentes=clientes_pendentes,
            novos_hoje=novos_hoje,
            novos_semana=novos_semana,
            novos_mes=novos_mes,
            cancelamentos_mes=cancelamentos_mes,
            mrr=mrr,
            ticket_medio=ticket_medio,
            taxa_conversao=round(taxa_conversao, 2)
        ),
        vendas_diarias=vendas_diarias,
        receita_mensal=receita_mensal,
        clientes_recentes=[ClienteRecente.from_orm(c) for c in clientes_recentes]
    )
