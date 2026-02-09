"""
AgendamentoNotificacaoService - Serviço de notificações de agendamentos
Task 10.7
"""

import logging
from sqlalchemy.orm import Session

from app.db.models.agendamento import Agendamento
from app.services.whatsapp.evolution_api import send_whatsapp_message
from app.services.agendamentos.agendamento_ai_parser import AgendamentoAIParser

logger = logging.getLogger(__name__)


class AgendamentoNotificacaoService:
    """Serviço para enviar notificações de agendamentos via WhatsApp"""
    
    @staticmethod
    def notificar_aprovacao(db: Session, agendamento: Agendamento) -> bool:
        """
        Envia notificação de aprovação de agendamento
        
        Args:
            db: Session do banco de dados
            agendamento: Agendamento aprovado
        
        Returns:
            True se notificação foi enviada com sucesso
        """
        try:
            parser = AgendamentoAIParser()
            
            # Gerar mensagem de aprovação
            mensagem = parser.gerar_mensagem_aprovacao(
                data_hora=agendamento.data_hora,
                tipo_servico=agendamento.tipo_servico,
                nome_usuario=agendamento.nome_usuario
            )
            
            # Enviar mensagem
            send_whatsapp_message(
                number=agendamento.numero_usuario,
                text=mensagem,
                db=db,
                cliente_id=agendamento.cliente_id
            )
            
            logger.info(f'[AGENDAMENTO] Notificação de aprovação enviada: ID={agendamento.id}')
            return True
            
        except Exception as e:
            logger.error(f'[AGENDAMENTO] Erro ao enviar notificação de aprovação: {e}')
            return False
    
    @staticmethod
    def notificar_recusa(db: Session, agendamento: Agendamento, motivo: str = None) -> bool:
        """
        Envia notificação de recusa de agendamento
        
        Args:
            db: Session do banco de dados
            agendamento: Agendamento recusado
            motivo: Motivo da recusa (opcional)
        
        Returns:
            True se notificação foi enviada com sucesso
        """
        try:
            parser = AgendamentoAIParser()
            
            # Gerar mensagem de recusa
            mensagem = parser.gerar_mensagem_recusa(
                data_hora=agendamento.data_hora,
                tipo_servico=agendamento.tipo_servico,
                nome_usuario=agendamento.nome_usuario,
                motivo=motivo
            )
            
            # Enviar mensagem
            send_whatsapp_message(
                number=agendamento.numero_usuario,
                text=mensagem,
                db=db,
                cliente_id=agendamento.cliente_id
            )
            
            logger.info(f'[AGENDAMENTO] Notificação de recusa enviada: ID={agendamento.id}')
            return True
            
        except Exception as e:
            logger.error(f'[AGENDAMENTO] Erro ao enviar notificação de recusa: {e}')
            return False
    
    @staticmethod
    def notificar_cancelamento(db: Session, agendamento: Agendamento, motivo: str = None) -> bool:
        """
        Envia notificação de cancelamento de agendamento
        
        Args:
            db: Session do banco de dados
            agendamento: Agendamento cancelado
            motivo: Motivo do cancelamento (opcional)
        
        Returns:
            True se notificação foi enviada com sucesso
        """
        try:
            mensagem = f"""Olá{', ' + agendamento.nome_usuario if agendamento.nome_usuario else ''}!

❌ Seu agendamento foi CANCELADO.

📅 Data: {agendamento.data_hora.strftime('%d/%m/%Y')}
🕐 Horário: {agendamento.data_hora.strftime('%H:%M')}"""

            if agendamento.tipo_servico:
                mensagem += f"\n🔧 Serviço: {agendamento.tipo_servico}"
            
            if motivo:
                mensagem += f"\n\nMotivo: {motivo}"
            
            mensagem += "\n\nPor favor, entre em contato para reagendar."
            
            # Enviar mensagem
            send_whatsapp_message(
                number=agendamento.numero_usuario,
                text=mensagem,
                db=db,
                cliente_id=agendamento.cliente_id
            )
            
            logger.info(f'[AGENDAMENTO] Notificação de cancelamento enviada: ID={agendamento.id}')
            return True
            
        except Exception as e:
            logger.error(f'[AGENDAMENTO] Erro ao enviar notificação de cancelamento: {e}')
            return False
