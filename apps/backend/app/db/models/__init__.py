# Models registry for Alembic
from app.db.models.cliente import Cliente
from app.db.models.conversa import Conversa
from app.db.models.mensagem import Mensagem
from app.db.models.instancia_whatsapp import InstanciaWhatsApp

__all__ = ["Cliente", "Conversa", "Mensagem", "InstanciaWhatsApp"]
