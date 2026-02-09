"""
AdminClienteService - Serviço para admin usar própria ferramenta
Task 12.2
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from jose import jwt

from app.db.models.cliente import Cliente, ClienteStatus
from app.db.models.admin import Admin
from app.core.security import get_password_hash
from app.core.config import settings


class AdminClienteService:
    """Serviço para gerenciar cliente do admin"""
    
    @staticmethod
    def criar_cliente_admin(db: Session, admin: Admin) -> Cliente:
        """
        Cria ou retorna cliente vinculado ao admin
        
        Cliente admin:
        - Status sempre ATIVO
        - Sem cobrança (stripe_customer_id = None)
        - Email: admin.email + "+ferramenta"
        - Senha: gerada automaticamente
        """
        # Verificar se já existe cliente admin para este admin
        cliente_existente = db.query(Cliente).filter(
            Cliente.admin_vinculado_id == admin.id,
            Cliente.eh_cliente_admin == 1
        ).first()
        
        if cliente_existente:
            return cliente_existente
        
        # Criar novo cliente admin
        email_cliente = f"{admin.email.split('@')[0]}+ferramenta@{admin.email.split('@')[1]}"
        senha_gerada = f"admin_{admin.id}_ferramenta"  # Senha automática
        
        cliente = Cliente(
            nome=f"{admin.nome} (Ferramenta)",
            nome_empresa=admin.nome_empresa or admin.nome,
            email=email_cliente,
            telefone=admin.telefone,
            senha_hash=get_password_hash(senha_gerada),
            status=ClienteStatus.ATIVO,
            eh_cliente_admin=1,
            admin_vinculado_id=admin.id,
            # Sem Stripe - não cobra
            stripe_customer_id=None,
            stripe_subscription_id=None,
            stripe_status=None
        )
        
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        
        return cliente
    
    @staticmethod
    def obter_token_cliente_admin(db: Session, admin: Admin) -> dict:
        """
        Gera token JWT para admin acessar como cliente
        
        Returns:
            dict com token e dados do cliente
        """
        # Criar ou obter cliente admin
        cliente = AdminClienteService.criar_cliente_admin(db, admin)
        
        # Gerar token JWT
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + access_token_expires
        
        to_encode = {
            "sub": str(cliente.id),
            "email": cliente.email,
            "tipo": "cliente",
            "exp": expire
        }
        
        access_token = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "cliente": {
                "id": cliente.id,
                "nome": cliente.nome,
                "email": cliente.email,
                "status": cliente.status.value,
                "eh_cliente_admin": True
            }
        }
    
    @staticmethod
    def obter_cliente_admin(db: Session, admin: Admin) -> Optional[Cliente]:
        """Retorna cliente admin se existir"""
        return db.query(Cliente).filter(
            Cliente.admin_vinculado_id == admin.id,
            Cliente.eh_cliente_admin == 1
        ).first()
    
    @staticmethod
    def eh_cliente_admin(cliente: Cliente) -> bool:
        """Verifica se cliente é admin usando ferramenta"""
        return cliente.eh_cliente_admin == 1
