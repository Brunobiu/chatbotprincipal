# FASE 6 - Segurança de Pagamentos

## 🎯 Objetivo
Garantir que NENHUM dado de pagamento seja exposto no frontend e que valores sempre venham do backend.

---

## 📋 Auditoria Atual

### ✅ Já Implementado
- Stripe integrado no backend
- Webhook signature verification
- Chaves em variáveis de ambiente

### ⚠️ Verificar

#### 1. Frontend NUNCA deve ter chaves secretas
```bash
# Procurar por chaves expostas
grep -r "sk_" apps/frontend/
grep -r "STRIPE_SECRET" apps/frontend/
```

**Regra:** Frontend só pode ter `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`

---

#### 2. Valores SEMPRE vêm do backend

**❌ VULNERÁVEL:**
```typescript
// Frontend
const amount = 99.90;  // ← Hacker pode alterar
fetch('/api/billing/create-payment', {
  body: JSON.stringify({ amount })
})
```

**✅ SEGURO:**
```typescript
// Frontend
const planId = "plan_basic";  // ← Só envia ID
fetch('/api/billing/create-payment', {
  body: JSON.stringify({ planId })
})

// Backend
@router.post("/billing/create-payment")
async def create_payment(planId: str, cliente: Cliente = Depends(...)):
    # Buscar preço no BANCO, não confiar no frontend
    plan = db.query(Plan).filter(Plan.id == planId).first()
    amount = plan.price  # ← Valor vem do backend
    
    # Criar payment intent
    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),
        currency="brl",
        customer=cliente.stripe_customer_id
    )
```

---

## 🔧 Implementações

### 6.1 Validação de Webhook Stripe

**Arquivo:** `apps/backend/app/api/v1/billing.py`

**Verificar se já existe:**
```python
@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        # ✅ CRÍTICO: Verificar assinatura
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Payload inválido
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        # Assinatura inválida
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Processar evento...
```

**Se não existir, implementar.**

---

### 6.2 Auditoria de Transações

**Novo modelo:** `apps/backend/app/db/models/payment_log.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from app.db.base import Base
from datetime import datetime

class PaymentLog(Base):
    """Log de todas transações de pagamento"""
    __tablename__ = "payment_logs"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    
    # Dados da transação
    stripe_payment_intent_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    currency = Column(String(3), default="brl")
    status = Column(String(50))  # succeeded, failed, pending
    
    # Metadados
    plan_id = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Segurança
    ip_address = Column(String(45))
    user_agent = Column(Text, nullable=True)
    
    # Webhook
    webhook_received = Column(Boolean, default=False)
    webhook_received_at = Column(DateTime, nullable=True)
    
    cliente = relationship("Cliente", back_populates="payment_logs")
```

**Logar TODAS transações:**
```python
@router.post("/billing/create-payment")
async def create_payment(
    request: Request,
    plan_id: str,
    db: Session = Depends(get_db),
    cliente: Cliente = Depends(get_current_cliente)
):
    # Buscar plano
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    
    # Criar payment intent
    intent = stripe.PaymentIntent.create(
        amount=int(plan.price * 100),
        currency="brl",
        customer=cliente.stripe_customer_id,
        metadata={
            "cliente_id": cliente.id,
            "plan_id": plan.id
        }
    )
    
    # ✅ LOGAR TRANSAÇÃO
    payment_log = PaymentLog(
        cliente_id=cliente.id,
        stripe_payment_intent_id=intent.id,
        amount=plan.price,
        currency="brl",
        status="pending",
        plan_id=plan.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(payment_log)
    db.commit()
    
    return {"client_secret": intent.client_secret}
```

---

### 6.3 Validação de Ownership em Pagamentos

**Problema:** Usuário pode tentar cancelar assinatura de outro

```python
# ❌ VULNERÁVEL
@router.post("/billing/cancel")
async def cancel_subscription(subscription_id: str):
    stripe.Subscription.delete(subscription_id)
    return {"status": "cancelled"}
```

