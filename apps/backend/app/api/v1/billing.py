from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import json
import stripe
import logging

from app.core.config import (
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    STRIPE_PRICE_LOOKUP_KEY,
)
from app.db.session import get_db
from app.services.clientes.cliente_service import ClienteService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stripe.api_key = STRIPE_SECRET_KEY or os.getenv("STRIPE_SECRET_KEY")

router = APIRouter()


@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    """
    Cria uma sessão de Checkout (subscription) e retorna a URL para redirecionamento.
    Espera um JSON opcional: { "lookup_key": "<PRICE_LOOKUP_KEY>" }
    """
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    lookup_key = body.get("lookup_key") or STRIPE_PRICE_LOOKUP_KEY or os.getenv("STRIPE_PRICE_LOOKUP_KEY")
    if not lookup_key:
        raise HTTPException(status_code=400, detail="lookup_key não encontrado")

    try:
        prices = stripe.Price.list(lookup_keys=[lookup_key], expand=["data.product"])
        price_id = prices.data[0].id

        your_domain = os.getenv("YOUR_DOMAIN", "http://localhost:3000")
        session = stripe.checkout.Session.create(
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=your_domain + "/?success=true&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=your_domain + "/?canceled=true",
        )
        return {"url": session.url, "id": session.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create-portal-session")
async def create_portal_session(payload: dict):
    """
    Cria uma sessão do Billing Portal a partir do checkout session id.
    Espera JSON: { "session_id": "<CHECKOUT_SESSION_ID>" }
    """
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id obrigatório")
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        portal = stripe.billing_portal.Session.create(
            customer=checkout_session.customer, return_url=os.getenv("YOUR_DOMAIN", "http://localhost:3000")
        )
        return {"url": portal.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para receber webhooks do Stripe. Valida assinatura se STRIPE_WEBHOOK_SECRET estiver configurado.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = STRIPE_WEBHOOK_SECRET or os.getenv("STRIPE_WEBHOOK_SECRET", "")

    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=webhook_secret)
        else:
            event = json.loads(payload)

        event_type = event.get("type")
        data_obj = event.get("data", {}).get("object", {})

        logger.info(f"📥 Webhook recebido: {event_type} | ID: {data_obj.get('id')}")

        # Processar eventos do Stripe
        if event_type == "checkout.session.completed":
            await processar_checkout_completo(db, data_obj)
        
        elif event_type == "invoice.payment_succeeded":
            await processar_pagamento_sucesso(db, data_obj)
        
        elif event_type == "customer.subscription.updated":
            await processar_subscription_atualizada(db, data_obj)
        
        elif event_type == "customer.subscription.deleted":
            await processar_subscription_cancelada(db, data_obj)

        return {"status": "success"}

    except ValueError as e:
        logger.error(f"❌ Payload inválido: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"❌ Assinatura inválida: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def processar_checkout_completo(db: Session, session_data: dict):
    """
    Processa evento checkout.session.completed
    Cria cliente no banco quando pagamento é aprovado
    """
    try:
        # Extrair dados do checkout session
        customer_email = session_data.get("customer_email")
        customer_name = session_data.get("customer_details", {}).get("name") or "Cliente"
        customer_phone = session_data.get("customer_details", {}).get("phone")
        stripe_customer_id = session_data.get("customer")
        stripe_subscription_id = session_data.get("subscription")
        
        if not customer_email:
            logger.warning("⚠️ Checkout sem email do cliente")
            return
        
        if not stripe_subscription_id:
            logger.warning("⚠️ Checkout sem subscription ID")
            return
        
        # Buscar detalhes da subscription no Stripe
        subscription = stripe.Subscription.retrieve(stripe_subscription_id)
        subscription_status = subscription.get("status", "incomplete")
        
        logger.info(f"📧 Criando cliente: {customer_email}")
        
        # Criar ou atualizar cliente
        cliente, senha_plana = ClienteService.criar_cliente_from_stripe(
            db=db,
            email=customer_email,
            nome=customer_name,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            stripe_status=subscription_status,
            telefone=customer_phone
        )
        
        if senha_plana:
            logger.info(f"✅ Cliente criado: ID={cliente.id} | Email={cliente.email}")
            logger.info(f"🔑 Senha gerada: {senha_plana}")
            # TODO FASE 5: Enviar email com credenciais
            logger.info(f"📧 TODO: Enviar email para {cliente.email} com senha: {senha_plana}")
        else:
            logger.info(f"✅ Cliente atualizado: ID={cliente.id} | Email={cliente.email}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar checkout: {str(e)}", exc_info=True)
        raise


async def processar_pagamento_sucesso(db: Session, invoice_data: dict):
    """
    Processa evento invoice.payment_succeeded
    Atualiza status da subscription
    """
    try:
        stripe_subscription_id = invoice_data.get("subscription")
        
        if not stripe_subscription_id:
            logger.warning("⚠️ Invoice sem subscription ID")
            return
        
        logger.info(f"💰 Pagamento aprovado para subscription: {stripe_subscription_id}")
        
        # Atualizar status da subscription
        cliente = ClienteService.atualizar_status_subscription(
            db=db,
            stripe_subscription_id=stripe_subscription_id,
            novo_status="active"
        )
        
        if cliente:
            logger.info(f"✅ Status atualizado: Cliente ID={cliente.id} | Status={cliente.status}")
        else:
            logger.warning(f"⚠️ Cliente não encontrado para subscription: {stripe_subscription_id}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar pagamento: {str(e)}", exc_info=True)
        raise


async def processar_subscription_atualizada(db: Session, subscription_data: dict):
    """
    Processa evento customer.subscription.updated
    Atualiza status da subscription
    """
    try:
        stripe_subscription_id = subscription_data.get("id")
        novo_status = subscription_data.get("status")
        
        if not stripe_subscription_id:
            logger.warning("⚠️ Subscription sem ID")
            return
        
        logger.info(f"🔄 Subscription atualizada: {stripe_subscription_id} | Status: {novo_status}")
        
        # Atualizar status
        cliente = ClienteService.atualizar_status_subscription(
            db=db,
            stripe_subscription_id=stripe_subscription_id,
            novo_status=novo_status
        )
        
        if cliente:
            logger.info(f"✅ Status atualizado: Cliente ID={cliente.id} | Status={cliente.status}")
        else:
            logger.warning(f"⚠️ Cliente não encontrado para subscription: {stripe_subscription_id}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar atualização: {str(e)}", exc_info=True)
        raise


async def processar_subscription_cancelada(db: Session, subscription_data: dict):
    """
    Processa evento customer.subscription.deleted
    Suspende cliente
    """
    try:
        stripe_subscription_id = subscription_data.get("id")
        
        if not stripe_subscription_id:
            logger.warning("⚠️ Subscription sem ID")
            return
        
        logger.info(f"❌ Subscription cancelada: {stripe_subscription_id}")
        
        # Suspender cliente
        cliente = ClienteService.atualizar_status_subscription(
            db=db,
            stripe_subscription_id=stripe_subscription_id,
            novo_status="canceled"
        )
        
        if cliente:
            logger.info(f"✅ Cliente suspenso: ID={cliente.id} | Status={cliente.status}")
        else:
            logger.warning(f"⚠️ Cliente não encontrado para subscription: {stripe_subscription_id}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar cancelamento: {str(e)}", exc_info=True)
        raise

