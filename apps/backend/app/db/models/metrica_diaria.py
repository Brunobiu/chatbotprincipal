from datetime import datetime, date
from sqlalchemy import Column, Integer, Date, DECIMAL, DateTime
from app.db.base import Base


class MetricaDiaria(Base):
    __tablename__ = "metricas_diarias"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False, unique=True, index=True)
    total_clientes = Column(Integer, default=0, nullable=False)
    clientes_ativos = Column(Integer, default=0, nullable=False)
    clientes_trial = Column(Integer, default=0, nullable=False)
    clientes_cancelados = Column(Integer, default=0, nullable=False)
    novos_clientes = Column(Integer, default=0, nullable=False)
    conversoes = Column(Integer, default=0, nullable=False)
    cancelamentos = Column(Integer, default=0, nullable=False)
    total_conversas = Column(Integer, default=0, nullable=False)
    total_mensagens = Column(Integer, default=0, nullable=False)
    receita_dia = Column(DECIMAL(10, 2), default=0, nullable=False)
    custo_openai_dia = Column(DECIMAL(10, 2), default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<MetricaDiaria(data={self.data}, clientes={self.total_clientes})>"
