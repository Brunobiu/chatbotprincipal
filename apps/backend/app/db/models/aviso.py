from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.db.base import Base


class Aviso(Base):
    __tablename__ = "avisos"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)  # info, warning, error, success
    titulo = Column(String(200), nullable=False)
    mensagem = Column(Text, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    dismissivel = Column(Boolean, default=True, nullable=False)
    data_inicio = Column(DateTime, nullable=True)
    data_fim = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
