"""
Modelo de Chat Suporte
Task 11.1
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime

from app.db.base import Base


class ChatSuporteMensagem(Base):
    """Mensagem do chat de suporte"""
    __tablename__ = "chat_suporte_mensagens"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False, index=True)
    
    # Tipo do remetente: 'cliente' ou 'ia'
    remetente_tipo = Column(String(20), nullable=False)
    
    # Conteúdo da mensagem
    mensagem = Column(Text, nullable=False)
    
    # Confiança da resposta (apenas para mensagens da IA)
    confianca = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<ChatSuporteMensagem(id={self.id}, cliente_id={self.cliente_id}, remetente={self.remetente_tipo})>"
