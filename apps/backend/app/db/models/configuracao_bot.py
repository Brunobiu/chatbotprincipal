"""
Model para configurações do bot
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class TomEnum(str, enum.Enum):
    """Enum para tom das mensagens"""
    FORMAL = "formal"
    CASUAL = "casual"
    TECNICO = "tecnico"


class ConfiguracaoBot(Base):
    """
    Configurações do bot por cliente
    Cada cliente tem suas próprias configurações de tom e mensagens
    """
    __tablename__ = "configuracoes_bot"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), unique=True, nullable=False)
    
    # Tom das mensagens
    tom = Column(SQLEnum(TomEnum), default="casual", nullable=False)
    
    # Mensagens personalizadas
    mensagem_saudacao = Column(Text, nullable=True)
    mensagem_fallback = Column(Text, nullable=True)
    mensagem_espera = Column(Text, nullable=True)
    mensagem_retorno_24h = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento
    cliente = relationship("Cliente", back_populates="configuracao_bot")
    
    def __repr__(self):
        return f"<ConfiguracaoBot(cliente_id={self.cliente_id}, tom={self.tom})>"
