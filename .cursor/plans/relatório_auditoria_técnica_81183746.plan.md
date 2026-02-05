---
name: Relatório Auditoria Técnica
overview: Auditoria técnica completa das Fases 1 a 4 do projeto SaaS Chatbot WhatsApp, comparando o documento arquiterura.md com os arquivos físicos do repositório, incluindo qualidade de código, imports, conexões de banco e Docker.
todos: []
isProject: false
---

# Relatório de Auditoria Técnica - Fases 1 a 4

**Documento de referência:** [arquiterura.md](arquiterura.md) (arquivo de fases)  
**Data da auditoria:** 04/02/2026  
**Escopo:** Validar implementação das Fases 1, 2, 3 e 4 conforme estrutura monorepo e regras de negócio.

---

## Fase 1: Organização do Repositório


| Item                                                              | Status      | Observação Técnica                                                                                                                                                                                                                                                                                |
| ----------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1.1 Pastas criadas (apps/backend, infra, docs, apps/frontend)** | [ ] Parcial | `apps/backend`, `apps/frontend` e `infra` existem. Pasta `docs` **não existe** (opcional segundo arquitetura, mas faz parte da estrutura recomendada).                                                                                                                                            |
| **1.2 Código movido para apps/backend**                           | [X]         | Migração realizada: `evolution_api`, `vectorstore`, `chains`, `prompts`, `memory`, `message_buffer`, `config` em [apps/backend/app/](apps/backend/app/).                                                                                                                                          |
| **1.3 Arquivos legados na raiz (duplicados)**                     | [ ]         | **Conflito:** Arquivos antigos permanecem na raiz: `app.py`, `evolution_api.py`, `vectorstore.py`, `chains.py`, `prompts.py`, `memory.py`, `message_buffer.py`, `config.py`. O [docker-compose.yml](docker-compose.yml) da raiz usa `build: .` e executa `app:app` (raiz), não o backend em apps. |
| **1.4 main.py como entrypoint**                                   | [X]         | [apps/backend/app/main.py](apps/backend/app/main.py) é o entrypoint correto (uvicorn app.main:app).                                                                                                                                                                                               |
| **1.5 .env.example padronizado**                                  | [X]         | [.env.example](.env.example) existe com placeholders para Stripe, DB, Evolution, Redis (sem chaves reais).                                                                                                                                                                                        |
| **1.6 docker-compose apontando para novo caminho**                | [ ] Parcial | **[infra/docker-compose.yml](infra/docker-compose.yml)** aponta para `build: ../apps/backend` — correto. Já o **[docker-compose.yml](docker-compose.yml) na raiz** ainda usa `build: .` e `app:app` (legado). Há dois compose conflitantes.                                                       |
| **1.7 Endpoint GET /health**                                      | [X]         | Implementado em [main.py](apps/backend/app/main.py) linha 14-16. Retorna `{status: ok, service: whatsapp-ai-bot}`.                                                                                                                                                                                |


**Aceite Fase 1:** O fluxo Evolution atual funciona **apenas** via `infra/docker-compose.yml`. O compose da raiz usa stack legada e não reflete a estrutura monorepo.

---

## Fase 2: Infra Local & Banco de Dados


