"""
Modelo para logs de autenticação
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from app.db.base import Base


class LogAutenticacao(Base):
    """
    Modelo para registrar todas as tentativas de autenticação
    Usado para auditoria e detecção de ataques
    """
    __tablename__ = "logs_autenticacao"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=True, index=True)  # Null se cliente não existe
    email_tentativa = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)  # IPv6 pode ter até 45 chars
    user_agent = Column(String(500), nullable=True)
    sucesso = Column(Boolean, nullable=False, index=True)
    motivo_falha = Column(String(255), nullable=True)  # Ex: "senha_incorreta", "conta_bloqueada", "email_nao_existe"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<LogAutenticacao(id={self.id}, email='{self.email_tentativa}', sucesso={self.sucesso}, ip='{self.ip_address}')>"
