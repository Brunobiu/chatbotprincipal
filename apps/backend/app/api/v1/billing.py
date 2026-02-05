from fastapi import APIRouter, Request, HTTPException
import os
import json
import stripe

from app.core.config import (
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    STRIPE_PRICE_LOOKUP_KEY,
)

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
async def stripe_webhook(request: Request):
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

        # Eventos básicos tratados (apenas log por enquanto)
        if event_type == "checkout.session.completed":
            print("🔔 checkout.session.completed", data_obj.get("id"))
        elif event_type == "invoice.payment_succeeded":
            print("🔔 invoice.payment_succeeded", data_obj.get("id"))
        elif event_type and event_type.startswith("customer.subscription"):
            print(f"🔔 {event_type}", data_obj.get("id"))

        # TODO: atualizar banco: criar cliente, subscription, marcar pagamento aprovado, etc.
        return {"status": "success"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

