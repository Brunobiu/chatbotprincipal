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
    
    @staticmethod
    def criar_checkout_pix(
        db: Session,
        cliente_id: int,
        price_id: str,
        plano: str = "mensal"
    ) -> Dict:
        """
        Cria checkout com PIX habilitado
        Task 18
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            price_id: ID do preço no Stripe
            plano: mensal, trimestral ou anual
            
        Returns:
            Dict com url do checkout e session_id
        """
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if not cliente:
            raise ValueError("Cliente não encontrado")
        
        try:
            your_domain = os.getenv("YOUR_DOMAIN", "http://localhost:3000")
            
            # Criar sessão com PIX habilitado
            session_params = {
                "line_items": [{"price": price_id, "quantity": 1}],
                "mode": "subscription",
                "success_url": your_domain + f"/dashboard?payment=success&plano={plano}",
                "cancel_url": your_domain + f"/dashboard?payment=canceled",
                "payment_method_types": ["card", "boleto"],  # PIX via boleto no Brasil
                "customer_email": cliente.email,
            }
            
            # Se já tem customer_id, usar
            if cliente.stripe_customer_id:
                session_params["customer"] = cliente.stripe_customer_id
            
            session = stripe.checkout.Session.create(**session_params)
            
            logger.info(f"Checkout PIX criado para cliente {cliente_id}: {session.id}")
            
            return {
                "url": session.url,
                "session_id": session.id,
                "plano": plano
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao criar checkout PIX: {e}")
            raise ValueError(f"Erro ao criar checkout PIX: {str(e)}")
    
    @staticmethod
    def criar_checkout_debito(
        db: Session,
        cliente_id: int,
        price_id: str,
        plano: str = "mensal"
    ) -> Dict:
        """
        Cria checkout com cartão de débito habilitado
        Task 18
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            price_id: ID do preço no Stripe
            plano: mensal, trimestral ou anual
            
        Returns:
            Dict com url do checkout e session_id
        """
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if not cliente:
            raise ValueError("Cliente não encontrado")
        
        try:
            your_domain = os.getenv("YOUR_DOMAIN", "http://localhost:3000")
            
            # Criar sessão com débito habilitado
            session_params = {
                "line_items": [{"price": price_id, "quantity": 1}],
                "mode": "subscription",
                "success_url": your_domain + f"/dashboard?payment=success&plano={plano}",
                "cancel_url": your_domain + f"/dashboard?payment=canceled",
                "payment_method_types": ["card"],  # Cartão (crédito e débito)
                "customer_email": cliente.email,
            }
            
            # Se já tem customer_id, usar
            if cliente.stripe_customer_id:
                session_params["customer"] = cliente.stripe_customer_id
            
            session = stripe.checkout.Session.create(**session_params)
            
            logger.info(f"Checkout débito criado para cliente {cliente_id}: {session.id}")
            
            return {
                "url": session.url,
                "session_id": session.id,
                "plano": plano
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao criar checkout débito: {e}")
            raise ValueError(f"Erro ao criar checkout débito: {str(e)}")
    
    @staticmethod
    def calcular_desconto(plano: str, valor_base: float) -> Dict:
        """
        Calcula desconto baseado no plano
        Task 19
        
        Args:
            plano: mensal, trimestral ou anual
            valor_base: valor mensal base
            
        Returns:
            Dict com valor_original, valor_com_desconto, desconto_percentual
        """
        descontos = {
            "mensal": 0,
            "trimestral": 10,
            "anual": 20
        }
        
        multiplicadores = {
            "mensal": 1,
            "trimestral": 3,
            "anual": 12
        }
        
        desconto_percentual = descontos.get(plano, 0)
        multiplicador = multiplicadores.get(plano, 1)
        
        valor_original = valor_base * multiplicador
        valor_com_desconto = valor_original * (1 - desconto_percentual / 100)
        
        return {
            "valor_original": round(valor_original, 2),
            "valor_com_desconto": round(valor_com_desconto, 2),
            "desconto_percentual": desconto_percentual,
            "economia": round(valor_original - valor_com_desconto, 2)
        }
    
    @staticmethod
    def mudar_plano(
        db: Session,
        cliente_id: int,
        novo_plano: str,
        price_id: str
    ) -> Dict:
        """
        Muda plano do cliente com cálculo proporcional
        Task 19
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            novo_plano: mensal, trimestral ou anual
            price_id: ID do novo preço no Stripe
            
        Returns:
            Dict com informações da mudança
        """
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if not cliente:
            raise ValueError("Cliente não encontrado")
        
        if not cliente.stripe_subscription_id:
            raise ValueError("Cliente não tem assinatura ativa")
        
        try:
            # Buscar subscription atual
            subscription = stripe.Subscription.retrieve(cliente.stripe_subscription_id)
            
            # Atualizar subscription com novo preço
            # Stripe faz cálculo proporcional automaticamente (proration)
            updated_subscription = stripe.Subscription.modify(
                cliente.stripe_subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': price_id,
                }],
                proration_behavior='create_prorations',  # Criar crédito/débito proporcional
            )
            
            logger.info(f"Plano alterado para cliente {cliente_id}: {novo_plano}")
            
            # Calcular informações da mudança
            current_period_end = datetime.fromtimestamp(updated_subscription.get("current_period_end"))
            dias_restantes = (current_period_end - datetime.utcnow()).days
            
            return {
                "sucesso": True,
                "novo_plano": novo_plano,
                "subscription_id": updated_subscription.id,
                "status": updated_subscription.get("status"),
                "proxima_cobranca": current_period_end.isoformat(),
                "dias_restantes": max(0, dias_restantes),
                "mensagem": f"Plano alterado para {novo_plano} com sucesso. Ajuste proporcional será aplicado na próxima fatura."
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao mudar plano: {e}")
            raise ValueError(f"Erro ao mudar plano: {str(e)}")
    
    @staticmethod
    def obter_planos_disponiveis(valor_base: float = 97.00) -> Dict:
        """
        Retorna todos os planos disponíveis com valores e descontos
        Task 19
        
        Args:
            valor_base: valor mensal base (padrão R$ 97,00)
            
        Returns:
            Dict com informações de todos os planos
        """
        planos = {}
        
        for plano in ["mensal", "trimestral", "anual"]:
            calculo = AssinaturaService.calcular_desconto(plano, valor_base)
            
            planos[plano] = {
                "nome": plano.capitalize(),
                "valor_original": calculo["valor_original"],
                "valor_final": calculo["valor_com_desconto"],
                "desconto_percentual": calculo["desconto_percentual"],
                "economia": calculo["economia"],
                "valor_mensal_equivalente": round(calculo["valor_com_desconto"] / (1 if plano == "mensal" else 3 if plano == "trimestral" else 12), 2)
            }
        
        return planos
