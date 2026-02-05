# 🚀 COMANDOS RÁPIDOS - MINI-FASE 1

## ✅ Problema Resolvido
O `Dockerfile` foi movido para `docs/legacy/`, mas o `docker-compose.yml` estava procurando na raiz.

**Correção aplicada:** `build: .` → `build: ./apps/backend`

---

## 🐳 Subir o Projeto

```bash
# Parar containers antigos (se houver)
docker-compose down

# Subir com rebuild
docker-compose up -d --build

# Ver logs
docker-compose logs -f bot
```

---

## 🧪 Testar Webhook (Opção 1 - Rápido)

```bash
# Entrar no container
docker exec -it bot bash

# Rodar teste manual
python test_webhook_manual.py

# Sair do container
exit
```

---

## 🧪 Testar Webhook (Opção 2 - Stripe CLI)

### Passo 1: Instalar Stripe CLI
```bash
# Windows (com Scoop)
scoop install stripe

# Ou baixar de: https://stripe.com/docs/stripe-cli
```

### Passo 2: Login
```bash
stripe login
```

### Passo 3: Escutar webhooks
```bash
stripe listen --forward-to localhost:8000/api/v1/billing/webhook
```

**Copie o webhook secret que aparecer e adicione no `.env`:**
```
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

### Passo 4: Trigger evento (em outro terminal)
```bash
stripe trigger checkout.session.completed
```

### Passo 5: Ver logs
```bash
# Logs do backend
docker logs bot -f

# Ou entrar no container
docker exec -it bot bash
```

---

## 🔍 Verificar Banco de Dados

```bash
# Entrar no PostgreSQL
docker exec -it postgres psql -U postgres -d whatsapp_bot

# Consultar clientes
SELECT id, nome, email, status, stripe_customer_id, stripe_subscription_id FROM clientes;

# Sair
\q
```

---

## 🐛 Troubleshooting

### Container não sobe
```bash
# Ver logs de erro
docker-compose logs bot

# Rebuild forçado
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Erro de migrations
```bash
# Entrar no container
docker exec -it bot bash

# Rodar migrations manualmente
cd /app/apps/backend
alembic upgrade head
```

### Ver estrutura do banco
```bash
docker exec -it postgres psql -U postgres -d whatsapp_bot -c "\dt"
```

---

## 📊 Status dos Containers

```bash
# Ver containers rodando
docker ps

# Ver todos os containers
docker ps -a

# Ver logs de todos os serviços
docker-compose logs
```

---

## 🔄 Reiniciar Serviços

```bash
# Reiniciar apenas o bot
docker-compose restart bot

# Reiniciar tudo
docker-compose restart

# Parar tudo
docker-compose down

# Subir tudo
docker-compose up -d
```

---

## 📝 Próximos Passos

1. ✅ Subir containers: `docker-compose up -d --build`
2. ✅ Testar webhook: `docker exec -it bot bash` → `python test_webhook_manual.py`
3. ✅ Verificar banco: `docker exec -it postgres psql -U postgres -d whatsapp_bot`
4. ✅ Avisar que funcionou!
5. ➡️ Avançar para MINI-FASE 2

---

## 🎯 Comando Único (Tudo de Uma Vez)

```bash
# Parar, rebuild, subir e ver logs
docker-compose down && docker-compose up -d --build && docker-compose logs -f bot
```

Pressione `Ctrl+C` para parar de ver os logs.
