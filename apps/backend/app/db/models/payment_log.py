"""
Modelo de Log de Pagamentos (FASE 6)
Auditoria completa de todas transações
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class PaymentLog(Base):
    """Log de auditoria de todas transações de pagamento"""
    
    __tablename__ = "payment_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    
    # Dados da transação Stripe
    stripe_payment_intent_id = Column(String(255), unique=True, index=True, nullable=True)
    stripe_subscription_id = Column(String(255), index=True, nullable=True)
    stripe_invoice_id = Column(String(255), index=True, nullable=True)
    stripe_customer_id = Column(String(255), index=True, nullable=True)
    
    # Valores
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="brl", nullable=False)
    
    # Status
    status = Column(String(50), nullable=False, index=True)  # pending, succeeded, failed, cancelled
    
    # Metadados
    plan_id = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    event_type = Column(String(100), nullable=True)  # Tipo do evento Stripe
    
    # Auditoria de segurança
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Webhook
    webhook_received = Column(Boolean, default=False, nullable=False)
    webhook_received_at = Column(DateTime, nullable=True)
    webhook_event_id = Column(String(255), unique=True, nullable=True)  # Previne replay
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento
    cliente = relationship("Cliente", back_populates="payment_logs")
    
    def __repr__(self):
        return f"<PaymentLog {self.id} - Cliente {self.cliente_id} - {self.status} - R$ {self.amount}>"
