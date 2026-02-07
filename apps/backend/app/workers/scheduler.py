"""
Scheduler para jobs agendados
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.session import SessionLocal
from app.services.fallback import FallbackService

logger = logging.getLogger(__name__)

# Criar scheduler global
scheduler = BackgroundScheduler()


def verificar_timeout_24h_job():
    """
    Job que verifica conversas aguardando há mais de 24h
    Executa a cada 1 hora
    """
    logger.info("[SCHEDULER] Iniciando verificação de timeout 24h")
    
    db = SessionLocal()
    try:
        conversas_retornadas = FallbackService.verificar_timeout_24h(db)
        
        if conversas_retornadas:
            logger.info(f"[SCHEDULER] {len(conversas_retornadas)} conversas retornaram ao modo automático")
        else:
            logger.info("[SCHEDULER] Nenhuma conversa com timeout 24h encontrada")
            
    except Exception as e:
        logger.error(f"[SCHEDULER] Erro ao verificar timeout 24h: {e}", exc_info=True)
    finally:
        db.close()


def iniciar_scheduler():
    """
    Inicializa o scheduler e adiciona os jobs
    """
    logger.info("[SCHEDULER] Inicializando scheduler de jobs")
    
    # Adicionar job de verificação de timeout 24h (executa a cada 1 hora)
    scheduler.add_job(
        func=verificar_timeout_24h_job,
        trigger=IntervalTrigger(hours=1),
        id='verificar_timeout_24h',
        name='Verificar timeout 24h de conversas aguardando humano',
        replace_existing=True
    )
    
    # Iniciar scheduler
    scheduler.start()
    logger.info("[SCHEDULER] Scheduler iniciado com sucesso")
    logger.info("[SCHEDULER] Job 'verificar_timeout_24h' agendado para executar a cada 1 hora")


def parar_scheduler():
    """
    Para o scheduler
    """
    logger.info("[SCHEDULER] Parando scheduler")
    scheduler.shutdown()
    logger.info("[SCHEDULER] Scheduler parado")
