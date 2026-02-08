"""
Model para conhecimento do bot
"""
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Conhecimento(Base):
    """
    Base de conhecimento por cliente
    Cada cliente tem seu próprio conhecimento (até 50.000 caracteres)
    """
    __tablename__ = "conhecimentos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), unique=True, nullable=False)
    
    # Conteúdo do conhecimento (máximo 50.000 caracteres)
    conteudo_texto = Column(Text, nullable=True)
    
    # Conteúdo estruturado em JSON (gerado automaticamente pela IA)
    conteudo_estruturado = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento
    cliente = relationship("Cliente", back_populates="conhecimento")
    
    def __repr__(self):
        return f"<Conhecimento(cliente_id={self.cliente_id}, chars={len(self.conteudo_texto or '')})>"
