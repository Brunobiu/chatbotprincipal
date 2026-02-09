from datetime import datetime
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey
from app.db.base import Base


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False, index=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    plano = Column(String(20), nullable=False)  # 'mensal', 'trimestral', 'semestral'
    valor = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), nullable=False, index=True)  # 'pending', 'succeeded', 'failed', 'refunded'
    data_pagamento = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Pagamento(id={self.id}, cliente_id={self.cliente_id}, plano='{self.plano}', valor={self.valor}, status='{self.status}')>"
