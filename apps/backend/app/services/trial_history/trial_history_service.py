"""
Serviço para gerenciar histórico de trials
Proteção Anti-Abuso
"""
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.trial_history import TrialHistory
from app.db.models.cliente import Cliente
import logging

logger = logging.getLogger(__name__)


class TrialHistoryService:
    
    @staticmethod
    def registrar_trial_usado(
        db: Session,
        whatsapp_number: str,
        email: str,
        ip_cadastro: str = None,
        device_fingerprint: str = None
    ) -> TrialHistory:
        """
        Registra que um número WhatsApp já usou o trial
        
        Args:
            db: Sessão do banco
            whatsapp_number: Número do WhatsApp
            email: E-mail do cliente
            ip_cadastro: IP usado no cadastro
            device_fingerprint: Fingerprint do dispositivo
            
        Returns:
            TrialHistory criado
        """
        # Verificar se já existe
        existente = db.query(TrialHistory).filter(
            TrialHistory.whatsapp_number == whatsapp_number
        ).first()
        
        if existente:
            logger.info(f"Trial já registrado para {whatsapp_number}")
            return existente
        
        # Criar novo registro
        trial_history = TrialHistory(
            whatsapp_number=whatsapp_number,
            email=email,
            ip_cadastro=ip_cadastro,
            device_fingerprint=device_fingerprint,
            used_at=datetime.utcnow()
        )
        
        db.add(trial_history)
        db.commit()
        db.refresh(trial_history)
        
        logger.info(f"✅ Trial registrado no histórico: {whatsapp_number}")
        return trial_history
    
    @staticmethod
    def verificar_trial_usado(db: Session, whatsapp_number: str) -> bool:
        """
        Verifica se um número WhatsApp já usou o trial
        
        Args:
            db: Sessão do banco
            whatsapp_number: Número do WhatsApp
            
        Returns:
            True se já usou, False caso contrário
        """
        trial = db.query(TrialHistory).filter(
            TrialHistory.whatsapp_number == whatsapp_number
        ).first()
        
        return trial is not None
    
    @staticmethod
    def registrar_trials_expirados(db: Session):
        """
        Registra no histórico todos os clientes com trial expirado
        que ainda não foram registrados
        
        Deve ser executado periodicamente (cron job)
        """
        from datetime import datetime
        
        # Buscar clientes com trial expirado e número WhatsApp
        clientes_expirados = db.query(Cliente).filter(
            Cliente.subscription_status.in_(['expired', 'active', 'canceled']),
            Cliente.whatsapp_number.isnot(None),
            Cliente.trial_ends_at < datetime.utcnow()
        ).all()
        
        registrados = 0
        for cliente in clientes_expirados:
            # Verificar se já está no histórico
            if not TrialHistoryService.verificar_trial_usado(db, cliente.whatsapp_number):
                TrialHistoryService.registrar_trial_usado(
                    db=db,
                    whatsapp_number=cliente.whatsapp_number,
                    email=cliente.email,
                    ip_cadastro=cliente.ip_cadastro,
                    device_fingerprint=cliente.device_fingerprint
                )
                registrados += 1
        
        logger.info(f"✅ {registrados} trials registrados no histórico")
        return registrados
