# FASE E - BILLING COM 3 PLANOS

**Prioridade:** ⭐ ALTA  
**Tempo Estimado:** 8-10 horas  
**Status:** ⏳ Pendente

---

## 🎯 Objetivo

Implementar sistema de billing com 3 planos de assinatura (Mensal, Trimestral, Semestral) com descontos progressivos e integração completa com Stripe.

---

## 💰 Planos de Assinatura

### Plano 1: Mensal
- **Preço:** R$ 147,00/mês
- **Cobrança:** Mensal
- **Desconto:** 0%
- **Economia:** R$ 0

### Plano 2: Trimestral (3 meses)
- **Preço:** R$ 127,00/mês (R$ 381,00 total)
- **Cobrança:** A cada 3 meses
- **Desconto:** 13,6%
- **Economia:** R$ 60,00 (vs mensal)

### Plano 3: Semestral (6 meses)
- **Preço:** R$ 97,00/mês (R$ 582,00 total)
- **Cobrança:** A cada 6 meses
- **Desconto:** 34%
- **Economia:** R$ 300,00 (vs mensal)

---

## 📋 Funcionalidades

### E1: Página de Escolha de Planos

**Localização:** `/planos`

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│              Escolha seu Plano                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │  MENSAL  │  │TRIMESTRAL│  │SEMESTRAL │ ⭐ POPULAR     │
│  ├──────────┤  ├──────────┤  ├──────────┤                │
│  │R$ 147/mês│  │R$ 127/mês│  │R$ 97/mês │                │
│  │          │  │          │  │          │                │
│  │Cobrado   │  │Cobrado   │  │Cobrado   │                │
│  │mensalmente│  │R$ 381    │  │R$ 582    │                │
│  │          │  │a cada 3  │  │a cada 6  │                │
│  │          │  │meses     │  │meses     │                │
│  │          │  │          │  │          │                │
│  │          │  │Economize │  │Economize │                │
│  │          │  │R$ 60     │  │R$ 300    │                │
│  │          │  │          │  │          │                │
│  │[Assinar] │  │[Assinar] │  │[Assinar] │                │
│  └──────────┘  └──────────┘  └──────────┘                │
│                                                             │
│  ✅ Todos os recursos incluídos                            │
│  ✅ Suporte prioritário                                    │
│  ✅ Cancele quando quiser                                  │
└─────────────────────────────────────────────────────────────┘
```

**Destaque:**
- Plano Semestral com badge "POPULAR" ou "MELHOR OFERTA"
- Mostrar economia em destaque
- Botão de ação claro

---

### E2: Integração com Stripe

**Produtos no Stripe:**

Criar 3 produtos no Stripe:
1. **Chatbot AI - Mensal**
   - Price ID: `price_mensal_xxx`
   - Valor: R$ 147,00
   - Recorrência: Mensal

2. **Chatbot AI - Trimestral**
   - Price ID: `price_trimestral_xxx`
   - Valor: R$ 381,00
   - Recorrência: A cada 3 meses

3. **Chatbot AI - Semestral**
   - Price ID: `price_semestral_xxx`
   - Valor: R$ 582,00
   - Recorrência: A cada 6 meses

**Fluxo de Pagamento:**
1. Cliente escolhe plano
2. Sistema cria Stripe Checkout Session
3. Cliente preenche dados do cartão
4. Stripe processa pagamento
5. Webhook confirma pagamento
6. Sistema ativa assinatura

---

### E3: Gestão de Assinaturas

**Funcionalidades:**

**1. Trocar de Plano:**
- Cliente pode fazer upgrade/downgrade
- Mudança entra em vigor no próximo ciclo
- Sem cobrança adicional imediata

**2. Trocar Cartão:**
- Cliente pode atualizar método de pagamento
- Sem interrupção do serviço

**3. Cancelar Assinatura:**
- Cliente mantém acesso até fim do período pago
- Não há reembolso proporcional
- Pode reativar antes do fim do período

**4. Reativar Assinatura:**
- Se cancelou, pode reativar
- Cobra imediatamente novo período

---

### E4: Exibição no Dashboard

**Aba "Meu Plano" - Cliente com Assinatura Ativa:**

```
┌─────────────────────────────────────────────────────┐
│ 📦 Plano Atual                                      │
├─────────────────────────────────────────────────────┤
│ Plano: Semestral - R$ 97,00/mês                    │
│ Próxima cobrança: 14/08/2026 (R$ 582,00)          │
│ Método de pagamento: Visa •••• 4242                │
│                                                     │
│ [Trocar Plano] [Trocar Cartão] [Cancelar]         │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 💰 Economia                                         │
├─────────────────────────────────────────────────────┤
│ Você está economizando R$ 300,00 a cada 6 meses!  │
│ Comparado ao plano mensal.                         │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 📜 Histórico de Pagamentos                         │
├─────────────────────────────────────────────────────┤
│ 14/02/2026 - R$ 582,00 - Pago ✅                   │
│ 14/08/2025 - R$ 582,00 - Pago ✅                   │
│ 14/02/2025 - R$ 147,00 - Pago ✅                   │
└─────────────────────────────────────────────────────┘
```

---

## 🗄️ Alterações no Banco de Dados

### Tabela `clientes`

**Adicionar campos:**
```sql
ALTER TABLE clientes ADD COLUMN plano VARCHAR(20);
-- Valores: 'mensal', 'trimestral', 'semestral'

