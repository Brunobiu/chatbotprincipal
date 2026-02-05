# Models registry for Alembic
from app.db.models.cliente import Cliente
from app.db.models.conversa import Conversa
from app.db.models.mensagem import Mensagem
from app.db.models.instancia_whatsapp import InstanciaWhatsApp
from app.db.models.configuracao_bot import ConfiguracaoBot
from app.db.models.conhecimento import Conhecimento

__all__ = ["Cliente", "Conversa", "Mensagem", "InstanciaWhatsApp", "ConfiguracaoBot", "Conhecimento"]
