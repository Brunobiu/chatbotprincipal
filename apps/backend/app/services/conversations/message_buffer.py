"""
Buffer de mensagens com suporte a multi-tenant
"""
import asyncio
import redis.asyncio as redis
import logging
from collections import defaultdict
from typing import Optional

from app.core.config import REDIS_URL, BUFFER_KEY_SUFIX, DEBOUNCE_SECONDS, BUFFER_TTL
from app.services.whatsapp.evolution_api import send_whatsapp_message
from app.services.llm.chains import get_conversational_rag_chain

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
debounce_tasks = defaultdict(asyncio.Task)


async def buffer_message(chat_id: str, message: str, cliente_id: Optional[int] = None):
    """
    Adiciona mensagem ao buffer com debounce
    
    Args:
        chat_id: ID do chat (número do WhatsApp)
        message: Mensagem recebida
        cliente_id: ID do cliente (para isolamento multi-tenant)
    """
    buffer_key = f'{chat_id}{BUFFER_KEY_SUFIX}'

    await redis_client.rpush(buffer_key, message)
    await redis_client.expire(buffer_key, BUFFER_TTL)

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
        await asyncio.sleep(float(DEBOUNCE_SECONDS))

        buffer_key = f'{chat_id}{BUFFER_KEY_SUFIX}'
        messages = await redis_client.lrange(buffer_key, 0, -1)

        full_message = ' '.join(messages).strip()
        if full_message:
            logger.info(f'[BUFFER] Enviando mensagem agrupada para {chat_id}: {full_message}')
            
            # Criar session_id único por cliente + chat
            if cliente_id:
                session_id = f'cliente_{cliente_id}_{chat_id}'
                logger.info(f'[BUFFER] Usando session_id: {session_id}')
            else:
                session_id = chat_id
                logger.warning(f'[BUFFER] Cliente ID não fornecido, usando session_id legado: {session_id}')
            
            # Obter chain com isolamento por cliente
            conversational_rag_chain = get_conversational_rag_chain(cliente_id)
            
            ai_response = conversational_rag_chain.invoke(
                input={'input': full_message},
                config={'configurable': {'session_id': session_id}},
            )['answer']

            send_whatsapp_message(
                number=chat_id,
                text=ai_response,
            )
            
            logger.info(f'[BUFFER] Resposta enviada para {chat_id}')
            
        await redis_client.delete(buffer_key)
        
        # Limpar task do dict
        if chat_id in debounce_tasks:
            del debounce_tasks[chat_id]

    except asyncio.CancelledError:
        logger.info(f'[BUFFER] Debounce cancelado para {chat_id}')
    except Exception as e:
        logger.error(f'[BUFFER] Erro ao processar mensagem: {str(e)}', exc_info=True)