ALTER TABLE clientes ADD COLUMN plano_preco DECIMAL(10,2);
-- Preço mensal do plano

ALTER TABLE clientes ADD COLUMN plano_valor_total DECIMAL(10,2);
-- Valor total cobrado por período

ALTER TABLE clientes ADD COLUMN proxima_cobranca TIMESTAMP;
-- Data da próxima cobrança

ALTER TABLE clientes ADD COLUMN plano_pendente VARCHAR(20);
-- Plano que entrará em vigor no próximo ciclo (se houver mudança)
```

### Nova Tabela: `pagamentos`

```sql
CREATE TABLE pagamentos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    stripe_payment_intent_id VARCHAR(255),
    plano VARCHAR(20),
    valor DECIMAL(10,2),
    status VARCHAR(20),
    -- Valores: 'pending', 'succeeded', 'failed', 'refunded'
    data_pagamento TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔧 Implementação Técnica

### Backend

**1. Criar produtos no Stripe:**
```python
# Script para criar produtos
stripe.Product.create(
    name="Chatbot AI - Mensal",
    description="Plano mensal"
)
stripe.Price.create(
    product="prod_xxx",
    unit_amount=14700,  # R$ 147,00 em centavos
    currency="brl",
    recurring={"interval": "month"}
)
```

**2. Rota para criar checkout:**
```
POST /api/v1/billing/create-checkout
Body: {
  "plano": "semestral"
}
Response: {
  "checkout_url": "https://checkout.stripe.com/..."
}
```

**3. Webhook Stripe:**
```python
@router.post("/webhook")
async def stripe_webhook(request: Request):
    event = stripe.Webhook.construct_event(...)
    
    if event.type == "checkout.session.completed":
        # Ativar assinatura
        # Atualizar cliente
        # Registrar pagamento
    
    elif event.type == "invoice.payment_succeeded":
        # Renovação automática
        # Registrar pagamento
    
    elif event.type == "customer.subscription.deleted":
        # Cancelamento
        # Atualizar status
```

**4. Rotas de gestão:**
```
POST /api/v1/billing/change-plan
Body: {"novo_plano": "trimestral"}

POST /api/v1/billing/update-card
Response: {"update_url": "..."}

POST /api/v1/billing/cancel-subscription

POST /api/v1/billing/reactivate-subscription

GET /api/v1/billing/payment-history
Response: [{"data": "...", "valor": 147, "status": "succeeded"}]
```

---

### Frontend

**1. Página de planos:**

**Componente:** `apps/frontend/app/planos/page.tsx`

**Conteúdo:**
- 3 cards de planos lado a lado
- Destaque no plano semestral
- Botão "Assinar" em cada card
- Comparação de economia

**2. Aba "Meu Plano":**

**Componente:** `apps/frontend/app/dashboard/meu-plano/page.tsx`

