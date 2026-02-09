"""
Rotas de Analytics
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.db.session import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/resumo")
def get_resumo(
    dias: int = 30,
    db: Session = Depends(get_db)
):
    """Retorna resumo geral"""
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=dias)
    
    return AnalyticsService.get_resumo_geral(db, data_inicio, data_fim)


@router.get("/crescimento-clientes")
def get_crescimento_clientes(
    meses: int = 6,
    db: Session = Depends(get_db)
):
    """Retorna dados para gráfico de crescimento"""
    return AnalyticsService.get_crescimento_clientes(db, meses)


@router.get("/receita-mensal")
def get_receita_mensal(
    meses: int = 6,
    db: Session = Depends(get_db)
):
    """Retorna dados para gráfico de receita"""
    return AnalyticsService.get_receita_mensal(db, meses)


@router.get("/distribuicao-planos")
def get_distribuicao_planos(db: Session = Depends(get_db)):
    """Retorna distribuição de clientes por plano"""
    return AnalyticsService.get_distribuicao_planos(db)


@router.post("/calcular-metricas")
def calcular_metricas(db: Session = Depends(get_db)):
    """Força cálculo de métricas de hoje"""
    metrica = AnalyticsService.calcular_metricas_diarias(db)
    return {
        'message': 'Métricas calculadas',
        'data': metrica.data.isoformat(),
        'total_clientes': metrica.total_clientes
    }
