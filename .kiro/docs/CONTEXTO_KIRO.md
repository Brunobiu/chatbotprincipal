# 📋 CONTEXTO COMPLETO - PROJETO WHATSAPP AI BOT SAAS

**Data de início:** 05/02/2026  
**Branch atual:** `fix/critical-issues`  
**Status:** MINI-FASE 3 COMPLETA ✅

---

## 🎯 OBJETIVO DO PROJETO

Transformar um chatbot WhatsApp simples em um **SaaS multi-tenant completo** com:
- Landing page + Checkout (Stripe)
- Dashboard para clientes
- Isolamento de dados por cliente
- RAG (Retrieval-Augmented Generation) personalizado
- Controle humano vs IA
- Sistema de assinaturas

---

## 📊 ANÁLISE TÉCNICA INICIAL

### Problemas Críticos Identificados

1. ❌ **Webhook de pagamento não persistia dados** (linha 89 do billing.py)
2. ❌ **Falta isolamento multi-tenant no RAG** (todos compartilhavam mesma base)
3. ❌ **Webhook WhatsApp não identificava cliente**
4. ❌ **Falta validação de assinatura ativa**
5. ❌ **Zero testes implementados**
6. ❌ **Segurança básica não implementada**

### Estrutura Encontrada

```
✅ Fases 1, 2, 3 implementadas (organização, infra, frontend)
⚠️ Fase 4 parcialmente implementada (checkout sem persistência)
❌ Fases 5-16 não implementadas
```

---

## 🚀 ESTRATÉGIA ADOTADA

**Abordagem:** Resolver problemas críticos em mini-fases, uma de cada vez.

### Mini-fases Planejadas

| Fase | Prioridade | Status | Tempo |
|------|-----------|--------|-------|
| 0. Preparação | 🔴 CRÍTICO | ✅ COMPLETA | 5min |
| 1. Webhook Pagamento | 🔴 CRÍTICO | ✅ COMPLETA | 40min |
| 2. Multi-tenant RAG | 🔴 CRÍTICO | ✅ COMPLETA | 50min |
| 3. Lookup Cliente | 🔴 CRÍTICO | ✅ COMPLETA (integrado na fase 2) | - |
| 4. Segurança Básica | 🟡 IMPORTANTE | ✅ COMPLETA | 40min |
| 5. Testes Básicos | 🟡 IMPORTANTE | ⏳ PENDENTE | 50min |
| 6. Performance | 🔵 OPCIONAL | ⏳ PENDENTE | 40min |
| 7. Limpeza | 🔵 OPCIONAL | ⏳ PENDENTE | 30min |

---

## ✅ MINI-FASE 0: PREPARAÇÃO (COMPLETA)

### O que foi feito
- ✅ Branch `fix/critical-issues` criada
- ✅ Backup commitado
- ✅ Arquivos legados movidos para `docs/legacy/`

### Arquivos movidos
- app.py, chains.py, config.py, evolution_api.py
- memory.py, message_buffer.py, prompts.py, vectorstore.py
- Dockerfile, requirements.txt (antigos)

### Commit
```
chore: backup antes das correções críticas
```

---

## ✅ MINI-FASE 1: WEBHOOK DE PAGAMENTO (COMPLETA)

### O que foi implementado

1. **ClienteService** (`apps/backend/app/services/clientes/cliente_service.py`)
   - Geração automática de senha segura (12 caracteres)
   - Hash de senha com bcrypt
   - Criação de cliente a partir de dados do Stripe
   - Atualização de status de subscription
   - Métodos de busca (por email, por ID)

2. **Webhook de Billing Completo** (`apps/backend/app/api/v1/billing.py`)
   - Processa `checkout.session.completed` → Cria cliente
   - Processa `invoice.payment_succeeded` → Ativa cliente
   - Processa `customer.subscription.updated` → Atualiza status
   - Processa `customer.subscription.deleted` → Suspende cliente
   - Logs estruturados com emojis
   - Tratamento de erros robusto

3. **Correção do docker-compose.yml**
   - `build: .` → `build: ./apps/backend`
   - Adicionado `DATABASE_URL` no environment

### Fluxo Implementado

```
Cliente paga no Stripe
   ↓
Stripe envia webhook: checkout.session.completed
   ↓
Backend extrai: email, nome, telefone, customer_id, subscription_id
   ↓
Gera senha aleatória segura
   ↓
Cria hash com bcrypt
   ↓
Salva cliente no banco com status ATIVO
   ↓
Loga senha (para envio futuro por email na Fase 5)
   ↓
Cliente criado! ✅
```

### Teste Realizado