**Seções:**
- Informações do plano atual
- Economia (se aplicável)
- Histórico de pagamentos
- Botões de ação

**3. Modal de confirmação:**

**Componente:** `apps/frontend/components/ConfirmCancelModal.tsx`

**Uso:** Ao cancelar assinatura

**Conteúdo:**
```
┌────────────────────────────────────────┐
│ ⚠️  Cancelar Assinatura?              │
├────────────────────────────────────────┤
│ Você manterá acesso até 14/08/2026    │
│ Após essa data, sua conta será        │
│ suspensa.                              │
│                                        │
│ Tem certeza?                           │
│                                        │
│ [Voltar] [Sim, Cancelar]              │
└────────────────────────────────────────┘
```

---

## ✅ Checklist de Implementação

### Stripe
- [ ] Criar produto "Chatbot AI - Mensal"
- [ ] Criar produto "Chatbot AI - Trimestral"
- [ ] Criar produto "Chatbot AI - Semestral"
- [ ] Configurar webhooks

### Backend
- [ ] Criar migração para novos campos
- [ ] Criar tabela `pagamentos`
- [ ] Criar rota `POST /api/v1/billing/create-checkout`
- [ ] Atualizar webhook Stripe
- [ ] Criar rota `POST /api/v1/billing/change-plan`
- [ ] Criar rota `POST /api/v1/billing/update-card`
- [ ] Criar rota `POST /api/v1/billing/cancel-subscription`
- [ ] Criar rota `POST /api/v1/billing/reactivate-subscription`
- [ ] Criar rota `GET /api/v1/billing/payment-history`

### Frontend
- [ ] Criar página `/planos`
- [ ] Atualizar página `/dashboard/meu-plano`
- [ ] Criar componente `PlanCard`
- [ ] Criar componente `ConfirmCancelModal`
- [ ] Criar componente `PaymentHistory`
- [ ] Adicionar links para `/planos` no banner de trial

### Testes
- [ ] Testar checkout de cada plano
- [ ] Testar renovação automática
- [ ] Testar mudança de plano
- [ ] Testar troca de cartão
- [ ] Testar cancelamento
- [ ] Testar reativação
- [ ] Testar histórico de pagamentos

---

## 🧪 Casos de Teste

### CT1: Assinar Plano Mensal
1. Cliente em trial clica "Assinar"
2. Escolhe plano mensal
3. Completa pagamento
4. **Esperado:** Status 'active', próxima cobrança em 1 mês

### CT2: Assinar Plano Semestral
1. Cliente escolhe plano semestral
2. Completa pagamento de R$ 582,00
3. **Esperado:** Status 'active', próxima cobrança em 6 meses

### CT3: Mudança de Plano (Upgrade)
1. Cliente com plano mensal
2. Clica "Trocar Plano"
3. Escolhe semestral
4. **Esperado:** Mudança agendada para próximo ciclo

### CT4: Mudança de Plano (Downgrade)
1. Cliente com plano semestral
2. Troca para mensal
3. **Esperado:** Mudança agendada, mantém semestral até fim do período

### CT5: Cancelamento
1. Cliente clica "Cancelar"
2. Confirma cancelamento
3. **Esperado:** Acesso mantido até fim do período pago

### CT6: Reativação
1. Cliente com assinatura cancelada
2. Clica "Reativar"
3. **Esperado:** Nova cobrança imediata, assinatura ativa

### CT7: Renovação Automática
1. Aguardar data de renovação
2. Stripe cobra automaticamente
3. **Esperado:** Webhook atualiza próxima cobrança

---

## 📝 Notas Importantes

1. **Descontos progressivos** - Incentivar planos longos
2. **Sem reembolso** - Política clara de não reembolso
3. **Acesso mantido** - Até fim do período pago, mesmo cancelado
4. **Mudança de plano** - Entra em vigor no próximo ciclo
5. **Histórico completo** - Cliente vê todos os pagamentos
6. **Economia visível** - Mostrar quanto está economizando

---

## 🚀 Próximos Passos

Após completar FASE E:
- [ ] Marcar como completa no README.md
- [ ] Passar para FASE B (IA Assistente)

---

**Status:** ⏳ Aguardando implementação