```python
# ✅ SEGURO
@router.post("/billing/cancel")
async def cancel_subscription(
    db: Session = Depends(get_db),
    cliente: Cliente = Depends(get_current_cliente)
):
    # Buscar assinatura do cliente no BANCO
    if not cliente.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="Sem assinatura ativa")
    
    # Verificar no Stripe que assinatura pertence ao customer do cliente
    subscription = stripe.Subscription.retrieve(cliente.stripe_subscription_id)
    
    if subscription.customer != cliente.stripe_customer_id:
        # Tentativa de fraude!
        logger.error(
            f"🚨 Cliente {cliente.id} tentou cancelar assinatura de outro usuário"
        )
        raise HTTPException(status_code=403, detail="Não autorizado")
    
    # Cancelar
    stripe.Subscription.delete(cliente.stripe_subscription_id)
    
    # Atualizar banco
    cliente.stripe_subscription_id = None
    cliente.subscription_status = "cancelled"
    db.commit()
    
    return {"status": "cancelled"}
```

---

### 6.4 Proteção Contra Replay Attack em Webhooks

**Problema:** Hacker pode reenviar webhook antigo

```python
@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    # Verificar assinatura
    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
    
    # ✅ PROTEÇÃO CONTRA REPLAY
    event_id = event.id
    
    # Verificar se já processamos este evento
    existing = db.query(PaymentLog).filter(
        PaymentLog.stripe_payment_intent_id == event.data.object.id,
        PaymentLog.webhook_received == True
    ).first()
    
    if existing:
        logger.warning(f"⚠️ Webhook duplicado ignorado: {event_id}")
        return {"status": "already_processed"}
    
    # Processar evento...
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        
        # Atualizar log
        log = db.query(PaymentLog).filter(
            PaymentLog.stripe_payment_intent_id == payment_intent.id
        ).first()
        
        if log:
            log.status = "succeeded"
            log.webhook_received = True
            log.webhook_received_at = datetime.utcnow()
            db.commit()
    
    return {"status": "success"}
```

---

### 6.5 Validação de Valores no Backend

**Criar serviço de validação:**

```python
# apps/backend/app/services/billing/price_validator.py

class PriceValidator:
    """Valida que valores de pagamento estão corretos"""
    
    @staticmethod
    def validate_payment_intent(
        db: Session,
        payment_intent_id: str,
        expected_amount: float
    ) -> bool:
        """
        Valida que valor do payment intent corresponde ao esperado
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Converter centavos para reais
            actual_amount = intent.amount / 100
            
            # Permitir diferença de 0.01 (arredondamento)
            if abs(actual_amount - expected_amount) > 0.01:
                logger.error(
                    f"🚨 Valor incorreto! "
                    f"Esperado: {expected_amount}, Recebido: {actual_amount}"
                )
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao validar payment intent: {e}")
            return False
```

---

## 🧪 Testes

### Teste 1: Frontend Não Tem Chaves Secretas
```bash
# Deve retornar ZERO resultados
grep -r "sk_" apps/frontend/
grep -r "STRIPE_SECRET" apps/frontend/
```

### Teste 2: Valores Vêm do Backend
```python
def test_payment_amount_from_backend():
    # Tentar criar pagamento com valor manipulado
    response = client.post("/api/v1/billing/create-payment", json={
        "plan_id": "basic",
        "amount": 0.01  # ← Tentar pagar R$ 0,01
    })
    
    # Backend deve ignorar amount e usar preço do banco
    intent_id = response.json()["payment_intent_id"]
    intent = stripe.PaymentIntent.retrieve(intent_id)
    
    # Verificar que valor é o correto (não o manipulado)
    assert intent.amount == 9990  # R$ 99,90 em centavos
```

### Teste 3: Webhook Signature
```python
def test_webhook_signature():
    # Enviar webhook sem assinatura
    response = client.post("/api/v1/billing/webhook", json={
        "type": "payment_intent.succeeded",
        "data": {}
    })
    
    # Deve rejeitar
    assert response.status_code == 400
```

---

## 📝 Checklist

- [ ] Auditar frontend (sem chaves secretas)
- [ ] Verificar que valores vêm do backend
- [ ] Validar webhook signature
- [ ] Criar modelo PaymentLog
- [ ] Logar todas transações
- [ ] Implementar proteção contra replay
- [ ] Validar ownership em cancelamentos
- [ ] Criar PriceValidator
- [ ] Testar manipulação de valores
- [ ] Testar webhook signature

---

## 🚨 Regras de Ouro

1. **Frontend NUNCA tem chaves secretas**
2. **Valores SEMPRE vêm do backend**
3. **SEMPRE verificar webhook signature**
4. **SEMPRE logar transações**
5. **SEMPRE validar ownership**

---

**Status:** 🔴 Não iniciado  
**Prioridade:** MÉDIA  
**Tempo estimado:** 3-4 horas  
**Depende de:** FASE 5 concluída
