from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.admin import Admin
from app.db.models.cliente import Cliente, ClienteStatus
from app.services.auth.auth_service import AuthService


router = APIRouter()


# ==================== SCHEMAS ====================

class AcessarFerramentaResponse(BaseModel):
    access_token: str
    cliente_id: int
    email: str
    nome: str


# ==================== ENDPOINTS ====================

@router.get("/acessar", response_model=AcessarFerramentaResponse)
def acessar_ferramenta(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Retorna token de acesso para o admin usar a ferramenta como cliente.
    Se o admin não tiver um cliente vinculado, cria automaticamente.
    """
    
    # Verificar se admin já tem cliente vinculado
    cliente = None
    if admin.cliente_especial_id:
        cliente = db.query(Cliente).filter(
            Cliente.id == admin.cliente_especial_id
        ).first()
    
    # Se não encontrou, tentar buscar por email
    if not cliente:
        email_admin = f"admin.{admin.id}@sistema.interno"
        cliente = db.query(Cliente).filter(
            Cliente.email == email_admin
        ).first()
        
        # Se encontrou, vincular ao admin
        if cliente:
            admin.cliente_especial_id = cliente.id
            db.commit()
    
    # Se ainda não tem cliente, criar
    if not cliente:
        cliente = Cliente(
            nome=f"{admin.nome} (Admin)",
            email=f"admin.{admin.id}@sistema.interno",
            senha_hash="ADMIN_ACCOUNT_NO_PASSWORD",  # Não precisa de senha
            status=ClienteStatus.ATIVO,
            stripe_customer_id=None,  # Sem cobrança
            stripe_subscription_id=None,
            stripe_status="active"  # Sempre ativo
        )
        
        db.add(cliente)
        db.flush()
        
        # Vincular cliente ao admin
        admin.cliente_especial_id = cliente.id
        db.commit()
        db.refresh(cliente)
    
    # Gerar token
    token = AuthService.criar_token_acesso(cliente.id, cliente.email)
    
    return AcessarFerramentaResponse(
        access_token=token,
        cliente_id=cliente.id,
        email=cliente.email,
        nome=cliente.nome
    )
