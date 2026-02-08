from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base


class TicketCategoria(Base):
    __tablename__ = "ticket_categorias"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relacionamentos
    tickets = relationship("Ticket", back_populates="categoria")


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("ticket_categorias.id", ondelete="SET NULL"), nullable=True)
    assunto = Column(String(200), nullable=False)
    status = Column(String(50), default="aberto", nullable=False)
    prioridade = Column(String(20), default="normal", nullable=False)
    atribuido_admin_id = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    ia_respondeu = Column(Boolean, default=False, nullable=False)
    confianca_ia = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    resolvido_em = Column(DateTime, nullable=True)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="tickets")
    categoria = relationship("TicketCategoria", back_populates="tickets")
    atribuido_admin = relationship("Admin")
    mensagens = relationship("TicketMensagem", back_populates="ticket", cascade="all, delete-orphan")


class TicketMensagem(Base):
    __tablename__ = "ticket_mensagens"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    remetente_tipo = Column(String(20), nullable=False)  # cliente, admin, ia
    remetente_id = Column(Integer, nullable=True)
    mensagem = Column(Text, nullable=False)
    anexos = Column(JSONB, nullable=True)
    lida = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relacionamentos
    ticket = relationship("Ticket", back_populates="mensagens")