| Item                                                                           | Status | Observação Técnica                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------------ | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **2.1 infra/docker-compose com postgres (5432), redis (6379), backend (8000)** | [X]    | [infra/docker-compose.yml](infra/docker-compose.yml) inclui postgres, redis, evolution-api, bot e frontend. Postgres 5432, Redis 6379, Backend 8000 expostos.                                                                                                                                  |
| **2.2 Conexão backend com Postgres (SQLAlchemy)**                              | [X]    | [apps/backend/app/db/session.py](apps/backend/app/db/session.py) usa `create_engine(DATABASE_URL)` e [config.py](apps/backend/app/core/config.py) define `DATABASE_URL` com default `postgresql://postgres:postgres@postgres:5432/whatsapp_bot`.                                               |
| **2.3 Tabela clientes**                                                        | [X]    | [apps/backend/app/db/models/cliente.py](apps/backend/app/db/models/cliente.py): id, nome, email, telefone, senha_hash, status. Migração [001_initial.py](apps/backend/app/db/migrations/versions/001_initial.py).                                                                              |
| **2.4 Tabela conversas**                                                       | [X]    | [apps/backend/app/db/models/conversa.py](apps/backend/app/db/models/conversa.py): cliente_id, numero_usuario, estado, timestamps. Migração 001.                                                                                                                                                |
| **2.5 Migrações Alembic**                                                      | [X]    | Alembic configurado em [alembic.ini](apps/backend/alembic.ini) e [env.py](apps/backend/app/db/migrations/env.py). Duas versões: 001 (clientes, conversas, mensagens), 002 (campos Stripe em clientes). [entrypoint_fixed.sh](apps/backend/entrypoint_fixed.sh) executa `alembic upgrade head`. |
| **2.6 Postgres cria DB whatsapp_bot**                                          | [X]    | [infra/docker-compose.yml](infra/docker-compose.yml) define `POSTGRES_DB=whatsapp_bot` no serviço postgres.                                                                                                                                                                                    |
| **2.7 Redis disponível**                                                       | [X]    | Redis no compose. `message_buffer.py` usa `CACHE_REDIS_URI` (mapeada para REDIS_URL em config).                                                                                                                                                                                                |


**Observação:** O [docker-compose.yml](docker-compose.yml) da **raiz** não define `POSTGRES_DB`, criando apenas o DB padrão `postgres`. Uso do compose da raiz geraria erro de conexão ao banco `whatsapp_bot`.

---

## Fase 3: Frontend Inicial


| Item                                             | Status | Observação Técnica                                                                                                                                                                                                                  |
| ------------------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **3.1 apps/frontend (Next.js 14 + Tailwind)**    | [X]    | [package.json](apps/frontend/package.json): Next.js 14.0.0, Tailwind configurado.                                                                                                                                                   |
| **3.2 Landing: título, descrição, benefícios**   | [X]    | [app/page.tsx](apps/frontend/app/page.tsx) monta Header, Hero, Benefits, Footer. [Hero.tsx](apps/frontend/components/Hero.tsx) com título e descrição. [Benefits.tsx](apps/frontend/components/Benefits.tsx) presente.              |
| **3.3 Botão "Quero Assinar" -> /checkout**       | [X]    | [Hero.tsx](apps/frontend/components/Hero.tsx) linha 22-27: `<Link href="/checkout">Quero Assinar</Link>`.                                                                                                                           |
| **3.4 Página /login (UI simples)**               | [X]    | [apps/frontend/app/login/page.tsx](apps/frontend/app/login/page.tsx) com formulário visual (sem auth, conforme Fase 3).                                                                                                             |
| **3.5 Frontend sobe (container ou npm run dev)** | [ ]    | **[apps/frontend/Dockerfile](apps/frontend/Dockerfile)** linha 25: `COPY public ./public` — pasta `public` **não existe** no frontend. O build Docker **falhará** com "no such file or directory". Em `npm run dev` local funciona. |
| **3.6 Proxy Nginx (opcional)**                   | [ ]    | Pasta `infra/nginx/` e `default.conf` **não existem**. Documento marca como opcional.                                                                                                                                               |


**Aceite Fase 3:** Landing e botão funcionam em dev. **Build Docker do frontend falha** por falta da pasta `public`.

---

## Fase 4: Checkout e Billing (Stripe)