```bash
docker exec -it bot bash
python << 'EOF'
# Código de teste...
EOF
```

**Resultado:**
```
✅ Cliente criado com sucesso!
   ID: 1
   Nome: Cliente Teste
   Email: teste@exemplo.com
   Status: ClienteStatus.ATIVO
   🔑 Senha gerada: 2AEoRT1eVndV
✅ Cliente encontrado no banco de dados!
```

### Commits
```
feat: implementar webhook de pagamento completo (MINI-FASE 1)
fix: corrigir caminho do Dockerfile no docker-compose.yml
docs: adicionar guia de comandos rápidos
docs: adicionar status da MINI-FASE 1
```

### Arquivos Criados
- `apps/backend/app/services/clientes/cliente_service.py`
- `apps/backend/app/services/clientes/__init__.py`
- `apps/backend/test_webhook_manual.py`
- `TESTE_FASE_1.md`
- `STATUS_FASE_1.md`
- `COMANDOS_RAPIDOS.md`

### Arquivos Modificados
- `apps/backend/app/api/v1/billing.py`
- `docker-compose.yml`

---

## ✅ MINI-FASE 2: ISOLAMENTO MULTI-TENANT NO RAG (COMPLETA)

### O que foi implementado

1. **Vectorstore Multi-tenant** (`apps/backend/app/services/rag/vectorstore.py`)
   - Coleções isoladas por cliente: `tenant_{cliente_id}`
   - Função `get_collection_name(cliente_id)`
   - Função `criar_vectorstore_cliente(cliente_id, documentos)`
   - Função `deletar_vectorstore_cliente(cliente_id)`
   - Chunk size reduzido: 1000 → 800 (melhor precisão)
   - Overlap: 20% (160 chars)
   - Suporte a documentos por cliente em `rag_files/cliente_{id}/`

2. **Chains com Cliente ID** (`apps/backend/app/services/llm/chains.py`)
   - `get_rag_chain(cliente_id)` - RAG chain isolada
   - `get_conversational_rag_chain(cliente_id)` - Conversational chain isolada
   - Logs estruturados

3. **Message Buffer com Cliente ID** (`apps/backend/app/services/conversations/message_buffer.py`)
   - `buffer_message(chat_id, message, cliente_id)` - Aceita cliente_id
   - Session ID único: `cliente_{id}_{chat_id}`
   - Memória isolada por cliente
   - Limpeza de tasks após processamento
   - Logs estruturados

4. **Modelo InstanciaWhatsApp** (`apps/backend/app/db/models/instancia_whatsapp.py`)
   - Mapeia instâncias Evolution API → Cliente
   - Campos: id, cliente_id, instance_id, numero, status, qr_code
   - Status: PENDENTE, CONECTADA, DESCONECTADA, ERRO
   - Relacionamento com Cliente

5. **Migration 003** (`apps/backend/app/db/migrations/versions/003_add_instancias_whatsapp.py`)
   - Cria tabela `instancias_whatsapp`
   - Índices: cliente_id, instance_id (unique), numero

6. **Webhook com Lookup de Cliente** (`apps/backend/app/main.py`)
   - Busca cliente por `instance_id` (prioritário)
   - Fallback: busca por `numero`
   - Valida assinatura ativa (ClienteStatus.ATIVO)
   - Ignora mensagens de grupo (`@g.us`)
   - Passa `cliente_id` para processamento
   - Logs estruturados com emojis
   - Tratamento de erros robusto

### Fluxo Implementado

```
Mensagem chega no WhatsApp
   ↓
Evolution API envia para /webhook
   ↓
Webhook extrai instance_id ou numero
   ↓
Busca InstanciaWhatsApp no banco
   ↓
Identifica cliente_id
   ↓
Valida se cliente está ATIVO
   ↓
Passa cliente_id para buffer_message
   ↓
Buffer cria session_id: cliente_{id}_{chat_id}
   ↓
RAG chain usa vectorstore do cliente: tenant_{id}
   ↓
Resposta usa APENAS conhecimento do cliente ✅
```

### Isolamento Implementado

```
┌─────────────────────────────────────────────────────────┐
│                    ChromaDB                              │
├─────────────────────────────────────────────────────────┤
│  Collection: tenant_1                                    │
│  ├─ Documento 1: "Produto X custa R$ 100"              │
│  └─ Documento 2: "Produto X é azul"                    │
├─────────────────────────────────────────────────────────┤
│  Collection: tenant_2                                    │
│  ├─ Documento 1: "Produto Y custa R$ 200"              │
│  └─ Documento 2: "Produto Y é vermelho"                │
└─────────────────────────────────────────────────────────┘

Cliente 1 busca "produto" → Retorna apenas tenant_1 ✅
Cliente 2 busca "produto" → Retorna apenas tenant_2 ✅
```

