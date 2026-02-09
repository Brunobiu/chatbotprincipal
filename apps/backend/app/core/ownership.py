"""
Módulo de verificação de ownership (FASE 2)
Garante que usuários só acessem seus próprios recursos
"""
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.cliente import Cliente
from app.db.models.conversa import Conversa
from app.db.models.instancia_whatsapp import InstanciaWhatsApp
from app.db.models.conhecimento import Conhecimento
from app.db.models.configuracao_bot import ConfiguracaoBot
from app.db.models.ticket import Ticket
from app.db.models.agendamento import Agendamento


class OwnershipVerifier:
    """
    Validador de ownership para garantir isolamento de usuários
    
    FASE 2 - Proteção contra IDOR (Insecure Direct Object Reference)
    """
    
    @staticmethod
    def verify_ownership(
        db: Session,
        model,
        resource_id: int,
        cliente: Cliente
    ):
        """
        Método genérico para verificar ownership de qualquer recurso
        
        Args:
            db: Sessão do banco
            model: Modelo SQLAlchemy (Conversa, Ticket, etc)
            resource_id: ID do recurso
            cliente: Cliente autenticado
            
        Returns:
            Recurso se pertence ao cliente
            
        Raises:
            HTTPException 404: Se não encontrar ou não pertencer
        """
        resource = db.query(model).filter(
            model.id == resource_id,
            model.cliente_id == cliente.id
        ).first()
        
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{model.__name__} não encontrado"
            )
        
        return resource
    
    @staticmethod
    def verify_conversa_ownership(
        db: Session,
        conversa_id: int,
        cliente: Cliente
    ) -> Conversa:
        """
        Verifica se a conversa pertence ao cliente
        
        Args:
            db: Sessão do banco
            conversa_id: ID da conversa
            cliente: Cliente autenticado
            
        Returns:
            Conversa se pertence ao cliente
            
        Raises:
            HTTPException 404: Se não encontrar ou não pertencer
        """
        conversa = db.query(Conversa).filter(
            Conversa.id == conversa_id,
            Conversa.cliente_id == cliente.id
        ).first()
        
        if not conversa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversa não encontrada"
            )
        
        return conversa
    
    @staticmethod
    def verify_instancia_ownership(
        db: Session,
        instancia_id: int,
        cliente: Cliente
    ) -> InstanciaWhatsApp:
        """
        Verifica se a instância WhatsApp pertence ao cliente
        
        Args:
            db: Sessão do banco
            instancia_id: ID da instância
            cliente: Cliente autenticado
            
        Returns:
            InstanciaWhatsApp se pertence ao cliente
            
        Raises:
            HTTPException 404: Se não encontrar ou não pertencer
        """
        instancia = db.query(InstanciaWhatsApp).filter(
            InstanciaWhatsApp.id == instancia_id,
            InstanciaWhatsApp.cliente_id == cliente.id
        ).first()
        
        if not instancia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instância não encontrada"
            )
        
        return instancia
    
    @staticmethod
    def verify_conhecimento_ownership(
        db: Session,
        cliente: Cliente
    ) -> Conhecimento:
        """
        Verifica e retorna o conhecimento do cliente
        
        Args:
            db: Sessão do banco
            cliente: Cliente autenticado
            
        Returns:
            Conhecimento do cliente
            
        Raises:
            HTTPException 404: Se não encontrar
        """
        conhecimento = db.query(Conhecimento).filter(
            Conhecimento.cliente_id == cliente.id
        ).first()
        
        if not conhecimento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conhecimento não encontrado"
            )
        
        return conhecimento
    
    @staticmethod
    def verify_configuracao_ownership(
        db: Session,
        cliente: Cliente
    ) -> ConfiguracaoBot:
        """
        Verifica e retorna a configuração do bot do cliente
        
        Args:
            db: Sessão do banco
            cliente: Cliente autenticado
            
        Returns:
            ConfiguracaoBot do cliente
            
        Raises:
            HTTPException 404: Se não encontrar
        """
        config = db.query(ConfiguracaoBot).filter(
            ConfiguracaoBot.cliente_id == cliente.id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuração não encontrada"
            )
        
        return config
    
    @staticmethod
    def verify_ticket_ownership(
        db: Session,
        ticket_id: int,
        cliente: Cliente
    ) -> Ticket:
        """
        Verifica se o ticket pertence ao cliente
        
        Args:
            db: Sessão do banco
            ticket_id: ID do ticket
            cliente: Cliente autenticado
            
        Returns:
            Ticket se pertence ao cliente
            
        Raises:
            HTTPException 404: Se não encontrar ou não pertencer
        """
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.cliente_id == cliente.id
        ).first()
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket não encontrado"
            )
        
        return ticket
    
    @staticmethod
    def verify_agendamento_ownership(
        db: Session,
        agendamento_id: int,
        cliente: Cliente
    ) -> Agendamento:
        """
        Verifica se o agendamento pertence ao cliente
        
        Args:
            db: Sessão do banco
            agendamento_id: ID do agendamento
            cliente: Cliente autenticado
            
        Returns:
            Agendamento se pertence ao cliente
            
        Raises:
            HTTPException 404: Se não encontrar ou não pertencer
        """
        agendamento = db.query(Agendamento).filter(
            Agendamento.id == agendamento_id,
            Agendamento.cliente_id == cliente.id
        ).first()
        
        if not agendamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agendamento não encontrado"
            )
        
        return agendamento
    
    @staticmethod
    def get_cliente_conversas(
        db: Session,
        cliente: Cliente,
        skip: int = 0,
        limit: int = 100
    ):
        """
        Retorna apenas conversas do cliente autenticado
        
        Args:
            db: Sessão do banco
            cliente: Cliente autenticado
            skip: Offset para paginação
            limit: Limite de resultados
            
        Returns:
            Lista de conversas do cliente
        """
        return db.query(Conversa).filter(
            Conversa.cliente_id == cliente.id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_cliente_tickets(
        db: Session,
        cliente: Cliente,
        skip: int = 0,
        limit: int = 100
    ):
        """
        Retorna apenas tickets do cliente autenticado
        
        Args:
            db: Sessão do banco
            cliente: Cliente autenticado
            skip: Offset para paginação
            limit: Limite de resultados
            
        Returns:
            Lista de tickets do cliente
        """
        return db.query(Ticket).filter(
            Ticket.cliente_id == cliente.id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_cliente_agendamentos(
        db: Session,
        cliente: Cliente,
        skip: int = 0,
        limit: int = 100
    ):
        """
        Retorna apenas agendamentos do cliente autenticado
        
        Args:
            db: Sessão do banco
            cliente: Cliente autenticado
            skip: Offset para paginação
            limit: Limite de resultados
            
        Returns:
            Lista de agendamentos do cliente
        """
        return db.query(Agendamento).filter(
            Agendamento.cliente_id == cliente.id
        ).offset(skip).limit(limit).all()


# Funções helper para uso direto
def verify_conversa_ownership(db: Session, conversa_id: int, cliente: Cliente) -> Conversa:
    """Helper function para verificar ownership de conversa"""
    return OwnershipVerifier.verify_conversa_ownership(db, conversa_id, cliente)


def verify_instancia_ownership(db: Session, instancia_id: int, cliente: Cliente) -> InstanciaWhatsApp:
    """Helper function para verificar ownership de instância"""
    return OwnershipVerifier.verify_instancia_ownership(db, instancia_id, cliente)


def verify_ticket_ownership(db: Session, ticket_id: int, cliente: Cliente) -> Ticket:
    """Helper function para verificar ownership de ticket"""
    return OwnershipVerifier.verify_ticket_ownership(db, ticket_id, cliente)


def verify_agendamento_ownership(db: Session, agendamento_id: int, cliente: Cliente) -> Agendamento:
    """Helper function para verificar ownership de agendamento"""
    return OwnershipVerifier.verify_agendamento_ownership(db, agendamento_id, cliente)
