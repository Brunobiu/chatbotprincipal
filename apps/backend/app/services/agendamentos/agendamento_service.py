"""
AgendamentoService - Serviço de gerenciamento de agendamentos
Task 10.2
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.models.agendamento import Agendamento, ConfiguracaoHorarios, AgendamentoStatus


class AgendamentoService:
    """Serviço para gerenciar agendamentos"""
    
    @staticmethod
    def configurar_horarios(
        db: Session,
        cliente_id: int,
        horarios_disponiveis: Dict,
        duracao_slot_minutos: int = 30,
        tipos_servico: Optional[List[str]] = None
    ) -> ConfiguracaoHorarios:
        """
        Configura horários disponíveis do cliente
        
        Args:
            cliente_id: ID do cliente
            horarios_disponiveis: Dict com horários por dia da semana
                Exemplo: {"segunda": [{"inicio": "09:00", "fim": "18:00"}], ...}
            duracao_slot_minutos: Duração de cada slot em minutos
            tipos_servico: Lista de tipos de serviço disponíveis
        
        Returns:
            ConfiguracaoHorarios criada ou atualizada
        """
        # Verificar se já existe configuração
        config = db.query(ConfiguracaoHorarios).filter(
            ConfiguracaoHorarios.cliente_id == cliente_id
        ).first()
        
        if config:
            # Atualizar existente
            config.horarios_disponiveis = horarios_disponiveis
            config.duracao_slot_minutos = duracao_slot_minutos
            config.tipos_servico = tipos_servico
            config.updated_at = datetime.utcnow()
        else:
            # Criar nova
            config = ConfiguracaoHorarios(
                cliente_id=cliente_id,
                horarios_disponiveis=horarios_disponiveis,
                duracao_slot_minutos=duracao_slot_minutos,
                tipos_servico=tipos_servico
            )
            db.add(config)
        
        db.commit()
        db.refresh(config)
        return config
    
    @staticmethod
    def obter_configuracao(db: Session, cliente_id: int) -> Optional[ConfiguracaoHorarios]:
        """Retorna configuração de horários do cliente"""
        return db.query(ConfiguracaoHorarios).filter(
            ConfiguracaoHorarios.cliente_id == cliente_id
        ).first()
    
    @staticmethod
    def criar_agendamento(
        db: Session,
        cliente_id: int,
        numero_usuario: str,
        data_hora: datetime,
        nome_usuario: Optional[str] = None,
        tipo_servico: Optional[str] = None,
        observacoes: Optional[str] = None,
        mensagem_original: Optional[str] = None
    ) -> Agendamento:
        """
        Cria novo agendamento
        
        Args:
            cliente_id: ID do cliente
            numero_usuario: Número WhatsApp do usuário
            data_hora: Data e hora do agendamento
            nome_usuario: Nome do usuário (opcional)
            tipo_servico: Tipo de serviço (opcional)
            observacoes: Observações adicionais (opcional)
            mensagem_original: Mensagem original do usuário (opcional)
        
        Returns:
            Agendamento criado
        """
        agendamento = Agendamento(
            cliente_id=cliente_id,
            numero_usuario=numero_usuario,
            nome_usuario=nome_usuario,
            data_hora=data_hora,
            tipo_servico=tipo_servico,
            observacoes=observacoes,
            mensagem_original=mensagem_original,
            status=AgendamentoStatus.PENDENTE
        )
        
        db.add(agendamento)
        db.commit()
        db.refresh(agendamento)
        return agendamento
    
    @staticmethod
    def listar_agendamentos_pendentes(
        db: Session,
        cliente_id: int,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> List[Agendamento]:
        """
        Lista agendamentos pendentes do cliente
        
        Args:
            cliente_id: ID do cliente
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)
        
        Returns:
            Lista de agendamentos pendentes
        """
        query = db.query(Agendamento).filter(
            Agendamento.cliente_id == cliente_id,
            Agendamento.status == AgendamentoStatus.PENDENTE
        )
        
        if data_inicio:
            query = query.filter(Agendamento.data_hora >= data_inicio)
        
        if data_fim:
            query = query.filter(Agendamento.data_hora <= data_fim)
        
        return query.order_by(Agendamento.data_hora.asc()).all()
    
    @staticmethod
    def listar_agendamentos(
        db: Session,
        cliente_id: int,
        status: Optional[AgendamentoStatus] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Agendamento]:
        """
        Lista agendamentos do cliente com filtros
        
        Args:
            cliente_id: ID do cliente
            status: Filtrar por status (opcional)
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)
            limit: Limite de resultados
            offset: Offset para paginação
        
        Returns:
            Lista de agendamentos
        """
        query = db.query(Agendamento).filter(
            Agendamento.cliente_id == cliente_id
        )
        
        if status:
            query = query.filter(Agendamento.status == status)
        
        if data_inicio:
            query = query.filter(Agendamento.data_hora >= data_inicio)
        
        if data_fim:
            query = query.filter(Agendamento.data_hora <= data_fim)
        
        return query.order_by(Agendamento.data_hora.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def aprovar_agendamento(db: Session, agendamento_id: int, cliente_id: int) -> Agendamento:
        """
        Aprova agendamento
        
        Args:
            agendamento_id: ID do agendamento
            cliente_id: ID do cliente (para validação)
        
        Returns:
            Agendamento aprovado
        
        Raises:
            ValueError: Se agendamento não encontrado ou não pertence ao cliente
        """
        agendamento = db.query(Agendamento).filter(
            Agendamento.id == agendamento_id,
            Agendamento.cliente_id == cliente_id
        ).first()
        
        if not agendamento:
            raise ValueError("Agendamento não encontrado")
        
        agendamento.status = AgendamentoStatus.APROVADO
        agendamento.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(agendamento)
        return agendamento
    
    @staticmethod
    def recusar_agendamento(db: Session, agendamento_id: int, cliente_id: int) -> Agendamento:
        """
        Recusa agendamento
        
        Args:
            agendamento_id: ID do agendamento
            cliente_id: ID do cliente (para validação)
        
        Returns:
            Agendamento recusado
        
        Raises:
            ValueError: Se agendamento não encontrado ou não pertence ao cliente
        """
        agendamento = db.query(Agendamento).filter(
            Agendamento.id == agendamento_id,
            Agendamento.cliente_id == cliente_id
        ).first()
        
        if not agendamento:
            raise ValueError("Agendamento não encontrado")
        
        agendamento.status = AgendamentoStatus.RECUSADO
        agendamento.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(agendamento)
        return agendamento
    
    @staticmethod
    def cancelar_agendamento(db: Session, agendamento_id: int, cliente_id: int) -> Agendamento:
        """
        Cancela agendamento
        
        Args:
            agendamento_id: ID do agendamento
            cliente_id: ID do cliente (para validação)
        
        Returns:
            Agendamento cancelado
        
        Raises:
            ValueError: Se agendamento não encontrado ou não pertence ao cliente
        """
        agendamento = db.query(Agendamento).filter(
            Agendamento.id == agendamento_id,
            Agendamento.cliente_id == cliente_id
        ).first()
        
        if not agendamento:
            raise ValueError("Agendamento não encontrado")
        
        agendamento.status = AgendamentoStatus.CANCELADO
        agendamento.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(agendamento)
        return agendamento
    
    @staticmethod
    def obter_agendamento(db: Session, agendamento_id: int, cliente_id: int) -> Optional[Agendamento]:
        """Retorna agendamento por ID"""
        return db.query(Agendamento).filter(
            Agendamento.id == agendamento_id,
            Agendamento.cliente_id == cliente_id
        ).first()
    
    @staticmethod
    def agendamentos_do_dia(db: Session, cliente_id: int, data: datetime) -> List[Agendamento]:
        """
        Retorna agendamentos de um dia específico
        
        Args:
            cliente_id: ID do cliente
            data: Data para buscar agendamentos
        
        Returns:
            Lista de agendamentos do dia
        """
        inicio_dia = data.replace(hour=0, minute=0, second=0, microsecond=0)
        fim_dia = inicio_dia + timedelta(days=1)
        
        return db.query(Agendamento).filter(
            Agendamento.cliente_id == cliente_id,
            Agendamento.data_hora >= inicio_dia,
            Agendamento.data_hora < fim_dia,
            Agendamento.status.in_([AgendamentoStatus.PENDENTE, AgendamentoStatus.APROVADO])
        ).order_by(Agendamento.data_hora.asc()).all()
