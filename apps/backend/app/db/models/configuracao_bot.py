"""
Model para configurações do bot
"""
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class TomEnum(str, enum.Enum):
    """Enum para tom das mensagens"""
    formal = "formal"
    casual = "casual"
    tecnico = "tecnico"


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
    
    # Configurações de confiança e fallback
    threshold_confianca = Column(Float, default=0.6, nullable=False)
    notificar_email = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento
    cliente = relationship("Cliente", back_populates="configuracao_bot")
    
    def __repr__(self):
        return f"<ConfiguracaoBot(cliente_id={self.cliente_id}, tom={self.tom})>"
