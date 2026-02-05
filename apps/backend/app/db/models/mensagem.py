from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Mensagem(Base):
    __tablename__ = "mensagens"

    id = Column(Integer, primary_key=True, index=True)
    conversa_id = Column(Integer, ForeignKey("conversas.id"), nullable=False, index=True)
    tipo = Column(String(20), nullable=False)  # 'usuario', 'ia', 'humano'
    conteudo = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    conversa = relationship("Conversa", back_populates="mensagens")

    def __repr__(self):
        return f"<Mensagem(id={self.id}, conversa_id={self.conversa_id}, tipo='{self.tipo}')>"
