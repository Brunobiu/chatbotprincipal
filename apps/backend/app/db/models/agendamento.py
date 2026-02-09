"""
Modelos de Agendamento
Task 10.1
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class AgendamentoStatus(str, enum.Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    RECUSADO = "recusado"
    CANCELADO = "cancelado"


class ConfiguracaoHorarios(Base):
    """Configuração de horários disponíveis do cliente"""
    __tablename__ = "configuracoes_horarios"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False, index=True)
    
    # JSON com horários disponíveis por dia da semana
    # Exemplo: {"segunda": [{"inicio": "09:00", "fim": "18:00"}], "terca": [...], ...}
    horarios_disponiveis = Column(JSON, nullable=False)
    
    # Duração de cada slot em minutos (padrão: 30 minutos)
    duracao_slot_minutos = Column(Integer, nullable=False, default=30)
    
    # Tipos de serviço disponíveis (opcional)
    # Exemplo: ["consulta", "banho", "corte", "manicure"]
    tipos_servico = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ConfiguracaoHorarios(cliente_id={self.cliente_id}, duracao_slot={self.duracao_slot_minutos})>"


class Agendamento(Base):
    """Agendamento criado pelo bot"""
    __tablename__ = "agendamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False, index=True)
    
    # Dados do usuário que fez o agendamento
    numero_usuario = Column(String(20), nullable=False, index=True)
    nome_usuario = Column(String(255), nullable=True)
    
    # Dados do agendamento
    data_hora = Column(DateTime, nullable=False, index=True)
    tipo_servico = Column(String(100), nullable=True)
    observacoes = Column(Text, nullable=True)
    
    # Status do agendamento
    status = Column(SQLEnum(AgendamentoStatus), default=AgendamentoStatus.PENDENTE, nullable=False, index=True)
    
    # Mensagem original do usuário (para contexto)
    mensagem_original = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Agendamento(id={self.id}, cliente_id={self.cliente_id}, data_hora={self.data_hora}, status={self.status})>"
