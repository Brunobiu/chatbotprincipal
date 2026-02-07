"""
Model para conversas do WhatsApp
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class StatusConversa(str, enum.Enum):
    """Enum para status da conversa"""
    ATIVA = "ativa"
    AGUARDANDO_HUMANO = "aguardando_humano"
    FINALIZADA = "finalizada"


class MotivoFallback(str, enum.Enum):
    """Enum para motivo do fallback"""
    BAIXA_CONFIANCA = "baixa_confianca"
    SOLICITACAO_MANUAL = "solicitacao_manual"


class Conversa(Base):
    """
    Conversas do WhatsApp
    Gerencia o estado da conversa e fallback para humano
    """
    __tablename__ = "conversas"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    numero_whatsapp = Column(String(20), nullable=False, index=True)
    
    # Status e fallback
    status = Column(String(20), default="ativa", nullable=False, index=True)
    motivo_fallback = Column(String(20), nullable=True)
    
    # Timestamps
    ultima_mensagem_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    assumida_por = Column(String(100), nullable=True)
    assumida_em = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="conversas")
    mensagens = relationship("Mensagem", back_populates="conversa", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversa(id={self.id}, numero={self.numero_whatsapp}, status={self.status.value})>"
