# FASE A - TRIAL GRATUITO E CADASTRO

**Prioridade:** ⭐ ALTA  
**Tempo Estimado:** 8-10 horas  
**Status:** ⏳ Pendente

---

## 🎯 Objetivo

Implementar sistema de trial gratuito de 7 dias sem exigir cartão de crédito, com novo fluxo de cadastro onde o cliente cria sua própria senha.

---

## 📋 Funcionalidades

### A1: Sistema de Trial de 7 Dias

**Comportamento:**
- Cliente se cadastra SEM pedir cartão
- Sistema marca `trial_starts_at` e `trial_ends_at` automaticamente
- Após 7 dias, bloqueia acesso automático
- Mostra tela pedindo pagamento

**Regras:**
- Trial começa no momento do cadastro
- Trial dura exatamente 7 dias (168 horas)
- Após expirar, cliente não consegue acessar dashboard
- Cliente pode assinar a qualquer momento durante o trial

---

### A2: Novo Fluxo de Cadastro

**Fluxo Atual (REMOVER):**
```
Landing → Stripe Checkout → Email com senha → Login
```

**Novo Fluxo:**
```
Landing → Página de Cadastro → Acesso Direto ao Dashboard
```

**Campos do Cadastro:**
- Nome completo
- Email (único)
- Senha (mínimo 8 caracteres)
- Confirmar senha
- Aceitar termos (checkbox)

**Validações:**
- Email válido e único
- Senha forte (mínimo 8 caracteres)
- Senhas devem coincidir
- Termos devem ser aceitos

**Após Cadastro:**
- Cliente é criado com status `trial`
- `trial_starts_at` = agora
- `trial_ends_at` = agora + 7 dias
- Login automático (JWT)
- Redireciona para dashboard

---

### A3: Contador de Trial no Dashboard

**Localização:** Topo do dashboard do cliente (banner fixo)

**Exibição:**

**Durante o Trial:**
```
┌────────────────────────────────────────────────────────┐
│ ⏰ TRIAL GRATUITO - Restam 5 dias                     │
│ Aproveite todos os recursos! Assine agora e ganhe 10% │
│ de desconto.                          [Assinar Agora] │
└────────────────────────────────────────────────────────┘
```

**Últimos 2 Dias (Urgência):**
```
┌────────────────────────────────────────────────────────┐
│ ⚠️  TRIAL EXPIRANDO - Restam 1 dia                    │
│ Não perca o acesso! Assine agora.     [Assinar Agora] │
└────────────────────────────────────────────────────────┘
```

**Trial Expirado:**
- Bloqueia acesso ao dashboard
- Mostra tela de bloqueio:
```
┌────────────────────────────────────────┐
│         🔒 Trial Expirado              │
│                                        │
│  Seu período de teste terminou.       │
│  Assine agora para continuar usando!  │
│                                        │
│          [Escolher Plano]              │
└────────────────────────────────────────┘
```

---

### A4: Gestão de Planos e Pagamentos

**Nova Aba no Dashboard Cliente:** "Meu Plano"

**Conteúdo (Durante Trial):**
```
┌─────────────────────────────────────────┐
│ 📦 Plano Atual: Trial Gratuito         │
│ ⏰ Expira em: 5 dias (14/02/2026)      │
│ 💳 Cartão: Nenhum                      │
│                                         │
│ [Assinar Agora]                        │
└─────────────────────────────────────────┘
```

**Conteúdo (Após Assinar):**
```
┌─────────────────────────────────────────┐
│ 📦 Plano Atual: Mensal - R$ 147,00     │
│ 📅 Próxima cobrança: 14/03/2026        │
│ 💳 Cartão: •••• 4242                   │
│                                         │
│ [Trocar Cartão] [Cancelar Assinatura] │
└─────────────────────────────────────────┘
```

**Funcionalidades:**
- Mostrar plano ativo
- Mostrar próxima cobrança
- Mostrar cartão salvo (últimos 4 dígitos)
- Botão para trocar cartão
- Botão para cancelar assinatura

---

## 🗄️ Alterações no Banco de Dados

### Tabela `clientes`

**Adicionar campos:**
```sql
ALTER TABLE clientes ADD COLUMN trial_starts_at TIMESTAMP;
ALTER TABLE clientes ADD COLUMN trial_ends_at TIMESTAMP;
ALTER TABLE clientes ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'trial';
-- Valores: 'trial', 'active', 'canceled', 'expired'
```

**Campos existentes a manter:**
- `stripe_customer_id` (NULL durante trial)
- `stripe_subscription_id` (NULL durante trial)
- `plano` (NULL durante trial, depois 'mensal', '3meses', '6meses')

---

## 🔧 Implementação Técnica

### Backend