### Teste Realizado

```bash
docker-compose down
docker-compose up -d --build
docker logs bot --tail 30
```

**Resultado:**
```
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, add instancias whatsapp table
✅ Migration rodou com sucesso!
✅ Aplicação iniciou sem erros!
```

**Teste de isolamento:**
```
1️⃣ Testando nomes de coleção...
   Cliente 1: tenant_1
   Cliente 2: tenant_2
✅ Código funcionando corretamente!
```

### Commits
```
feat: implementar isolamento multi-tenant no RAG (MINI-FASE 2)
docs: adicionar guias de teste da MINI-FASE 2
```

### Arquivos Criados
- `apps/backend/app/db/models/instancia_whatsapp.py`
- `apps/backend/app/db/migrations/versions/003_add_instancias_whatsapp.py`
- `TESTE_FASE_2.md`
- `STATUS_FASE_2.md`

### Arquivos Modificados
- `apps/backend/app/services/rag/vectorstore.py`
- `apps/backend/app/services/llm/chains.py`
- `apps/backend/app/services/conversations/message_buffer.py`
- `apps/backend/app/main.py`
- `apps/backend/app/db/models/__init__.py`

---

## ✅ MINI-FASE 3: SEGURANÇA BÁSICA (COMPLETA)

### O que foi implementado

1. **Pydantic Settings** (`apps/backend/app/core/config.py`)
   - Migrado de `os.getenv()` para `pydantic-settings`
   - Validação automática de variáveis obrigatórias
   - Type hints para todas as configurações
   - Valores padrão seguros
   - Método `get_allowed_origins_list()` para CORS
   - Falha rápida se variável obrigatória estiver faltando

2. **Módulo de Segurança** (`apps/backend/app/core/security.py`)
   - `verify_webhook_api_key()` - Valida API Key do webhook WhatsApp
   - `verify_evolution_api_key()` - Valida API Key da Evolution API
   - Modo desenvolvimento (sem API key) para facilitar testes
   - HTTPException padronizada para erros de autenticação

3. **Middlewares Customizados** (`apps/backend/app/core/middleware.py`)
   - `ErrorHandlerMiddleware` - Tratamento global de erros
     - Captura exceções não tratadas
     - Retorna respostas JSON padronizadas
     - Logs estruturados de erros com stack trace
   - `LoggingMiddleware` - Logging de requisições
     - Loga todas as requisições com método e path
     - Calcula tempo de processamento
     - Adiciona header `X-Process-Time` em todas as respostas

4. **Rate Limiting** (`apps/backend/app/main.py`)
   - Biblioteca `slowapi` integrada
   - Limite configurável via `RATE_LIMIT_PER_MINUTE` (padrão: 60)
   - Aplicado em todos os endpoints:
     - `/health` - Rate limited
     - `/health/db` - Rate limited
     - `/webhook` - Rate limited
   - Proteção contra spam e DDoS básico

5. **CORS Configurado** (`apps/backend/app/main.py`)
   - `CORSMiddleware` do FastAPI
   - Origens permitidas configuráveis via `ALLOWED_ORIGINS`
   - Suporta múltiplas origens (separadas por vírgula)
   - Permite credenciais
   - Permite todos os métodos e headers
   - Padrão: `http://localhost:3000,http://localhost:8000`

6. **Webhook Protegido** (`apps/backend/app/main.py`)
   - Webhook `/webhook` agora aceita API Key opcional
   - Header: `X-API-Key`
   - Se `WEBHOOK_API_KEY` não estiver configurado, permite acesso (modo dev)
   - Se configurado, valida antes de processar mensagem
   - Dependency injection com `Depends(verify_webhook_api_key)`

7. **Logging Melhorado** (`apps/backend/app/main.py`)
   - Formato estruturado: `timestamp - name - level - message`
   - Logs de inicialização com emojis:
     - 🚀 Aplicação iniciada
     - 🔒 CORS configurado
     - ⏱️ Rate limit configurado
   - Logs de requisições com emojis (📥 📤)
   - Logs incluem tempo de processamento

### Fluxo de Segurança Implementado

```
Requisição chega
   ↓
LoggingMiddleware: Loga entrada (📥)
   ↓
Rate Limiter: Valida limite de requisições
   ↓
CORS: Valida origem
   ↓
Endpoint: Processa requisição
   ↓
ErrorHandlerMiddleware: Captura erros (se houver)
   ↓
LoggingMiddleware: Loga saída (📤) + tempo
   ↓
Resposta com header X-Process-Time
```

