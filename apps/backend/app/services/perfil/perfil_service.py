"""
Service para gerenciar perfil do cliente
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional

from app.db.models.cliente import Cliente
from app.services.auth.auth_service import AuthService

logger = logging.getLogger(__name__)


class PerfilService:
    """Service para gerenciar perfil do cliente"""
    
    @staticmethod
    def editar_perfil(
        db: Session,
        cliente_id: int,
        nome: Optional[str] = None,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        senha_confirmacao: str = None
    ) -> Cliente:
        """
        Edita perfil do cliente com validação de senha
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            nome: Novo nome (opcional)
            telefone: Novo telefone (opcional)
            email: Novo email (opcional)
            senha_confirmacao: Senha para confirmar alteração
            
        Returns:
            Cliente: Cliente atualizado
            
        Raises:
            ValueError: Se senha incorreta ou email já existe
        """
        # Buscar cliente
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if not cliente:
            raise ValueError("Cliente não encontrado")
        
        # Validar senha
        if not senha_confirmacao:
            raise ValueError("Senha de confirmação é obrigatória")
        
        if not AuthService.verificar_senha(senha_confirmacao, cliente.senha_hash):
            raise ValueError("Senha incorreta")
        
        # Validar email único se estiver sendo alterado
        if email and email != cliente.email:
            email_existente = db.query(Cliente).filter(
                Cliente.email == email,
                Cliente.id != cliente_id
            ).first()
            
            if email_existente:
                raise ValueError("Email já está em uso por outro cliente")
            
            cliente.email = email
            logger.info(f"Email do cliente {cliente_id} alterado para {email}")
        
        # Atualizar campos
        if nome:
            cliente.nome = nome
            logger.info(f"Nome do cliente {cliente_id} alterado para {nome}")
        
        if telefone is not None:  # Permite string vazia para remover telefone
            cliente.telefone = telefone if telefone else None
            logger.info(f"Telefone do cliente {cliente_id} alterado")
        
        cliente.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(cliente)
        
        logger.info(f"Perfil do cliente {cliente_id} atualizado com sucesso")
        
        return cliente
