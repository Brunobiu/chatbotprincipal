"""
Endpoints para admin usar própria ferramenta
Task 12.4
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.admin import Admin
from app.core.security import get_current_admin
from app.services.admin_cliente.admin_cliente_service import AdminClienteService


router = APIRouter()


@router.get("/acessar")
def acessar_minha_ferramenta(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Gera token para admin acessar como cliente
    
    Returns:
        Token JWT e dados do cliente admin
    """
    try:
        token_data = AdminClienteService.obter_token_cliente_admin(db, current_admin)
        return token_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar token: {str(e)}")


@router.get("/status")
def status_minha_ferramenta(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Verifica se admin já tem cliente criado
    
    Returns:
        Status do cliente admin
    """
    cliente = AdminClienteService.obter_cliente_admin(db, current_admin)
    
    if not cliente:
        return {
            "existe": False,
            "mensagem": "Cliente admin ainda não foi criado"
        }
    
    return {
        "existe": True,
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "email": cliente.email,
            "status": cliente.status.value,
            "created_at": cliente.created_at.isoformat()
        }
    }
