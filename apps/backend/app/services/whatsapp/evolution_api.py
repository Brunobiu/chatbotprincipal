import requests
import logging

from app.core.config import (
    EVOLUTION_API_URL,
    EVOLUTION_INSTANCE_NAME,
    EVOLUTION_AUTHENTICATION_API_KEY,
)

logger = logging.getLogger(__name__)


def send_whatsapp_message(number, text):
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
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem: {e}")
        raise
