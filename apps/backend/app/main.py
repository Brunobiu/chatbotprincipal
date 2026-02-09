from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import atexit

from app.services.conversations.message_buffer import buffer_message
from app.db.session import get_db
from app.api.v1.billing import router as billing_router
from app.api.v1.auth import router as auth_router
from app.db.models.instancia_whatsapp import InstanciaWhatsApp, InstanciaStatus
from app.db.models.cliente import Cliente, ClienteStatus
from app.core.config import settings
from app.core.middleware import ErrorHandlerMiddleware, LoggingMiddleware
from app.core.security import verify_webhook_api_key
from app.workers.scheduler import iniciar_scheduler, parar_scheduler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar rate limiter
limiter = Limiter(key_func=get_remote_address)

# Criar app
app = FastAPI(
    title="WhatsApp AI Bot SaaS",
    description="Sistema multi-tenant de chatbot WhatsApp com IA",
    version="1.0.0"
)

# Registrar rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Adicionar middlewares (ordem importa!)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(billing_router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])

# Importar e incluir router de configurações
from app.api.v1.configuracoes import router as configuracoes_router
app.include_router(configuracoes_router, prefix="/api/v1", tags=["Configuracoes"])

# Importar e incluir router de conhecimento
from app.api.v1.conhecimento import router as conhecimento_router
app.include_router(conhecimento_router, prefix="/api/v1", tags=["Conhecimento"])

# Importar e incluir router de whatsapp
from app.api.v1.whatsapp import router as whatsapp_router
app.include_router(whatsapp_router, prefix="/api/v1/whatsapp", tags=["WhatsApp"])

# Importar e incluir router de conversas
from app.api.v1.conversas import router as conversas_router
app.include_router(conversas_router, prefix="/api/v1", tags=["Conversas"])

# Importar e incluir router de admin (consolidado)
from app.api.v1.admin import router as admin_router
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])

# Importar e incluir router de tickets (cliente)
from app.api.v1.tickets import router as tickets_router
app.include_router(tickets_router, prefix="/api/v1/tickets", tags=["Tickets"])

# Importar e incluir router de tutoriais (cliente)
from app.api.v1.tutoriais import router as tutoriais_router
app.include_router(tutoriais_router, prefix="/api/v1/tutoriais", tags=["Tutoriais"])

# Importar e incluir router de agendamentos
from app.api.v1.agendamentos import router as agendamentos_router
app.include_router(agendamentos_router, prefix="/api/v1/agendamentos", tags=["Agendamentos"])

# Importar e incluir router de chat suporte
from app.api.v1.chat_suporte import router as chat_suporte_router
app.include_router(chat_suporte_router, prefix="/api/v1/chat-suporte", tags=["Chat Suporte"])

logger.info("🚀 Aplicação iniciada com segurança habilitada")
logger.info(f"🔒 CORS configurado para: {settings.get_allowed_origins_list()}")
logger.info(f"⏱️ Rate limit: {settings.RATE_LIMIT_PER_MINUTE} req/min")

# Inicializar scheduler de jobs
iniciar_scheduler()

# Registrar função para parar scheduler ao encerrar aplicação
atexit.register(parar_scheduler)

@app.get('/health')
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def health_check(request: Request):
    return {'status': 'ok', 'service': 'whatsapp-ai-bot'}

@app.get('/health/db')
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def health_db(request: Request, db: Session = Depends(get_db)):
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

@app.post('/webhook/whatsapp')
@limiter.exempt  # Webhook não tem rate limit - precisa receber todas as mensagens
async def webhook(
    request: Request,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_webhook_api_key)
):
    """
    Webhook para receber mensagens do WhatsApp via Evolution API
    Agora com suporte a multi-tenant, lookup de cliente e segurança
    
    Requer API Key no header X-API-Key (se WEBHOOK_API_KEY estiver configurado)
    SEM rate limit - precisa processar todas as mensagens
    """
    try:
        data = await request.json()
        
        # DEBUG: Logar payload completo
        logger.info(f"🔍 [DEBUG] Webhook payload: {data}")
        
        # Extrair event type
        event = data.get('event')
        instance_id = data.get('instance')
        
        # Ignorar eventos de presença (digitando, online, etc)
        if event == 'presence.update':
            return {'status': 'ignored', 'reason': 'presence_event'}
        
        # Processar apenas eventos de mensagens
        if event != 'messages.upsert':
            logger.debug(f"⏭️ Evento ignorado: {event}")
            return {'status': 'ignored', 'reason': 'not_message_event'}
        
        # Extrair dados da mensagem
        message_data = data.get('data', {})
        
        # Verificar se data é lista (alguns eventos vêm assim)
        if isinstance(message_data, list):
            if len(message_data) == 0:
                logger.warning("⚠️ Lista de mensagens vazia")
                return {'status': 'ignored', 'reason': 'empty_list'}
            message_data = message_data[0]  # Pegar primeira mensagem
        
        # Extrair chat_id e mensagem
        chat_id = message_data.get('key', {}).get('remoteJid')
        from_me = message_data.get('key', {}).get('fromMe', False)
        message = message_data.get('message', {}).get('conversation')
        
        # IGNORAR MENSAGENS ENVIADAS PELO PRÓPRIO BOT
        if from_me:
            logger.info(f"⏭️ Mensagem própria ignorada: {chat_id}")
            return {'status': 'ignored', 'reason': 'own_message'}
        
        # Tentar outros formatos de mensagem
        if not message:
            msg_obj = message_data.get('message', {})
            message = (
                msg_obj.get('extendedTextMessage', {}).get('text') or
                msg_obj.get('imageMessage', {}).get('caption') or
                msg_obj.get('videoMessage', {}).get('caption')
            )
        
        # Validações básicas
        if not chat_id or not message:
            logger.warning(f"⚠️ Webhook sem chat_id ou message | event: {event}")
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