### Teste Realizado

```bash
docker-compose down
docker-compose up -d --build
docker logs bot --tail 50
```

**Resultado:**
```
🚀 Aplicação iniciada com segurança habilitada
🔒 CORS configurado para: ['http://localhost:3000', 'http://localhost:8000']
⏱️ Rate limit: 60 req/min
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Teste de endpoints:**
```bash
curl http://localhost:8000/health
# {"status":"ok","service":"whatsapp-ai-bot"}
# Header: x-process-time: 0.015396356582641602

curl http://localhost:8000/health/db
# {"status":"ok","database":"connected","test_query":1}
# Header: x-process-time: 0.31118059158325195
```

### Commits
```
feat: implementar segurança básica (MINI-FASE 3)
```

### Arquivos Criados
- `apps/backend/app/core/security.py`
- `apps/backend/app/core/middleware.py`
- `.kiro/docs/STATUS_FASE_3.md`
- `.kiro/docs/TESTE_FASE_3.md`

### Arquivos Modificados
- `apps/backend/app/core/config.py`
- `apps/backend/app/main.py`
- `apps/backend/requirements.txt` (slowapi, python-jose)
- `.env.example`

---

## ⏳ PRÓXIMAS MINI-FASES (PENDENTES)

### MINI-FASE 3: Segurança Básica (40min)

**Objetivo:** Adicionar validações de segurança mínimas

**Tarefas:**
1. Adicionar validação de API key no webhook WhatsApp
2. Adicionar rate limiting básico (slowapi)
3. Configurar CORS
4. Adicionar validação de variáveis obrigatórias (Pydantic Settings)
5. Melhorar tratamento de erros

**Arquivos a modificar:**
- `apps/backend/app/core/config.py` (validações)
- `apps/backend/app/core/security.py` (NOVO - criar)
- `apps/backend/app/main.py` (adicionar middlewares)
- `apps/backend/requirements.txt` (adicionar slowapi)

---

### MINI-FASE 4: Testes Básicos (50min)

**Objetivo:** Criar testes automatizados para funcionalidades críticas

**Tarefas:**
1. Configurar pytest e pytest-asyncio
2. Criar fixtures para banco de dados de teste
3. Criar testes para webhook de pagamento (billing.py)
4. Criar testes para isolamento multi-tenant (vectorstore.py)
5. Criar testes para lookup de cliente (webhook)
6. Criar testes para segurança (rate limiting, CORS)

**Arquivos a criar:**
- `apps/backend/pytest.ini`
- `apps/backend/conftest.py`
- `apps/backend/app/tests/test_billing.py`
- `apps/backend/app/tests/test_webhook.py`
- `apps/backend/app/tests/test_multi_tenant.py`
- `apps/backend/app/tests/test_security.py`

---

### MINI-FASE 5: Melhorias de Performance (40min)

**Objetivo:** Otimizar pontos críticos

**Tarefas:**
1. Adicionar índices no banco
2. Configurar pool de conexões
3. Cachear vectorstore
4. Adicionar limite no buffer

**Arquivos a modificar:**
- `apps/backend/app/db/session.py` (pool)
- `apps/backend/app/db/migrations/versions/` (índices)
- `apps/backend/app/services/rag/vectorstore.py` (cache)
- `apps/backend/app/services/conversations/message_buffer.py` (limite)

---

### MINI-FASE 6: Limpeza e Documentação (30min)

**Objetivo:** Remover código legado e documentar

**Tarefas:**
1. Verificar se docs/legacy/ pode ser deletado
2. Atualizar README.md
3. Adicionar docstrings
4. Criar CHANGELOG.md

---

## 📁 ESTRUTURA DE ARQUIVOS ATUAL

```
/
├─ .kiro/
│  └─ docs/
│     └─ CONTEXTO_KIRO.md (ESTE ARQUIVO)
├─ apps/
│  ├─ backend/
│  │  ├─ app/
│  │  │  ├─ main.py ✅ (webhook com lookup)
│  │  │  ├─ api/v1/
│  │  │  │  └─ billing.py ✅ (webhook completo)
│  │  │  ├─ core/
│  │  │  │  └─ config.py ✅
│  │  │  ├─ db/
│  │  │  │  ├─ models/
│  │  │  │  │  ├─ cliente.py ✅
│  │  │  │  │  ├─ conversa.py ✅
│  │  │  │  │  ├─ mensagem.py ✅
│  │  │  │  │  ├─ instancia_whatsapp.py ✅ (NOVO)
│  │  │  │  │  └─ __init__.py ✅
│  │  │  │  ├─ migrations/versions/
│  │  │  │  │  ├─ 001_initial.py ✅
│  │  │  │  │  ├─ 002_add_stripe_fields.py ✅
│  │  │  │  │  └─ 003_add_instancias_whatsapp.py ✅ (NOVO)
│  │  │  │  ├─ base.py ✅
│  │  │  │  └─ session.py ✅
│  │  │  ├─ services/
│  │  │  │  ├─ clientes/
│  │  │  │  │  ├─ cliente_service.py ✅ (NOVO)
│  │  │  │  │  └─ __init__.py ✅ (NOVO)
│  │  │  │  ├─ conversations/
│  │  │  │  │  ├─ memory.py ✅
│  │  │  │  │  └─ message_buffer.py ✅ (multi-tenant)
│  │  │  │  ├─ llm/
│  │  │  │  │  ├─ chains.py ✅ (multi-tenant)
│  │  │  │  │  └─ prompts.py ✅
│  │  │  │  ├─ rag/
│  │  │  │  │  └─ vectorstore.py ✅ (multi-tenant)
│  │  │  │  └─ whatsapp/
│  │  │  │     └─ evolution_api.py ✅
│  │  │  └─ tests/ (vazio - FASE 4)
│  │  ├─ Dockerfile ✅
│  │  ├─ requirements.txt ✅
│  │  └─ entrypoint_fixed.sh ✅
│  └─ frontend/
│     ├─ app/
│     │  ├─ page.tsx ✅
│     │  ├─ login/page.tsx ✅
│     │  └─ checkout/page.tsx ✅
│     └─ components/ ✅
├─ docs/
│  └─ legacy/ (arquivos antigos movidos)
├─ infra/
│  └─ docker-compose.yml ✅
├─ docker-compose.yml ✅ (corrigido)
├─ .env.example ✅
├─ arquiterura.md ✅
├─ COMANDOS_RAPIDOS.md ✅
├─ TESTE_FASE_1.md ✅
├─ STATUS_FASE_1.md ✅
├─ TESTE_FASE_2.md ✅
└─ STATUS_FASE_2.md ✅
```

---

## 🔧 COMANDOS ÚTEIS

### Subir projeto
```bash
docker-compose down
docker-compose up -d --build
docker logs bot --tail 30
```

### Entrar no container
```bash
docker exec -it bot bash
```

### Ver banco de dados
```bash
docker exec -it postgres psql -U postgres -d whatsapp_bot
```

### Rodar migrations manualmente
```bash
docker exec -it bot bash
cd /app/apps/backend
alembic upgrade head
```

---

## 📝 NOTAS IMPORTANTES

### Problemas Resolvidos
- ✅ Webhook de pagamento agora persiste dados
- ✅ Isolamento multi-tenant implementado
- ✅ Lookup de cliente funcionando
- ✅ Validação de assinatura ativa
- ✅ Logs estruturados
- ✅ Rate limiting implementado
- ✅ CORS configurado
- ✅ Validação de variáveis de ambiente
- ✅ Tratamento global de erros
- ✅ Webhook protegido com API Key opcional

### Problemas Pendentes
- ⏳ Testes automatizados
- ⏳ Performance (índices, pool, cache)
- ⏳ Email de boas-vindas (Fase 5 do arquitetura.md)

### Decisões Técnicas
- Bcrypt para hash de senhas
- ChromaDB para vectorstore
- Coleções isoladas: `tenant_{cliente_id}`
- Session ID: `cliente_{id}_{chat_id}`
- Chunk size: 800 chars (overlap 20%)
- Logs com emojis para facilitar leitura

---

## 🎯 PRÓXIMOS PASSOS RECOMENDADOS

1. **Validar API key OpenAI** - Trocar no `.env` e testar embeddings
2. **Decidir próxima fase:**
   - MINI-FASE 3 (Segurança) - Recomendado
   - MINI-FASE 4 (Testes) - Importante
   - MINI-FASE 5 (Performance) - Opcional
3. **Testar com Stripe CLI** - Webhook real
4. **Criar instância WhatsApp para cliente de teste**

---

## 📞 COMO CONTINUAR EM NOVA CONVERSA

1. Ler este arquivo: `.kiro/docs/CONTEXTO_KIRO.md`
2. Verificar branch: `fix/critical-issues`
3. Ver último commit para entender onde parou
4. Ler `STATUS_FASE_2.md` para status atual
5. Decidir próxima mini-fase

---

**Última atualização:** 05/02/2026 17:35  
**Autor:** Kiro AI Assistant  
**Branch:** fix/critical-issues  
**Status:** MINI-FASE 3 COMPLETA ✅
