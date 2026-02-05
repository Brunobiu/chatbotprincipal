# 🧪 TESTE - MINI-FASE 1: Webhook de Pagamento

## ✅ O que foi implementado

1. **Serviço de Clientes** (`apps/backend/app/services/clientes/cliente_service.py`)
   - Criação de cliente a partir de dados do Stripe
   - Geração automática de senha segura
   - Hash de senha com bcrypt
   - Atualização de status de subscription

2. **Webhook de Billing** (`apps/backend/app/api/v1/billing.py`)
   - Processamento de `checkout.session.completed`
   - Processamento de `invoice.payment_succeeded`
   - Processamento de `customer.subscription.updated`
   - Processamento de `customer.subscription.deleted`
   - Logs estruturados

3. **Limpeza**
   - Arquivos legados movidos para `docs/legacy/`

---

## 🧪 Como testar

### Opção 1: Teste Manual (Rápido)

```bash
# 1. Entrar no container do backend
docker exec -it bot bash

# 2. Rodar o script de teste
python test_webhook_manual.py
```

**Resultado esperado:**
```
✅ Cliente criado com sucesso!
   ID: 1
   Nome: Cliente Teste
   Email: teste@exemplo.com
   Status: ClienteStatus.ATIVO
   🔑 Senha gerada: AbC123!@#xyz
✅ Cliente encontrado no banco de dados!
```

---

### Opção 2: Teste com Stripe CLI (Recomendado)

#### Passo 1: Instalar Stripe CLI
```bash
# Windows (com Scoop)
scoop install stripe

# Ou baixar de: https://stripe.com/docs/stripe-cli
```

#### Passo 2: Login no Stripe
```bash
stripe login
```

#### Passo 3: Escutar webhooks localmente
```bash
# Isso vai criar um webhook endpoint temporário e encaminhar para localhost:8000
stripe listen --forward-to localhost:8000/api/v1/billing/webhook
```

**Você vai receber um webhook secret. Copie e adicione no .env:**
```
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

#### Passo 4: Criar um checkout de teste
```bash
# Em outro terminal, trigger um evento de teste
stripe trigger checkout.session.completed
```

#### Passo 5: Verificar logs

**No terminal do Stripe CLI, você deve ver:**
```
✅ Received event checkout.session.completed
```

**Nos logs do backend (docker logs bot), você deve ver:**
```
📥 Webhook recebido: checkout.session.completed | ID: cs_test_xxxxx
📧 Criando cliente: customer@example.com
✅ Cliente criado: ID=1 | Email=customer@example.com
🔑 Senha gerada: AbC123!@#xyz
📧 TODO: Enviar email para customer@example.com com senha: AbC123!@#xyz
```

#### Passo 6: Verificar no banco de dados
```bash
# Entrar no container do postgres
docker exec -it postgres psql -U postgres -d whatsapp_bot

# Consultar clientes
SELECT id, nome, email, status, stripe_customer_id, stripe_subscription_id FROM clientes;
```

**Resultado esperado:**
```
 id |     nome      |        email         | status | stripe_customer_id | stripe_subscription_id
----+---------------+----------------------+--------+--------------------+-----------------------
  1 | Jenny Rosen   | customer@example.com | ativo  | cus_xxxxx          | sub_xxxxx
```

---

## 🔍 Checklist de Validação

- [ ] Script de teste manual executa sem erros
- [ ] Cliente é criado no banco de dados
- [ ] Senha é gerada automaticamente
- [ ] Hash da senha é armazenado (não a senha em texto plano)
- [ ] Status do cliente é ATIVO
- [ ] Stripe customer_id e subscription_id são salvos
- [ ] Webhook do Stripe é recebido e processado
- [ ] Logs aparecem corretamente
- [ ] Eventos de atualização/cancelamento funcionam

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'bcrypt'"
**Solução:** Bcrypt já está no requirements.txt. Rebuild o container:
```bash
docker-compose down
docker-compose up --build
```

### Erro: "No such table: clientes"
**Solução:** Rodar migrations:
```bash
docker exec -it bot bash
cd apps/backend
alembic upgrade head
```

### Webhook não chega
**Solução:** Verificar se o Stripe CLI está rodando e se a URL está correta:
```bash
stripe listen --forward-to localhost:8000/api/v1/billing/webhook
```

---

## 📊 Próximos Passos

Após validar que a MINI-FASE 1 está funcionando:

1. ✅ Commit das mudanças
2. ➡️ Avançar para MINI-FASE 2 (Multi-tenant RAG)

---

## 📝 Notas

- A senha gerada é logada apenas em desenvolvimento
- Na FASE 5, implementaremos o envio de email com as credenciais
- O webhook valida assinatura apenas se `STRIPE_WEBHOOK_SECRET` estiver configurado
