"""
Modelo para histórico de trials utilizados
Proteção Anti-Abuso
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base


class TrialHistory(Base):
    __tablename__ = "trial_history"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_number = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    ip_cadastro = Column(String(45), nullable=True)
    device_fingerprint = Column(String(255), nullable=True)
    used_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<TrialHistory(whatsapp={self.whatsapp_number}, email={self.email})>"
