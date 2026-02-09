from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class ContextoUsuarioWhatsApp(Base):
    __tablename__ = "contexto_usuarios_whatsapp"
    __table_args__ = (
        UniqueConstraint('cliente_id', 'numero_usuario', name='uq_cliente_numero'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    numero_usuario = Column(String(50), nullable=False)
    nome = Column(String(200), nullable=True)
    primeira_interacao = Column(DateTime, server_default=func.now(), nullable=False)
    ultima_interacao = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relacionamentos
    cliente = relationship("Cliente")
