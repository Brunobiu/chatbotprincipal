from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.services.conversations.message_buffer import buffer_message
from app.db.session import get_db
from app.api.v1.billing import router as billing_router
from app.db.models.instancia_whatsapp import InstanciaWhatsApp, InstanciaStatus
from app.db.models.cliente import Cliente, ClienteStatus

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(billing_router, prefix="/api/v1/billing")

@app.get('/health')
async def health_check():
    return {'status': 'ok', 'service': 'whatsapp-ai-bot'}

@app.get('/health/db')
async def health_db(db: Session = Depends(get_db)):
    try:
        # Testa conexão com PostgreSQL
        result = db.execute(text("SELECT 1"))
        return {
            'status': 'ok',
            'database': 'connected',
            'test_query': result.scalar()
        }
    except Exception as e:
        return {
            'status': 'error',
            'database': 'disconnected',
            'error': str(e)
        }

@app.post('/webhook')
async def webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook para receber mensagens do WhatsApp via Evolution API
    Agora com suporte a multi-tenant e lookup de cliente
    """
    try:
        data = await request.json()
        
        # Extrair dados da mensagem
        chat_id = data.get('data', {}).get('key', {}).get('remoteJid')
        message = data.get('data', {}).get('message', {}).get('conversation')
        instance_id = data.get('instance')  # ID da instância que recebeu a mensagem
        
        # Validações básicas
        if not chat_id or not message:
            logger.warning("⚠️ Webhook sem chat_id ou message")
            return {'status': 'ignored', 'reason': 'missing_data'}
        
        # Ignorar mensagens de grupo
        if '@g.us' in chat_id:
            logger.info(f"⚠️ Mensagem de grupo ignorada: {chat_id}")
            return {'status': 'ignored', 'reason': 'group_message'}
        
        logger.info(f"📥 Mensagem recebida: {chat_id} | Instance: {instance_id}")
        
        # Buscar instância e cliente
        instancia = None
        cliente = None
        
        if instance_id:
            # Buscar por instance_id
            instancia = db.query(InstanciaWhatsApp).filter(
                InstanciaWhatsApp.instance_id == instance_id
            ).first()
            
            if instancia:
                cliente = instancia.cliente
                logger.info(f"✅ Cliente identificado: ID={cliente.id} | Email={cliente.email}")
        
        # Se não encontrou por instance_id, tentar por número
        if not cliente:
            # Extrair número do chat_id (remover @s.whatsapp.net)
            numero = chat_id.replace('@s.whatsapp.net', '')
            
            instancia = db.query(InstanciaWhatsApp).filter(
                InstanciaWhatsApp.numero == numero
            ).first()
            
            if instancia:
                cliente = instancia.cliente
                logger.info(f"✅ Cliente identificado por número: ID={cliente.id} | Email={cliente.email}")
        
        # Se não encontrou cliente, logar e ignorar
        if not cliente:
            logger.warning(f"⚠️ Cliente não encontrado para chat_id: {chat_id} | instance: {instance_id}")
            return {'status': 'ignored', 'reason': 'client_not_found'}
        
        # Validar assinatura ativa
        if cliente.status != ClienteStatus.ATIVO:
            logger.warning(f"⚠️ Cliente {cliente.id} com status {cliente.status} - mensagem ignorada")
            return {'status': 'ignored', 'reason': 'inactive_subscription'}
        
        # Processar mensagem com isolamento por cliente
        await buffer_message(
            chat_id=chat_id,
            message=message,
            cliente_id=cliente.id  # ← ISOLAMENTO MULTI-TENANT
        )
        
        logger.info(f"✅ Mensagem processada para cliente {cliente.id}")
        return {'status': 'ok'}
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': str(e)}
