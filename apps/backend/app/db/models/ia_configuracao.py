from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.db.base import Base


class IAConfiguracao(Base):
    __tablename__ = "ia_configuracoes"

    id = Column(Integer, primary_key=True, index=True)
    provedor = Column(String(20), nullable=False, unique=True)  # 'openai', 'anthropic', 'google'
    api_key_encrypted = Column(Text, nullable=True)
    modelo = Column(String(50), nullable=False)
    ativo = Column(Boolean, default=False, nullable=False)
    configurado = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<IAConfiguracao(provedor='{self.provedor}', modelo='{self.modelo}', ativo={self.ativo})>"
