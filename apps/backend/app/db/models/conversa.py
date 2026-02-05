import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class ConversaEstado(str, enum.Enum):
    IA_ATIVA = "ia_ativa"
    AGUARDANDO_HUMANO = "aguardando_humano"
    HUMANO_RESPONDEU = "humano_respondeu"


class Conversa(Base):
    __tablename__ = "conversas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    numero_usuario = Column(String(20), nullable=False, index=True)
    estado = Column(SQLEnum(ConversaEstado), default=ConversaEstado.IA_ATIVA, nullable=False)
    ultima_mensagem = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="conversas")
    mensagens = relationship("Mensagem", back_populates="conversa", cascade="all, delete-orphan", order_by="Mensagem.created_at")

    def __repr__(self):
        return f"<Conversa(id={self.id}, cliente_id={self.cliente_id}, numero='{self.numero_usuario}', estado='{self.estado}')>"
