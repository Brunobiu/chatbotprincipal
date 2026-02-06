"""
Buffer de mensagens com suporte a multi-tenant
"""
import asyncio
import redis.asyncio as redis
import logging
from collections import defaultdict
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.whatsapp.evolution_api import send_whatsapp_message
from app.services.ai import AIService
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(settings.CACHE_REDIS_URI, decode_responses=True)
debounce_tasks = defaultdict(asyncio.Task)


async def buffer_message(chat_id: str, message: str, cliente_id: Optional[int] = None):
    """
    Adiciona mensagem ao buffer com debounce
    
    Args:
        chat_id: ID do chat (número do WhatsApp)
        message: Mensagem recebida
        cliente_id: ID do cliente (para isolamento multi-tenant)
    """
    buffer_key = f'{chat_id}{settings.BUFFER_KEY_SUFIX}'

    await redis_client.rpush(buffer_key, message)
    await redis_client.expire(buffer_key, int(settings.BUFFER_TTL))

    logger.info(f'[BUFFER] Mensagem adicionada ao buffer de {chat_id}: {message}')

    if debounce_tasks.get(chat_id):
        debounce_tasks[chat_id].cancel()
        logger.info(f'[BUFFER] Debounce resetado para {chat_id}')

    debounce_tasks[chat_id] = asyncio.create_task(
        handle_debounce(chat_id, cliente_id)
    )


async def handle_debounce(chat_id: str, cliente_id: Optional[int] = None):
    """
    Processa mensagens após debounce
    
    Args:
        chat_id: ID do chat
        cliente_id: ID do cliente (para isolamento multi-tenant)
    """
    try:
        logger.info(f'[BUFFER] Iniciando debounce para {chat_id}')
        await asyncio.sleep(float(settings.DEBOUNCE_SECONDS))

        buffer_key = f'{chat_id}{settings.BUFFER_KEY_SUFIX}'
        messages = await redis_client.lrange(buffer_key, 0, -1)

        full_message = ' '.join(messages).strip()
        if full_message:
            logger.info(f'[BUFFER] Processando mensagem para {chat_id}: {full_message}')
            
            if not cliente_id:
                logger.error(f'[BUFFER] Cliente ID não fornecido para {chat_id}')
                return
            
            # Criar session_id único por cliente + chat
            session_id = f'cliente_{cliente_id}_{chat_id}'
            
            # Buscar configurações do cliente
            db = SessionLocal()
            try:
                from app.services.configuracoes import ConfiguracaoService
                config = ConfiguracaoService.buscar_ou_criar(db, cliente_id)
                tom = config.tom.value
                
                logger.info(f'[BUFFER] Usando tom: {tom}')
                
                # Processar com IA
                resultado = AIService.processar_mensagem(
                    cliente_id=cliente_id,
                    chat_id=session_id,
                    mensagem=full_message,
                    tom=tom
                )
                
                resposta = resultado['resposta']
                confianca = resultado['confianca']
                
                logger.info(f'[BUFFER] Resposta gerada (confiança: {confianca:.2f}): {resposta[:100]}...')
                
                # Enviar resposta
                send_whatsapp_message(
                    number=chat_id,
                    text=resposta,
                )
                
                logger.info(f'[BUFFER] Resposta enviada para {chat_id}')
                
            finally:
                db.close()
            
        await redis_client.delete(buffer_key)
        
        # Limpar task do dict
        if chat_id in debounce_tasks:
            del debounce_tasks[chat_id]

    except asyncio.CancelledError:
        logger.info(f'[BUFFER] Debounce cancelado para {chat_id}')
    except Exception as e:
        logger.error(f'[BUFFER] Erro ao processar mensagem: {str(e)}', exc_info=True)
