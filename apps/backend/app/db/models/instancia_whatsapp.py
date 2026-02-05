"""
Modelo para instâncias do WhatsApp (Evolution API)
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class InstanciaStatus(str, enum.Enum):
    PENDENTE = "pendente"
    CONECTADA = "conectada"
    DESCONECTADA = "desconectada"
    ERRO = "erro"


class InstanciaWhatsApp(Base):
    __tablename__ = "instancias_whatsapp"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    instance_id = Column(String(255), unique=True, nullable=False, index=True)
    numero = Column(String(20), nullable=True, index=True)  # Número conectado
    status = Column(SQLEnum(InstanciaStatus), default=InstanciaStatus.PENDENTE, nullable=False)
    qr_code = Column(String(2000), nullable=True)  # QR code base64
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    cliente = relationship("Cliente", backref="instancias_whatsapp")

    def __repr__(self):
        return f"<InstanciaWhatsApp(id={self.id}, cliente_id={self.cliente_id}, instance_id='{self.instance_id}', status='{self.status}')>"
