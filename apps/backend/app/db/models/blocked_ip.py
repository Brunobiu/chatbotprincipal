"""
Modelo de IPs bloqueados (FASE 5)
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from app.db.base import Base


class BlockedIP(Base):
    """IPs bloqueados por comportamento suspeito"""
    
    __tablename__ = "blocked_ips"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), unique=True, index=True, nullable=False)  # IPv6 = 45 chars
    reason = Column(String(500), nullable=False)
    blocked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    blocked_until = Column(DateTime, nullable=True)  # None = permanente
    is_permanent = Column(Boolean, default=False, nullable=False)
    attempts_count = Column(Integer, default=1, nullable=False)
    last_attempt = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(Text, nullable=True)  # JSON com detalhes adicionais
    
    def __repr__(self):
        return f"<BlockedIP {self.ip_address} - {self.reason}>"
