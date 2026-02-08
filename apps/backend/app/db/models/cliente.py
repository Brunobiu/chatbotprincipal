import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class ClienteStatus(str, enum.Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    PENDENTE = "pendente"
    SUSPENSO = "suspenso"


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    nome_empresa = Column(String(255), nullable=True)  # Nome da empresa do cliente
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=True)
    senha_hash = Column(String(255), nullable=False)
    status = Column(SQLEnum(ClienteStatus), default=ClienteStatus.PENDENTE, nullable=False)
    # Stripe fields
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True, index=True)
    stripe_status = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Tracking fields (FASE 16.3)
    ultimo_login = Column(DateTime, nullable=True, index=True)
    ip_ultimo_login = Column(String(45), nullable=True)  # IPv6 pode ter até 45 chars
    total_mensagens_enviadas = Column(Integer, default=0, nullable=False)

    # Relacionamentos
    conversas = relationship("Conversa", back_populates="cliente", cascade="all, delete-orphan")
    configuracao_bot = relationship("ConfiguracaoBot", back_populates="cliente", uselist=False, cascade="all, delete-orphan")
    conhecimento = relationship("Conhecimento", back_populates="cliente", uselist=False, cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="cliente", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome}', email='{self.email}', status='{self.status}')>"
