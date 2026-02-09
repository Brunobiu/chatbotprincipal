# Models registry for Alembic
from app.db.models.cliente import Cliente
from app.db.models.conversa import Conversa
from app.db.models.mensagem import Mensagem
from app.db.models.instancia_whatsapp import InstanciaWhatsApp
from app.db.models.configuracao_bot import ConfiguracaoBot
from app.db.models.conhecimento import Conhecimento
from app.db.models.admin import Admin, LoginAttempt, IPBloqueado, AuditLog, NotificacaoAdmin
from app.db.models.uso_openai import UsoOpenAI
from app.db.models.ticket import Ticket, TicketCategoria, TicketMensagem
from app.db.models.tutorial import Tutorial, TutorialVisualizacao, TutorialComentario
from app.db.models.aviso import Aviso
from app.db.models.agendamento import Agendamento, ConfiguracaoHorarios
from app.db.models.chat_suporte import ChatSuporteMensagem
from app.db.models.log_autenticacao import LogAutenticacao
from app.db.models.trial_history import TrialHistory
from app.db.models.sms_verification import SMSVerification

__all__ = [
    "Cliente", 
    "Conversa", 
    "Mensagem", 
    "InstanciaWhatsApp", 
    "ConfiguracaoBot", 
    "Conhecimento",
    "Admin",
    "LoginAttempt",
    "IPBloqueado",
    "AuditLog",
    "NotificacaoAdmin",
    "UsoOpenAI",
    "Ticket",
    "TicketCategoria",
    "TicketMensagem",
    "Tutorial",
    "TutorialVisualizacao",
    "TutorialComentario",
    "Aviso",
    "Agendamento",
    "ConfiguracaoHorarios",
    "ChatSuporteMensagem",
    "LogAutenticacao",
    "TrialHistory",
    "SMSVerification"
]
