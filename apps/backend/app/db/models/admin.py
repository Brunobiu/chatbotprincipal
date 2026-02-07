from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="admin")
    tema = Column(String(20), nullable=False, default="light")
    cliente_especial_id = Column(Integer, ForeignKey("clientes.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    cliente_especial = relationship("Cliente", foreign_keys=[cliente_especial_id])
    audit_logs = relationship("AuditLog", back_populates="admin")
    notificacoes = relationship("NotificacaoAdmin", back_populates="admin")


class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    ip = Column(String(45), nullable=False, index=True)
    success = Column(Boolean, nullable=False)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class IPBloqueado(Base):
    __tablename__ = "ips_bloqueados"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(45), unique=True, nullable=False, index=True)
    reason = Column(Text, nullable=True)
    blocked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False)
    old_data = Column(JSONB, nullable=True)
    new_data = Column(JSONB, nullable=True)
    ip = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relacionamentos
    admin = relationship("Admin", back_populates="audit_logs")


class NotificacaoAdmin(Base):
    __tablename__ = "notificacoes_admin"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(50), nullable=False)
    titulo = Column(String(255), nullable=False)
    mensagem = Column(Text, nullable=False)
    prioridade = Column(String(20), nullable=False, default="normal")
    lida = Column(Boolean, nullable=False, default=False)
    data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relacionamentos
    admin = relationship("Admin", back_populates="notificacoes")
