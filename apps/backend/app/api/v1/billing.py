from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
from app.services.email.email_service import EmailService
from app.services.assinatura.assinatura_service import AssinaturaService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stripe.api_key = STRIPE_SECRET_KEY or os.getenv("STRIPE_SECRET_KEY")

router = APIRouter()
security = HTTPBearer()


# Dependency para pegar cliente autenticado
def get_current_cliente(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency que valida o token JWT e retorna o cliente autenticado
    """
    from app.services.auth.auth_service import AuthService
    
    token = credentials.credentials
    payload = AuthService.validar_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado"
        )
    
    cliente_id = int(payload.get("sub"))
    cliente = ClienteService.buscar_por_id(db, cliente_id)
    
    if not cliente:
        raise HTTPException(
            status_code=401,
            detail="Cliente não encontrado"
        )
    
    return cliente


@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    """
    Cria uma sessão de Checkout (subscription) e retorna a URL para redirecionamento.
    Espera um JSON opcional: { "lookup_key": "<PRICE_LOOKUP_KEY>" } ou { "price_id": "<PRICE_ID>" }
    """
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    
    # Prioridade: 1) price_id do body, 2) STRIPE_PRICE_ID do env, 3) lookup_key
    price_id = body.get("price_id")
    if not price_id:
        price_id = os.getenv("STRIPE_PRICE_ID")
    
    lookup_key = body.get("lookup_key")
    if not lookup_key:
        lookup_key = STRIPE_PRICE_LOOKUP_KEY or os.getenv("STRIPE_PRICE_LOOKUP_KEY")
    
    try:
        # Se não tem price_id, busca pelo lookup_key
        if not price_id:
            if not lookup_key:
                raise HTTPException(status_code=400, detail="price_id ou lookup_key não encontrado")
            prices = stripe.Price.list(lookup_keys=[lookup_key], expand=["data.product"])
            if not prices.data:
                raise HTTPException(status_code=400, detail=f"Nenhum preço encontrado com lookup_key: {lookup_key}")
            price_id = prices.data[0].id

        your_domain = os.getenv("YOUR_DOMAIN", "http://localhost:3000")
        session = stripe.checkout.Session.create(
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=your_domain + "/?success=true&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=your_domain + "/?canceled=true",
        )
        return {"url": session.url, "id": session.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/assinatura/info")
async def obter_info_assinatura(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Retorna informações da assinatura do cliente autenticado
    
    Requer token JWT válido no header Authorization: Bearer <token>
    """
    try:
        info = AssinaturaService.obter_info_assinatura(db, cliente.id)
        return info
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao obter info de assinatura: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao obter informações da assinatura")


@router.post("/assinatura/pagar-mais-mes")
async def pagar_mais_mes(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Cria sessão de pagamento para pagar mais um mês
    
    Requer token JWT válido no header Authorization: Bearer <token>
    Retorna URL para checkout
    """
    try:
        url = AssinaturaService.criar_sessao_pagamento_mensal(db, cliente.id)
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar sessão de pagamento: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao criar sessão de pagamento")


@router.post("/checkout-pix")
async def criar_checkout_pix(
    payload: dict,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Cria checkout com PIX habilitado
    Task 18
    
    Body:
    {
        "price_id": "price_xxx",
        "plano": "mensal" | "trimestral" | "anual"
    }
    
    Retorna URL para checkout
    """
    try:
        price_id = payload.get("price_id")
        plano = payload.get("plano", "mensal")
        
        if not price_id:
            raise HTTPException(status_code=400, detail="price_id é obrigatório")
        
        resultado = AssinaturaService.criar_checkout_pix(
            db=db,
            cliente_id=cliente.id,
            price_id=price_id,
            plano=plano
        )
        
        return resultado
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar checkout PIX: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao criar checkout PIX")


@router.post("/checkout-debito")
async def criar_checkout_debito(
    payload: dict,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Cria checkout com cartão de débito habilitado
    Task 18
    
    Body:
    {
        "price_id": "price_xxx",
        "plano": "mensal" | "trimestral" | "anual"
    }
    
    Retorna URL para checkout
    """
    try:
        price_id = payload.get("price_id")
        plano = payload.get("plano", "mensal")
        
        if not price_id:
            raise HTTPException(status_code=400, detail="price_id é obrigatório")
        
        resultado = AssinaturaService.criar_checkout_debito(
            db=db,
            cliente_id=cliente.id,
            price_id=price_id,
            plano=plano
        )
        
        return resultado
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar checkout débito: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao criar checkout débito")


@router.get("/planos")
async def obter_planos():
    """
    Retorna todos os planos disponíveis com valores e descontos
    Task 19
    
    Retorna informações de planos: mensal, trimestral, anual
    """
    try:
        # Valor base mensal (ajustar conforme necessário)
        valor_base = float(os.getenv("VALOR_BASE_MENSAL", "97.00"))
        planos = AssinaturaService.obter_planos_disponiveis(valor_base)
        return planos
    except Exception as e:
        logger.error(f"Erro ao obter planos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao obter planos")


@router.post("/mudar-plano")
async def mudar_plano(
    payload: dict,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Muda plano do cliente com cálculo proporcional
    Task 19
    
    Body:
    {
        "novo_plano": "mensal" | "trimestral" | "anual",
        "price_id": "price_xxx"
    }
    
    Retorna informações da mudança
    """
    try:
        novo_plano = payload.get("novo_plano")
        price_id = payload.get("price_id")
        
        if not novo_plano or not price_id:
            raise HTTPException(status_code=400, detail="novo_plano e price_id são obrigatórios")
        
        if novo_plano not in ["mensal", "trimestral", "anual"]:
            raise HTTPException(status_code=400, detail="Plano inválido. Use: mensal, trimestral ou anual")
        
        resultado = AssinaturaService.mudar_plano(
            db=db,
            cliente_id=cliente.id,
            novo_plano=novo_plano,
            price_id=price_id
        )
        
        return resultado
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao mudar plano: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao mudar plano")


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
            
            # Enviar email com credenciais
            try:
                from app.core.config import settings
                dashboard_url = getattr(settings, 'DASHBOARD_URL', 'http://localhost:3000/login')
                
                email_enviado = EmailService.enviar_email_boas_vindas(
                    email_destino=cliente.email,
                    nome_cliente=cliente.nome,
                    senha=senha_plana,
                    dashboard_url=dashboard_url
                )
                
                if email_enviado:
                    logger.info(f"📧 Email de boas-vindas enviado para {cliente.email}")
                else:
                    logger.warning(f"⚠️ Falha ao enviar email para {cliente.email}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao enviar email: {str(e)}", exc_info=True)
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

