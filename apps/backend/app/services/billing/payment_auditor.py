"""
Serviço de Auditoria de Pagamentos (FASE 6)
Loga e valida todas transações
"""
from sqlalchemy.orm import Session
from app.db.models.payment_log import PaymentLog
from datetime import datetime
from typing import Optional, Dict
import logging
import stripe

logger = logging.getLogger("payments")


class PaymentAuditor:
    """Auditoria e validação de pagamentos"""
    
    @staticmethod
    def log_payment(
        db: Session,
        cliente_id: int,
        amount: float,
        status: str,
        stripe_payment_intent_id: Optional[str] = None,
        stripe_subscription_id: Optional[str] = None,
        stripe_invoice_id: Optional[str] = None,
        stripe_customer_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        description: Optional[str] = None,
        event_type: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        webhook_event_id: Optional[str] = None
    ) -> PaymentLog:
        """
        Loga transação de pagamento
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            amount: Valor em reais
            status: Status (pending, succeeded, failed, cancelled)
            ... outros parâmetros opcionais
            
        Returns:
            PaymentLog criado
        """
        log = PaymentLog(
            cliente_id=cliente_id,
            stripe_payment_intent_id=stripe_payment_intent_id,
            stripe_subscription_id=stripe_subscription_id,
            stripe_invoice_id=stripe_invoice_id,
            stripe_customer_id=stripe_customer_id,
            amount=amount,
            currency="brl",
            status=status,
            plan_id=plan_id,
            description=description,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            webhook_event_id=webhook_event_id
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        logger.info(
            f"💰 Pagamento logado: Cliente {cliente_id} - "
            f"R$ {amount:.2f} - Status: {status}"
        )
        
        return log
    
    @staticmethod
    def update_payment_status(
        db: Session,
        stripe_payment_intent_id: str,
        new_status: str,
        webhook_event_id: Optional[str] = None
    ) -> Optional[PaymentLog]:
        """
        Atualiza status de pagamento
        
        Args:
            db: Sessão do banco
            stripe_payment_intent_id: ID do payment intent
            new_status: Novo status
            webhook_event_id: ID do evento webhook (previne replay)
            
        Returns:
            PaymentLog atualizado ou None
        """
        log = db.query(PaymentLog).filter(
            PaymentLog.stripe_payment_intent_id == stripe_payment_intent_id
        ).first()
        
        if not log:
            logger.warning(
                f"⚠️ Payment log não encontrado: {stripe_payment_intent_id}"
            )
            return None
        
        # Verificar se já processamos este webhook (proteção contra replay)
        if webhook_event_id and log.webhook_event_id == webhook_event_id:
            logger.warning(
                f"⚠️ Webhook duplicado ignorado: {webhook_event_id}"
            )
            return log
        
        # Atualizar
        log.status = new_status
        log.webhook_received = True
        log.webhook_received_at = datetime.utcnow()
        
        if webhook_event_id:
            log.webhook_event_id = webhook_event_id
        
        db.commit()
        db.refresh(log)
        
        logger.info(
            f"✅ Status atualizado: {stripe_payment_intent_id} -> {new_status}"
        )
        
        return log
    
    @staticmethod
    def validate_payment_amount(
        payment_intent_id: str,
        expected_amount: float,
        tolerance: float = 0.01
    ) -> bool:
        """
        Valida que valor do payment intent está correto
        
        Args:
            payment_intent_id: ID do payment intent
            expected_amount: Valor esperado em reais
            tolerance: Tolerância para diferença (padrão 0.01)
            
        Returns:
            True se válido, False caso contrário
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Converter centavos para reais
            actual_amount = intent.amount / 100
            
            # Verificar diferença
            diff = abs(actual_amount - expected_amount)
            
            if diff > tolerance:
                logger.error(
                    f"🚨 VALOR INCORRETO! "
                    f"Payment Intent: {payment_intent_id} | "
                    f"Esperado: R$ {expected_amount:.2f} | "
                    f"Recebido: R$ {actual_amount:.2f} | "
                    f"Diferença: R$ {diff:.2f}"
                )
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao validar payment intent: {e}")
            return False
    
    @staticmethod
    def check_replay_attack(
        db: Session,
        webhook_event_id: str
    ) -> bool:
        """
        Verifica se webhook já foi processado (proteção contra replay)
        
        Args:
            db: Sessão do banco
            webhook_event_id: ID do evento webhook
            
        Returns:
            True se é replay (já processado), False se é novo
        """
        existing = db.query(PaymentLog).filter(
            PaymentLog.webhook_event_id == webhook_event_id
        ).first()
        
        if existing:
            logger.warning(
                f"🚨 REPLAY ATTACK DETECTADO! "
                f"Webhook {webhook_event_id} já foi processado"
            )
            return True
        
        return False
    
    @staticmethod
    def get_cliente_payments(
        db: Session,
        cliente_id: int,
        limit: int = 50
    ) -> list:
        """
        Lista pagamentos de um cliente
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            limit: Limite de resultados
            
        Returns:
            Lista de PaymentLog
        """
        return db.query(PaymentLog).filter(
            PaymentLog.cliente_id == cliente_id
        ).order_by(
            PaymentLog.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_failed_payments(
        db: Session,
        days: int = 7,
        limit: int = 100
    ) -> list:
        """
        Lista pagamentos falhados recentes
        
        Args:
            db: Sessão do banco
            days: Últimos N dias
            limit: Limite de resultados
            
        Returns:
            Lista de PaymentLog
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        return db.query(PaymentLog).filter(
            PaymentLog.status == "failed",
            PaymentLog.created_at >= cutoff
        ).order_by(
            PaymentLog.created_at.desc()
        ).limit(limit).all()
