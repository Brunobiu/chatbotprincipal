"""
Serviço de Gestão de Vendas e Assinaturas
Gerencia transações, assinaturas Stripe e operações financeiras
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
import stripe

from app.core.config import settings
from app.db.models.cliente import Cliente, ClienteStatus

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class VendaService:
    """Serviço para gerenciar vendas e assinaturas"""
    
    @staticmethod
    def listar_transacoes(
        db: Session,
        status: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        cliente_id: Optional[int] = None,
        limite: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Lista todas as transações do Stripe
        """
        try:
            # Buscar charges do Stripe
            filtros = {"limit": limite}
            
            if data_inicio:
                filtros["created"] = {"gte": int(data_inicio.timestamp())}
            if data_fim:
                if "created" in filtros:
                    filtros["created"]["lte"] = int(data_fim.timestamp())
                else:
                    filtros["created"] = {"lte": int(data_fim.timestamp())}
            
            charges = stripe.Charge.list(**filtros)
            
            transacoes = []
            for charge in charges.data:
                # Buscar cliente no banco
                cliente = None
                if charge.customer:
                    cliente = db.query(Cliente).filter(
                        Cliente.stripe_customer_id == charge.customer
                    ).first()
                
                # Filtrar por cliente_id se especificado
                if cliente_id and (not cliente or cliente.id != cliente_id):
                    continue
                
                # Filtrar por status se especificado
                if status and charge.status != status:
                    continue
                
                transacoes.append({
                    "id": charge.id,
                    "valor": charge.amount / 100,  # Converter de centavos
                    "moeda": charge.currency.upper(),
                    "status": charge.status,
                    "descricao": charge.description or "Assinatura WhatsApp AI Bot",
                    "cliente_id": cliente.id if cliente else None,
                    "cliente_nome": cliente.nome if cliente else "Cliente não encontrado",
                    "cliente_email": cliente.email if cliente else charge.billing_details.email,
                    "data": datetime.fromtimestamp(charge.created),
                    "metodo_pagamento": charge.payment_method_details.type if charge.payment_method_details else None,
                    "reembolsado": charge.refunded,
                    "valor_reembolsado": charge.amount_refunded / 100 if charge.amount_refunded else 0
                })
            
            return {
                "transacoes": transacoes,
                "total": len(transacoes),
                "has_more": charges.has_more
            }
            
        except stripe.error.StripeError as e:
            return {
                "erro": str(e),
                "transacoes": [],
                "total": 0
            }
    
    @staticmethod
    def listar_assinaturas(
        db: Session,
        status: Optional[str] = None,
        limite: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Lista todas as assinaturas
        """
        try:
            # Buscar assinaturas do Stripe
            filtros = {"limit": limite}
            if status:
                filtros["status"] = status
            
            subscriptions = stripe.Subscription.list(**filtros)
            
            assinaturas = []
            for sub in subscriptions.data:
                # Buscar cliente no banco
                cliente = db.query(Cliente).filter(
                    Cliente.stripe_customer_id == sub.customer
                ).first()
                
                # Calcular próxima cobrança
                proxima_cobranca = None
                if sub.current_period_end:
                    proxima_cobranca = datetime.fromtimestamp(sub.current_period_end)
                
                # Valor da assinatura
                valor = 0
                if sub.items and sub.items.data:
                    valor = sub.items.data[0].price.unit_amount / 100
                
                assinaturas.append({
                    "id": sub.id,
                    "cliente_id": cliente.id if cliente else None,
                    "cliente_nome": cliente.nome if cliente else "Cliente não encontrado",
                    "cliente_email": cliente.email if cliente else None,
                    "status": sub.status,
                    "valor": valor,
                    "moeda": sub.currency.upper() if sub.currency else "BRL",
                    "intervalo": sub.items.data[0].price.recurring.interval if sub.items.data else "month",
                    "data_inicio": datetime.fromtimestamp(sub.start_date),
                    "proxima_cobranca": proxima_cobranca,
                    "cancelar_no_fim": sub.cancel_at_period_end,
                    "data_cancelamento": datetime.fromtimestamp(sub.canceled_at) if sub.canceled_at else None
                })
            
            return {
                "assinaturas": assinaturas,
                "total": len(assinaturas),
                "has_more": subscriptions.has_more
            }
            
        except stripe.error.StripeError as e:
            return {
                "erro": str(e),
                "assinaturas": [],
                "total": 0
            }
    
    @staticmethod
    def cancelar_assinatura(
        db: Session,
        assinatura_id: str,
        imediato: bool = False
    ) -> Dict[str, Any]:
        """
        Cancela uma assinatura
        """
        try:
            if imediato:
                # Cancelar imediatamente
                subscription = stripe.Subscription.delete(assinatura_id)
            else:
                # Cancelar no fim do período
                subscription = stripe.Subscription.modify(
                    assinatura_id,
                    cancel_at_period_end=True
                )
            
            # Atualizar cliente no banco
            cliente = db.query(Cliente).filter(
                Cliente.stripe_subscription_id == assinatura_id
            ).first()
            
            if cliente:
                if imediato:
                    cliente.status = ClienteStatus.SUSPENSO
                    cliente.stripe_status = "canceled"
                else:
                    cliente.stripe_status = "canceling"
                db.commit()
            
            return {
                "sucesso": True,
                "mensagem": "Assinatura cancelada com sucesso",
                "assinatura_id": assinatura_id,
                "cancelamento_imediato": imediato
            }
            
        except stripe.error.StripeError as e:
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    @staticmethod
    def reativar_assinatura(
        db: Session,
        assinatura_id: str
    ) -> Dict[str, Any]:
        """
        Reativa uma assinatura cancelada (antes do fim do período)
        """
        try:
            subscription = stripe.Subscription.modify(
                assinatura_id,
                cancel_at_period_end=False
            )
            
            # Atualizar cliente no banco
            cliente = db.query(Cliente).filter(
                Cliente.stripe_subscription_id == assinatura_id
            ).first()
            
            if cliente:
                cliente.status = ClienteStatus.ATIVO
                cliente.stripe_status = subscription.status
                db.commit()
            
            return {
                "sucesso": True,
                "mensagem": "Assinatura reativada com sucesso",
                "assinatura_id": assinatura_id
            }
            
        except stripe.error.StripeError as e:
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    @staticmethod
    def reembolsar_transacao(
        db: Session,
        charge_id: str,
        valor: Optional[float] = None,
        motivo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reembolsa uma transação (total ou parcial)
        """
        try:
            params = {"charge": charge_id}
            
            if valor:
                # Reembolso parcial (converter para centavos)
                params["amount"] = int(valor * 100)
            
            if motivo:
                params["reason"] = motivo
            
            refund = stripe.Refund.create(**params)
            
            return {
                "sucesso": True,
                "mensagem": "Reembolso processado com sucesso",
                "refund_id": refund.id,
                "valor_reembolsado": refund.amount / 100,
                "status": refund.status
            }
            
        except stripe.error.StripeError as e:
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    @staticmethod
    def obter_historico_cliente(
        db: Session,
        cliente_id: int
    ) -> Dict[str, Any]:
        """
        Obtém histórico completo de pagamentos de um cliente
        """
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if not cliente or not cliente.stripe_customer_id:
            return {
                "erro": "Cliente não encontrado ou sem histórico de pagamentos",
                "transacoes": [],
                "assinaturas": []
            }
        
        try:
            # Buscar charges do cliente
            charges = stripe.Charge.list(
                customer=cliente.stripe_customer_id,
                limit=100
            )
            
            transacoes = []
            for charge in charges.data:
                transacoes.append({
                    "id": charge.id,
                    "valor": charge.amount / 100,
                    "moeda": charge.currency.upper(),
                    "status": charge.status,
                    "descricao": charge.description,
                    "data": datetime.fromtimestamp(charge.created),
                    "reembolsado": charge.refunded,
                    "valor_reembolsado": charge.amount_refunded / 100 if charge.amount_refunded else 0
                })
            
            # Buscar assinaturas do cliente
            subscriptions = stripe.Subscription.list(
                customer=cliente.stripe_customer_id,
                limit=100
            )
            
            assinaturas = []
            for sub in subscriptions.data:
                valor = 0
                if sub.items and sub.items.data:
                    valor = sub.items.data[0].price.unit_amount / 100
                
                assinaturas.append({
                    "id": sub.id,
                    "status": sub.status,
                    "valor": valor,
                    "moeda": sub.currency.upper() if sub.currency else "BRL",
                    "data_inicio": datetime.fromtimestamp(sub.start_date),
                    "proxima_cobranca": datetime.fromtimestamp(sub.current_period_end) if sub.current_period_end else None,
                    "cancelar_no_fim": sub.cancel_at_period_end
                })
            
            return {
                "cliente": {
                    "id": cliente.id,
                    "nome": cliente.nome,
                    "email": cliente.email,
                    "status": cliente.status.value
                },
                "transacoes": transacoes,
                "assinaturas": assinaturas,
                "total_transacoes": len(transacoes),
                "total_assinaturas": len(assinaturas)
            }
            
        except stripe.error.StripeError as e:
            return {
                "erro": str(e),
                "transacoes": [],
                "assinaturas": []
            }
