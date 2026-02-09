from datetime import datetime
from sqlalchemy import Column, Integer, DECIMAL, DateTime
from app.db.base import Base


class AdminObjetivos(Base):
    __tablename__ = "admin_objetivos"

    id = Column(Integer, primary_key=True)
    meta_clientes_mes = Column(Integer, default=10, nullable=False)
    meta_receita_mes = Column(DECIMAL(10, 2), default=5000.00, nullable=False)
    max_anuncios_percent = Column(Integer, default=30, nullable=False)
    max_openai_percent = Column(Integer, default=20, nullable=False)
    taxa_conversao_esperada = Column(Integer, default=20, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AdminObjetivos(meta_clientes={self.meta_clientes_mes}, meta_receita={self.meta_receita_mes})>"
