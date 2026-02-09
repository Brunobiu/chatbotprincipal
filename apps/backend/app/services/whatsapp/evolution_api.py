import requests
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import (
    EVOLUTION_API_URL,
    EVOLUTION_INSTANCE_NAME,
    EVOLUTION_AUTHENTICATION_API_KEY,
)

logger = logging.getLogger(__name__)


def send_whatsapp_message(number, text, db: Optional[Session] = None, cliente_id: Optional[int] = None):
    """
    Envia mensagem via Evolution API e incrementa contador do cliente
    
    Args:
        number: Número do WhatsApp
        text: Texto da mensagem
        db: Sessão do banco (opcional)
        cliente_id: ID do cliente (opcional, para incrementar contador)
    """
    url = f'{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE_NAME}'
    headers = {
        'apikey': EVOLUTION_AUTHENTICATION_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        'number': number,
        'text': text,
    }
    
    try:
        logger.info(f"📤 Enviando mensagem para {number}")
        logger.info(f"   URL: {url}")
        logger.info(f"   Texto: {text[:50]}...")
        
        response = requests.post(
            url=url,
            json=payload,
            headers=headers,
        )
        
        logger.info(f"✅ Resposta Evolution API: {response.status_code}")
        logger.info(f"   Body: {response.text}")
        
        # Incrementar contador de mensagens se envio foi bem-sucedido
        if response.status_code == 200 and db and cliente_id:
            try:
                from app.db.models.cliente import Cliente
                cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
                if cliente:
                    cliente.total_mensagens_enviadas += 1
                    db.commit()
                    logger.info(f"📊 Contador incrementado: cliente {cliente_id} agora tem {cliente.total_mensagens_enviadas} mensagens")
            except Exception as e:
                logger.error(f"❌ Erro ao incrementar contador: {e}")
                db.rollback()
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem: {e}")
        raise
