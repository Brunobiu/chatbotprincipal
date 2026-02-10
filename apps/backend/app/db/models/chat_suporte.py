"""
Models para Chat Suporte
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class ChatSuporteConversa(Base):
    __tablename__ = "chat_suporte_conversas"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    status = Column(String(20), default="nao_respondido")  # nao_respondido, respondido, concluido
    visualizado_admin = Column(Boolean, default=False)
    iniciada_em = Column(DateTime(timezone=True), server_default=func.now())
    encerrada_em = Column(DateTime(timezone=True), nullable=True)
    encerrada_por = Column(Integer, nullable=True)
    ultima_mensagem_em = Column(DateTime(timezone=True), server_default=func.now())
    ultima_mensagem_admin_em = Column(DateTime(timezone=True), nullable=True)
    bot_respondeu_boas_vindas = Column(Boolean, default=False)
    bot_respondeu_aguarde = Column(Boolean, default=False)
    ultima_mensagem_cliente = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    mensagens = relationship("ChatSuporteMensagem", back_populates="conversa")


class ChatSuporteMensagem(Base):
    __tablename__ = "chat_suporte_mensagens"
    
    id = Column(Integer, primary_key=True, index=True)
    conversa_id = Column(Integer, ForeignKey("chat_suporte_conversas.id"))
    remetente_tipo = Column(String(20))  # cliente, admin, sistema
    remetente_id = Column(Integer, nullable=True)
    mensagem = Column(Text)
    visualizado = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversa = relationship("ChatSuporteConversa", back_populates="mensagens")
