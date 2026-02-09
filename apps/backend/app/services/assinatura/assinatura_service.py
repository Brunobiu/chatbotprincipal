"""
Service para gerenciar informações de assinatura
"""
import logging
import stripe
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional, Dict

from app.db.models.cliente import Cliente
from app.core.config import STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

stripe.api_key = STRIPE_SECRET_KEY or os.getenv("STRIPE_SECRET_KEY")


class AssinaturaService:
    """Service para gerenciar assinatura do cliente"""
    
    @staticmethod
    def obter_info_assinatura(db: Session, cliente_id: int) -> Dict:
        """
        Obtém informações da assinatura do cliente
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            
        Returns:
            Dict com informações da assinatura:
            - status: ativa, cancelada, expirada, pendente
            - dias_restantes: dias até próxima cobrança ou expiração
            - plano_atual: mensal, trimestral, anual
            - data_proxima_cobranca: data da próxima cobrança
            - valor_mensal: valor em reais
            - pode_pagar_mais_mes: se pode pagar mais um mês (plano mensal)
        """
        # Buscar cliente
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if not cliente:
            raise ValueError("Cliente não encontrado")
        
        # Valores padrão
        info = {
            "status": "pendente",
            "dias_restantes": 0,
            "plano_atual": "mensal",
            "data_proxima_cobranca": None,
            "valor_mensal": 0.0,
            "pode_pagar_mais_mes": False,
            "stripe_customer_id": cliente.stripe_customer_id,
            "stripe_subscription_id": cliente.stripe_subscription_id
        }
        
        # Se não tem subscription no Stripe, retornar pendente
        if not cliente.stripe_subscription_id:
            logger.info(f"Cliente {cliente_id} não tem subscription no Stripe")
            return info
        
        try:
            # Buscar subscription no Stripe
            subscription = stripe.Subscription.retrieve(cliente.stripe_subscription_id)
            
            # Status da subscription
            stripe_status = subscription.get("status")
            
            # Mapear status do Stripe para nosso status
            if stripe_status == "active":
                info["status"] = "ativa"
            elif stripe_status == "canceled":
                info["status"] = "cancelada"
            elif stripe_status in ["past_due", "unpaid"]:
                info["status"] = "expirada"
            else:
                info["status"] = "pendente"
            
            # Data da próxima cobrança (current_period_end)
            current_period_end = subscription.get("current_period_end")
            if current_period_end:
                data_proxima_cobranca = datetime.fromtimestamp(current_period_end)
                info["data_proxima_cobranca"] = data_proxima_cobranca.isoformat()
                
                # Calcular dias restantes
                dias_restantes = (data_proxima_cobranca - datetime.utcnow()).days
                info["dias_restantes"] = max(0, dias_restantes)
            
            # Buscar informações do plano
            items = subscription.get("items", {}).get("data", [])
            if items:
                price = items[0].get("price", {})
                
                # Valor
                amount = price.get("unit_amount", 0)
                info["valor_mensal"] = amount / 100  # Stripe retorna em centavos
                
                # Intervalo (mensal, trimestral, anual)
                interval = price.get("recurring", {}).get("interval")
                interval_count = price.get("recurring", {}).get("interval_count", 1)
                
                if interval == "month":
                    if interval_count == 1:
                        info["plano_atual"] = "mensal"
                        info["pode_pagar_mais_mes"] = True
                    elif interval_count == 3:
                        info["plano_atual"] = "trimestral"
                    elif interval_count == 12:
                        info["plano_atual"] = "anual"
                elif interval == "year":
                    info["plano_atual"] = "anual"
            
            logger.info(f"Informações de assinatura obtidas para cliente {cliente_id}: {info['status']}, {info['dias_restantes']} dias restantes")
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao buscar subscription no Stripe: {e}")
            # Retornar info padrão em caso de erro
        
        return info
    
    @staticmethod
    def criar_sessao_pagamento_mensal(db: Session, cliente_id: int) -> str:
        """
        Cria sessão de pagamento para pagar mais um mês
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            
        Returns:
            URL da sessão de checkout
        """
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if not cliente:
            raise ValueError("Cliente não encontrado")
        
        if not cliente.stripe_customer_id:
            raise ValueError("Cliente não tem customer_id no Stripe")
        
        try:
            # Buscar price_id do plano mensal
            price_id = os.getenv("STRIPE_PRICE_ID")
            if not price_id:
                # Buscar pelo lookup_key
                lookup_key = os.getenv("STRIPE_PRICE_LOOKUP_KEY", "monthly_plan")
                prices = stripe.Price.list(lookup_keys=[lookup_key])
                if not prices.data:
                    raise ValueError(f"Plano mensal não encontrado (lookup_key: {lookup_key})")
                price_id = prices.data[0].id
            
            # Criar sessão de checkout
            your_domain = os.getenv("YOUR_DOMAIN", "http://localhost:3000")
            session = stripe.checkout.Session.create(
                customer=cliente.stripe_customer_id,
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=your_domain + "/dashboard?payment=success",
                cancel_url=your_domain + "/dashboard?payment=canceled",
            )
            
            logger.info(f"Sessão de pagamento criada para cliente {cliente_id}: {session.id}")
            
            return session.url
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao criar sessão de pagamento: {e}")
            raise ValueError(f"Erro ao criar sessão de pagamento: {str(e)}")