| Item                                                                  | Status      | Observação Técnica                                                                                                                                                                                                                |
| --------------------------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **4.1 Gateway Stripe em modo teste**                                  | [X]         | [billing.py](apps/backend/app/api/v1/billing.py) usa `stripe`; config com `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_LOOKUP_KEY`.                                                                                |
| **4.2 Endpoint POST /webhook/billing (valida assinatura)**            | [X]         | Webhook em `POST /api/v1/billing/webhook` (rota montada em [main.py](apps/backend/app/main.py)). Valida assinatura quando `STRIPE_WEBHOOK_SECRET` configurado.                                                                    |
| **4.3 Serviço billing para eventos (aprovado, falhou, cancelamento)** | [ ] Parcial | Tratamento básico: `checkout.session.completed`, `invoice.payment_succeeded`, `customer.subscription.*` — apenas **log (print)**. Sem persistência (TODO na linha 87). Eventos de falha/cancelamento não tratados explicitamente. |
| **4.4 Botão "Quero Assinar" redireciona para checkout real**          | [X]         | [checkout/page.tsx](apps/frontend/app/checkout/page.tsx) chama `POST /api/v1/billing/create-checkout-session`, recebe URL Stripe e redireciona.                                                                                   |
| **4.5 Webhook loga "payment_success"**                                | [ ] Parcial | Loga `checkout.session.completed` e `invoice.payment_succeeded`, mas sem string literal "payment_success". Aceite exige que evento de pagamento aprovado seja identificado e logado — implementado via prints dos eventos.        |


**Aceite Fase 4:** Checkout funciona. Webhook valida assinatura e processa eventos. Persistência no banco e tratamento explícito de falha/cancelamento pendentes (previstos para Fase 5).

---

## Diagrama de Dependências Atual

```mermaid
flowchart TB
    subgraph Root ["Raiz (Legado)"]
        RootDocker[docker-compose.yml]
        RootDockerfile[Dockerfile]
        RootApp[app.py]
    end
    
    subgraph Infra ["infra/ (Recomendado)"]
        InfraCompose[docker-compose.yml]
    end
    
    subgraph Backend ["apps/backend"]
        Main[main.py]
        Billing[billing.py]
        DB[db/session + models]
        Migrations[alembic]
    end
    
    subgraph Frontend ["apps/frontend"]
        Landing[Landing Page]
        Checkout[Checkout Page]
        DockerfileFE[Dockerfile]
    end
    
    RootDocker --> RootDockerfile
    RootDocker --> RootApp
    InfraCompose --> Backend
    InfraCompose --> Frontend
    Main --> Billing
    Main --> DB
    Billing --> stripe[Stripe API]
    Checkout --> Main
    DockerfileFE -.->|"COPY public FALHA"| Frontend
```



---

## Conclusão Final

### Diagnóstico

**O projeto NÃO está íntegro e pronto para rodar testes de integração end-to-end sem correções.**

### Erros Críticos (correção imediata)

1. **Build Docker do frontend quebra:** `COPY public ./public` falha porque a pasta `public` não existe. Solução: criar pasta vazia ou remover/ajustar a linha no Dockerfile.
2. **Dois docker-compose conflitantes:** O compose da raiz aponta para stack legada e não cria o banco `whatsapp_bot`. Para consistência, o compose da raiz deve ser descontinuado ou redirecionado para `infra/`.
3. **Arquivos duplicados na raiz:** Podem causar confusão e imports incorretos. Recomendação: remover ou mover para `docs/legacy/` após validar que o fluxo via `infra/` está estável.

### Pontos de Atenção (não bloqueantes para smoke tests)

- Persistência de pagamentos no webhook (Fase 5)
- Tratamento explícito de `payment_failed` e cancelamento
- Pasta `docs/` e `infra/nginx/` (opcionais)

### Próximos passos sugeridos

1. Corrigir [apps/frontend/Dockerfile](apps/frontend/Dockerfile) (remover `COPY public` ou criar pasta vazia).
2. Padronizar uso de `infra/docker-compose.yml` como compose oficial e documentar no README.
3. Executar `docker-compose -f infra/docker-compose.yml up --build` e validar: `/health`, `/health/db`, landing, checkout e webhook Stripe.
4. Após validação, planejar remoção dos arquivos legados da raiz.

