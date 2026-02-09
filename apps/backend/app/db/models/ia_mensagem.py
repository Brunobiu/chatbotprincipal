from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.db.base import Base


class IAMensagem(Base):
    __tablename__ = "ia_mensagens"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False, index=True)
    conteudo = Column(Text, nullable=False)
    dados_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<IAMensagem(id={self.id}, tipo='{self.tipo}')>"
