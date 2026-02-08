"""
Modelo para rastreamento de uso da OpenAI
FASE 16.4 - Monitoramento de Uso (Créditos OpenAI)
"""
from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class UsoOpenAI(Base):
    """
    Rastreia uso diário de tokens OpenAI por cliente
    Permite controle de custos e alertas de uso excessivo
    """
    __tablename__ = "uso_openai"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True)
    data = Column(Date, nullable=False, index=True)
    
    # Tokens
    tokens_prompt = Column(Integer, default=0, nullable=False)
    tokens_completion = Column(Integer, default=0, nullable=False)
    tokens_total = Column(Integer, default=0, nullable=False)
    
    # Custo
    custo_estimado = Column(Float, default=0.0, nullable=False)
    
    # Estatísticas
    mensagens_processadas = Column(Integer, default=0, nullable=False)
    modelo = Column(String(50), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento
    cliente = relationship("Cliente", backref="uso_openai")
    
    def __repr__(self):
        return f"<UsoOpenAI(cliente_id={self.cliente_id}, data={self.data}, tokens={self.tokens_total}, custo=R${self.custo_estimado:.4f})>"