**1. Nova rota de cadastro:**
```
POST /api/v1/auth/register
Body: {
  "nome": "João Silva",
  "email": "joao@example.com",
  "senha": "senha123",
  "aceitar_termos": true
}
Response: {
  "access_token": "...",
  "refresh_token": "...",
  "cliente": {...}
}
```

**2. Middleware de verificação de trial:**
```python
# Verificar em TODAS as rotas do cliente
if cliente.subscription_status == 'trial':
    if datetime.now() > cliente.trial_ends_at:
        raise HTTPException(403, "Trial expirado")
```

**3. Rota para verificar status do trial:**
```
GET /api/v1/clientes/me/trial-status
Response: {
  "status": "trial",
  "days_remaining": 5,
  "trial_ends_at": "2026-02-14T10:30:00"
}
```

**4. Atualizar rota de pagamento:**
- Ao completar pagamento Stripe, atualizar:
  - `subscription_status` = 'active'
  - `stripe_customer_id`
  - `stripe_subscription_id`
  - `plano` = 'mensal' (ou outro)

---

### Frontend

**1. Nova página de cadastro:**
```
/cadastro
```

**Componente:** `apps/frontend/app/cadastro/page.tsx`

**Campos:**
- Nome completo
- Email
- Senha
- Confirmar senha
- Checkbox "Aceito os termos"
- Botão "Criar Conta Grátis"

**2. Banner de trial:**

**Componente:** `apps/frontend/components/TrialBanner.tsx`

**Lógica:**
- Buscar status do trial via API
- Calcular dias restantes
- Mostrar banner apropriado
- Esconder se não estiver em trial

**3. Tela de bloqueio:**

**Componente:** `apps/frontend/components/TrialExpiredModal.tsx`

**Lógica:**
- Detectar trial expirado (403 da API)
- Mostrar modal full-screen
- Botão redireciona para página de planos

**4. Aba "Meu Plano":**

**Componente:** `apps/frontend/app/dashboard/meu-plano/page.tsx`

**Conteúdo:**
- Informações do plano atual
- Status do trial (se aplicável)
- Cartão salvo
- Botões de ação

---

## ✅ Checklist de Implementação

### Backend
- [ ] Criar migração para adicionar campos de trial
- [ ] Criar rota `POST /api/v1/auth/register`
- [ ] Criar rota `GET /api/v1/clientes/me/trial-status`
- [ ] Criar middleware de verificação de trial
- [ ] Atualizar rota de webhook Stripe
- [ ] Criar rota `POST /api/v1/clientes/me/cancel-subscription`
- [ ] Criar rota `POST /api/v1/clientes/me/update-card`

### Frontend
- [ ] Criar página `/cadastro`
- [ ] Criar componente `TrialBanner`
- [ ] Criar componente `TrialExpiredModal`
- [ ] Criar página `/dashboard/meu-plano`
- [ ] Atualizar landing page (link para /cadastro)
- [ ] Adicionar interceptor para detectar trial expirado

### Testes
- [ ] Testar cadastro completo
- [ ] Testar login após cadastro
- [ ] Testar contador de dias
- [ ] Testar bloqueio após 7 dias
- [ ] Testar assinatura durante trial
- [ ] Testar cancelamento de assinatura

---

## 🧪 Casos de Teste

### CT1: Cadastro Novo Cliente
1. Acessar `/cadastro`
2. Preencher todos os campos
3. Clicar em "Criar Conta Grátis"
4. **Esperado:** Login automático e redirecionamento para dashboard

### CT2: Contador de Trial
1. Fazer login com cliente em trial
2. Ver banner no topo
3. **Esperado:** "Restam X dias"

### CT3: Trial Expirado
1. Alterar `trial_ends_at` para data passada
2. Tentar acessar dashboard
3. **Esperado:** Modal de bloqueio

### CT4: Assinatura Durante Trial
1. Cliente em trial clica "Assinar Agora"
2. Completa pagamento Stripe
3. **Esperado:** Status muda para 'active', banner desaparece

### CT5: Cancelar Assinatura
1. Cliente com assinatura ativa
2. Ir em "Meu Plano"
3. Clicar "Cancelar Assinatura"
4. **Esperado:** Status muda para 'canceled', acesso mantido até fim do período pago

---

## 📝 Notas Importantes

1. **Não pedir cartão no cadastro** - Trial é 100% grátis
2. **Bloquear acesso após 7 dias** - Sem exceções
3. **Permitir assinatura a qualquer momento** - Durante ou após trial
4. **Salvar cartão no Stripe** - Para cobranças recorrentes
5. **Permitir trocar cartão** - A qualquer momento
6. **Cancelamento mantém acesso** - Até fim do período pago

---

## 🚀 Próximos Passos

Após completar FASE A:
- [ ] Marcar como completa no README.md
- [ ] Passar para FASE E (Billing com 3 planos)

---

**Status:** ⏳ Aguardando implementação
