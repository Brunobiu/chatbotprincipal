"""
Endpoints de Monitoramento de Sistema
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.admin import Admin
from app.services.sistema import SistemaService


router = APIRouter()


@router.get("/saude")
async def obter_saude_sistema(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retorna status de saúde de todos os serviços
    - PostgreSQL
    - Redis
    - ChromaDB
    - Evolution API
    - OpenAI
    """
    return await SistemaService.obter_saude_completa(db)


@router.get("/metricas")
def obter_metricas_sistema(
    admin: Admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Retorna métricas de uso do sistema
    - CPU
    - Memória
    - Disco
    - Performance (tempo de resposta, requests/min, erros/min)
    """
    return SistemaService.obter_metricas_sistema()
