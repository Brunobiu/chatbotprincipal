from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class DicaIA(Base):
    __tablename__ = "dicas_ia"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False, index=True)
    conteudo = Column(JSON, nullable=False)  # JSON com todas as dicas
    objetivo_mensal = Column(Float, nullable=True)  # Objetivo de faturamento mensal
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relacionamentos
    admin = relationship("Admin")
