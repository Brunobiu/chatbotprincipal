"""
Rotas de monitoramento de uso OpenAI para admin
FASE 16.4 - Monitoramento de Uso (Créditos OpenAI)
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.v1.admin.auth import get_current_admin
from app.services.uso import UsoOpenAIService


router = APIRouter()


# Schemas
class TopGastador(BaseModel):
    """Schema para top gastador"""
    cliente_id: int
    nome: str
    email: str
    tokens_total: int
    custo_total: float
    mensagens_total: int
    custo_medio_por_mensagem: float


class HistoricoUso(BaseModel):
    """Schema para histórico de uso"""
    data: str
    tokens_prompt: int
    tokens_completion: int
    tokens_total: int
    custo_estimado: float
    mensagens_processadas: int
    modelo: str


class Alerta(BaseModel):
    """Schema para alerta de uso"""
    cliente_id: int
    nome: str
    email: str
    custo_hoje: float
    tokens_hoje: int
    mensagens_hoje: int
    threshold: float
    percentual_acima: float


class ResumoGeral(BaseModel):
    """Schema para resumo geral"""
    periodo_dias: int
    tokens_total: int
    custo_total: float
    mensagens_total: int
    clientes_ativos: int
    custo_hoje: float
    custo_medio_por_mensagem: float


@router.get("/uso/resumo", response_model=ResumoGeral)
def obter_resumo_geral(
    dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Retorna resumo geral de uso de todos os clientes
    
    Query params:
    - dias: Período em dias (padrão: 30)
    """
    resumo = UsoOpenAIService.obter_resumo_geral(db, dias)
    return resumo


@router.get("/uso/top-gastadores", response_model=List[TopGastador])
def obter_top_gastadores(
    limite: int = Query(10, ge=1, le=100),
    dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Retorna top clientes que mais gastam
    
    Query params:
    - limite: Número de clientes (padrão: 10)
    - dias: Período em dias (padrão: 30)
    """
    top = UsoOpenAIService.obter_top_gastadores(db, limite, dias)
    return top


@router.get("/uso/cliente/{cliente_id}", response_model=List[HistoricoUso])
def obter_historico_cliente(
    cliente_id: int,
    dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Retorna histórico de uso de um cliente específico
    
    Path params:
    - cliente_id: ID do cliente
    
    Query params:
    - dias: Período em dias (padrão: 30)
    """
    historico = UsoOpenAIService.obter_historico_cliente(db, cliente_id, dias)
    return historico


@router.get("/uso/alertas", response_model=List[Alerta])
def obter_alertas(
    threshold: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Retorna clientes que ultrapassaram o threshold de custo hoje
    
    Query params:
    - threshold: Limite de custo diário em dólares (padrão: $10)
    """
    alertas = UsoOpenAIService.obter_alertas(db, threshold)
    return alertas
