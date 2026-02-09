"""
Modelo para verificação de SMS
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from app.db.base import Base


class SMSVerification(Base):
    __tablename__ = "sms_verifications"

    id = Column(Integer, primary_key=True, index=True)
    telefone = Column(String(20), nullable=False, index=True)
    codigo = Column(String(6), nullable=False)
    verificado = Column(Boolean, default=False, nullable=False)
    tentativas = Column(Integer, default=0, nullable=False)
    expira_em = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SMSVerification(telefone='{self.telefone}', verificado={self.verificado})>"
