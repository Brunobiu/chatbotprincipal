SaaS Chatbot WhatsApp com IA (Multi-tenant) — Documento de Estrutura + Plano em Fases
Versão: 1.1
Data: 03/02/2026
Status: Aprovado para Implementação (Execução por Fases)


=====================================================================
0) Objetivo deste documento
=====================================================================
Este documento existe para:
1) Definir a ESTRUTURA PADRÃO (monorepo) do projeto (backend + frontend + infra).
2) Definir um PLANO EM FASES (passo a passo) para executar com IA/Dev sem quebrar o projeto.
3) Permitir migração segura do projeto atual (que hoje roda com Evolution API e módulos Python)
   para um SaaS completo com Landing Page + Pagamento + Dashboard + RAG + Controle Humano vs IA.


Regra de Ouro: UMA FASE POR VEZ.
- Só avance quando a fase atual estiver 100% funcionando e versionada (commit).
- Se der erro, corrija na fase atual antes de avançar.
- Sempre rode testes/healthcheck antes de seguir.


=====================================================================
1) Estrutura Recomendada (Monorepo)
=====================================================================
/
├─ apps/
│  ├─ backend/                  # FastAPI (API SaaS + Webhooks)
│  │  ├─ app/
│  │  │  ├─ main.py             # Entrypoint FastAPI
│  │  │  ├─ api/                # Rotas (routers)
│  │  │  │  ├─ v1/
│  │  │  │  │  ├─ auth.py
│  │  │  │  │  ├─ billing.py
│  │  │  │  │  ├─ whatsapp.py
│  │  │  │  │  ├─ knowledge.py
│  │  │  │  │  └─ conversations.py
│  │  │  ├─ core/               # config, segurança, logging, multi-tenant deps
│  │  │  │  ├─ config.py
│  │  │  │  ├─ security.py
│  │  │  │  └─ logging.py
│  │  │  ├─ db/                 # PostgreSQL (models, session, migrations)
│  │  │  │  ├─ base.py
│  │  │  │  ├─ session.py
│  │  │  │  ├─ models/
│  │  │  │  └─ migrations/
│  │  │  ├─ services/           # Regras de negócio (camadas)
│  │  │  │  ├─ rag/
│  │  │  │  │  ├─ vectorstore.py
│  │  │  │  │  ├─ embeddings.py
│  │  │  │  │  └─ chunking.py
│  │  │  │  ├─ llm/
│  │  │  │  │  ├─ chains.py
│  │  │  │  │  └─ prompts.py
│  │  │  │  ├─ whatsapp/
│  │  │  │  │  └─ evolution_api.py
│  │  │  │  ├─ conversations/
│  │  │  │  │  ├─ state_machine.py
│  │  │  │  │  ├─ memory.py
│  │  │  │  │  └─ message_buffer.py
│  │  │  │  └─ email/
│  │  │  ├─ workers/            # Celery tasks (processar embeddings etc.)
│  │  │  └─ utils/
│  │  │  ├─ tests/
│  │  │  ├─ Dockerfile
│  │  │  └─ requirements.txt
│  │
│  └─ frontend/                 # Next.js 14 + Tailwind
│     ├─ app/
│     │  ├─ (public)/           # Landing page pública
│     │  └─ dashboard/          # Área logada
│     ├─ components/
│     ├─ lib/
│     ├─ Dockerfile
│     └─ package.json
│
├─ infra/
│  ├─ docker-compose.yml        # postgres/redis/chroma/evolution/backend/frontend
│  └─ nginx/
│     └─ default.conf
│
├─ docs/
│  ├─ PRD.md                    # (Opcional) PRD completo do produto
│  └─ ARQUITETURA.md            # (Opcional) Arquitetura detalhada
│
├─ .env.example
├─ README.md
└─ .gitignore


=====================================================================
2) Como encaixar seu projeto atual nessa estrutura (migração segura)
=====================================================================
Pelo que você mostrou, hoje seu repo tem arquivos como:
- app.py
- evolution_api.py
- vectorstore.py
- chains.py
- prompts.py
- memory.py
- message_buffer.py
- docker-compose.yml
- Dockerfile
- etc.


MIGRAÇÃO RECOMENDADA (sem quebrar):
1) Criar a pasta apps/backend e mover os arquivos Python para dentro, mantendo imports funcionando.
2) Renomear app.py -> apps/backend/app/main.py (ou adaptar para virar main).
3) Reorganizar gradualmente:
   - evolution_api.py -> apps/backend/app/services/whatsapp/evolution_api.py
   - vectorstore.py   -> apps/backend/app/services/rag/vectorstore.py
   - chains.py        -> apps/backend/app/services/llm/chains.py
   - prompts.py       -> apps/backend/app/services/llm/prompts.py
   - memory.py        -> apps/backend/app/services/conversations/memory.py
   - message_buffer.py-> apps/backend/app/services/conversations/message_buffer.py
   - config.py        -> apps/backend/app/core/config.py
4) Em cada mudança: rodar o backend e garantir que o webhook/fluxo atual continua respondendo.


Estratégia anti-quebra:
- Não refatore tudo de uma vez.
- Primeiro só “muda de lugar” mantendo nomes/funções.
- Depois refatora com testes/healthcheck.


=====================================================================
3) Plano em Fases (passo a passo — execução segura)
=====================================================================
Abaixo estão fases sequenciais. Cada fase tem:
- Objetivo
- Tarefas
- Critérios de aceite (para NÃO avançar se não cumprir)


---------------------------------------------------------------------
FASE 1 — Organização do Repositório (sem mudar comportamento)
---------------------------------------------------------------------
Objetivo:
- Adotar a estrutura monorepo (apps/backend, infra, docs) sem quebrar o que já existe.


Tarefas:
1) Criar pastas: apps/backend/app, infra, docs, apps/frontend (vazio por enquanto).
2) Mover código atual para apps/backend (mantendo o projeto rodando).
3) Criar apps/backend/app/main.py como entrypoint (se hoje é app.py, adaptar).
4) Padronizar .env.example (sem colocar chaves reais).
5) Ajustar docker-compose para apontar para o backend no novo caminho (se já usa).
6) Criar endpoint GET /health no backend.


Aceite:
- docker-compose up (ou python) sobe sem erro.
- GET /health retorna 200.
- Seu fluxo atual com Evolution (o que já funciona hoje) continua funcionando.


---------------------------------------------------------------------
FASE 2 — Infra local mínima (Postgres + Redis) + Base de Config
---------------------------------------------------------------------
Objetivo:
- Ter Postgres e Redis disponíveis localmente para suportar multi-tenant, estados e histórico.


Tarefas:
1) Atualizar infra/docker-compose.yml para incluir:
   - postgres (porta interna 5432)
   - redis (porta interna 6379)
   - backend (porta 8000)
2) Criar conexão no backend (SQLAlchemy/asyncpg ou sync, você escolhe).
3) Criar tabela mínima “clientes” (id, nome, email, telefone, senha_hash, status).
4) Criar tabela mínima “conversas” (cliente_id, numero_usuario, estado, timestamps).
5) Criar migrations (Alembic recomendado).


Aceite:
- Backend conecta no Postgres.
- Migrações rodam (alembic upgrade head).
- Redis responde (ping).


---------------------------------------------------------------------
FASE 3 — Frontend inicial (Landing Page simples) + Rotas base
---------------------------------------------------------------------
Objetivo:
- Subir o frontend (Next.js) com uma landing page funcional e um botão “Quero Assinar”.


Tarefas:
1) Criar apps/frontend (Next.js 14 + Tailwind).
2) Landing page com:
   - Título, descrição, benefícios
   - Botão “Quero Assinar”
   - Link do botão apontando para /checkout (placeholder)
3) Criar página /login (UI simples, sem autenticar ainda).
4) Configurar proxy no Nginx (opcional) ou rodar separado no dev.


Aceite:
- Frontend sobe (npm run dev ou container).
- Landing renderiza.
- Botão funciona (navega para /checkout ou abre link).


Observação:
- Aqui ainda NÃO tem pagamento real. É só base visual.


---------------------------------------------------------------------
FASE 4 — Checkout (Pagamento) em modo teste + Webhook recebendo evento
---------------------------------------------------------------------
Objetivo:
- Implementar pagamento com Stripe (recomendado por simplicidade) OU PagSeguro.
- Pelo menos: criar checkout e receber webhook.


Tarefas:
1) Escolher gateway: Stripe (teste) ou PagSeguro (sandbox).
2) Criar endpoint no backend: POST /webhook/billing (valida assinatura do webhook).
3) Criar serviço billing para interpretar eventos:
   - pagamento aprovado
   - pagamento falhou
   - cancelamento
4) No frontend, botão “Quero Assinar” passa a redirecionar para o checkout real.


Aceite:
- Pagamento teste aprovado dispara webhook.
- Webhook é validado (assinatura) e loga evento “payment_success”.


---------------------------------------------------------------------
FASE 5 — Cadastro automático pós-pagamento + Email de boas-vindas
---------------------------------------------------------------------
Objetivo:
- Quando pagamento aprovar: criar conta automaticamente, gerar senha e enviar email.


Tarefas:
1) No webhook “payment_success”:
   - criar cliente no banco com status ATIVO
   - gerar senha aleatória segura e salvar hash
2) Criar envio de email (SendGrid/Mailgun) em modo teste:
   - email com login + senha
   - link do dashboard
3) Criar endpoint de login no backend (POST /api/v1/auth/login):
   - email + senha -> JWT


Aceite:
- Pagamento aprovado cria cliente no banco.
- Email é enviado (ou logado em dev).
- Login funciona e retorna token.


---------------------------------------------------------------------
FASE 6 — Dashboard base (UI) + Proteção (login obrigatório)
---------------------------------------------------------------------
Objetivo:
- Ter área logada com menu lateral e páginas vazias (scaffold), sem features complexas ainda.


Tarefas:
1) Criar layout do dashboard:
   - Menu lateral com: Meu Perfil, Meu Conhecimento, Conectar WhatsApp, Conversas, Config Bot, Tutoriais, Suporte, Sair
2) Implementar middleware/client-side guard (se não tiver token, manda pro /login).
3) Criar /api/me no backend para retornar dados do cliente logado.
4) Página “Meu Perfil” (read-only para nome/email/telefone) + troca de senha.


Aceite:
- Login -> entra no dashboard.
- /api/me responde corretamente.
- Alterar senha funciona.


---------------------------------------------------------------------
FASE 7 — Configurações do Bot (CRUD) + Templates de mensagens
---------------------------------------------------------------------
Objetivo:
- Cliente edita mensagens (Formal/Casual/Técnico).


Tarefas:
1) Criar tabela configuracoes_bot no Postgres.
2) Criar endpoints CRUD:
   - GET /config
   - PUT /config
3) Frontend: tela “Configurações do Bot” com formulário.
4) Definir defaults (saudação, fallback, espera, retorno 24h).


Aceite:
- Cliente altera e salva configs.
- Ao recarregar, aparece persistido.


---------------------------------------------------------------------
FASE 8 — Editor de Conhecimento (50k) + Chunking (sem embeddings ainda)
---------------------------------------------------------------------
Objetivo:
- Criar a tela e API para salvar texto do conhecimento com validação e chunking.


Tarefas:
1) Tabela conhecimentos (cliente_id, conteudo_texto, updated_at).
2) Endpoint:
   - GET /knowledge
   - PUT /knowledge (valida 50.000 chars)
3) Implementar chunking:
   - ~800 chars
   - overlap 20%
   - salvar chunks em estrutura interna (por enquanto sem vetor)
4) Frontend: textarea com contador e botão “Salvar”.


Aceite:
- Limite 50k bloqueia.
- Salvar e recuperar funciona.
- Chunking gera lista consistente (log).


---------------------------------------------------------------------
FASE 9 — Embeddings + Vector DB (ChromaDB) + Multi-tenant (coleção por cliente)
---------------------------------------------------------------------
Objetivo:
- Transformar chunks em embeddings e salvar em Chroma por cliente.


Tarefas:
1) Subir ChromaDB no docker-compose.
2) Criar camada vectorstore multi-tenant:
   - collection = “tenant_{cliente_id}”
3) Ao salvar conhecimento:
   - apagar coleção antiga
   - criar nova
   - gerar embeddings (OpenAI)
   - inserir documentos
4) Endpoint de busca interna (debug):
   - GET /knowledge/search?q=...


Aceite:
- Salvar conhecimento cria coleção isolada.
- Busca retorna chunks relevantes.
- Cliente A não encontra dados do B.


---------------------------------------------------------------------
FASE 10 — Integração Evolution API (instância por cliente) + QR no dashboard
---------------------------------------------------------------------
Objetivo:
- Cliente conecta WhatsApp via QR code e o sistema recebe mensagens.


Tarefas:
1) Tabela instancias_whatsapp (cliente_id, instance_id, status, qr_code_data).
2) Backend:
   - POST /whatsapp/instance (cria instância na Evolution)
   - GET  /whatsapp/status (status atual)
   - GET  /whatsapp/qrcode (retorna QR)
3) Frontend:
   - Tela “Conectar WhatsApp” exibe QR e status (polling ou SSE).
4) Filtro: ignorar mensagens de grupo (100% ignore).


Aceite:
- QR aparece.
- Conecta e status vira CONECTADO.
- Mensagem de grupo não dispara processamento.


---------------------------------------------------------------------
FASE 11 — Pipeline IA (RAG + Memória 10 mensagens) respondendo no WhatsApp
---------------------------------------------------------------------
Objetivo:
- Receber mensagem -> buscar contexto -> chamar OpenAI -> responder via Evolution.


Tarefas:
1) Webhook de mensagens da Evolution:
   - identifica cliente dono do número
   - valida assinatura ATIVA
   - ignora grupos
   - verifica estado da conversa
2) Memória:
   - guardar últimas 10 mensagens (Redis)
3) RAG:
   - buscar top-k chunks na coleção do cliente
   - montar prompt rígido (não inventar)
4) Enviar resposta via Evolution e registrar histórico.


Aceite:
- Mensagens comuns são respondidas em < 3s (média).
- Resposta usa contexto do cliente.
- Não responde sem assinatura ativa.


---------------------------------------------------------------------
FASE 12 — Confiança + Fallback para Humano (Estado da conversa)
---------------------------------------------------------------------
Objetivo:
- Quando confiança < 0.5: IA para e transfere para humano.
- Humano responde no dashboard, e IA não responde enquanto humano está ativo.


Tarefas:
1) Implementar cálculo de confiança:
   - baseado em similaridade média/top dos chunks retornados
2) Implementar estados:
   - IA_ATIVA
   - AGUARDANDO_HUMANO
   - HUMANO_RESPONDEU
3) Regras:
   - Se <0.5: envia mensagem fallback, muda estado para AGUARDANDO_HUMANO
   - Se estado != IA_ATIVA: não responder automaticamente
4) Dashboard:
   - Tela “Conversas” lista pendentes (AGUARDANDO)
   - Tela de chat para resposta humana (envia via Evolution)
   - Ao humano enviar: estado vira HUMANO_RESPONDEU


Aceite:
- Pergunta fora do conhecimento dispara fallback e IA para.
- Humano responde pelo dashboard e a mensagem chega no WhatsApp.
- IA não interfere após humano responder.


---------------------------------------------------------------------
FASE 13 — Retorno automático em 24h + Notificações por Email
---------------------------------------------------------------------
Objetivo:
- Se 24h sem resposta humana, IA volta a atuar automaticamente com mensagem de retorno.
- Enviar email “Atendimento pendente” ao cliente.


Tarefas:
1) Implementar cron/worker (Celery + Redis recomendado):
   - checar conversas AGUARDANDO_HUMANO ou HUMANO_RESPONDEU sem atividade
2) Enviar mensagens automáticas:
   - retorno após 24h
   - “ninguém respondeu em 24h” (se AGUARDANDO)
3) Enviar emails:
   - atendimento pendente
   - falha pagamento (grace)
   - suspensão


Aceite:
- Comportamento 24h funciona.
- Emails disparam corretamente.


---------------------------------------------------------------------
FASE 14 — Histórico 30 dias + Limpeza automática (TTL)
---------------------------------------------------------------------
Objetivo:
- Persistir histórico e deletar após 30 dias (política de retenção).


Tarefas:
1) Tabela historico_mensagens (conversa_id, tipo, conteudo, timestamp).
2) Criar job de limpeza (diário).
3) Dashboard mostra histórico no chat.


Aceite:
- Histórico aparece.
- Mensagens antigas são removidas pela rotina.


---------------------------------------------------------------------
FASE 15 — Testes, Observabilidade e Segurança
---------------------------------------------------------------------
Objetivo:
- Estabilizar e deixar pronto para produção.


Tarefas:
1) Testes básicos:
   - login
   - webhook billing
   - webhook whatsapp
   - isolamento multi-tenant
2) Logs estruturados e correlation id por request.
3) Rate limit básico para webhook.
4) HTTPS obrigatório em produção (Nginx + Let's Encrypt).


Aceite:
- Testes passam.
- Logs ajudam a debugar.
- Sem endpoints expostos sem auth (exceto webhooks + health).


---------------------------------------------------------------------
FASE 16 — Deploy Produção (VPS) + Backup + Monitoramento
---------------------------------------------------------------------
Objetivo:
- Colocar online 24/7 com segurança.


Tarefas:
1) VPS Ubuntu + Docker + Docker Compose.
2) Nginx reverse proxy + SSL.
3) DNS e domínio.
4) Backups automáticos Postgres (diário).
5) Monitoramento uptime.


Aceite:
- Sistema acessível pelo domínio.
- SSL ativo.
- Backups executando.


=====================================================================
4) Checklist rápido antes de pedir para a IA executar uma fase
=====================================================================
- [ ] Estamos em qual fase exatamente?
- [ ] Qual tarefa única vamos executar agora?
- [ ] Quais arquivos serão alterados?
- [ ] Como eu testo que funcionou?
- [ ] Já fiz commit antes de mexer?


=====================================================================
5) Observação final (ordem “Landing primeiro” vs “Infra primeiro”)
=====================================================================
Você pode começar pela Landing (FASE 3) para “ver algo na tela”, mas o MAIS SEGURO é:
FASE 1 -> FASE 2 -> FASE 3
Porque:
- sem infra e estrutura, você retrabalha o frontend depois.
- com base pronta, você conecta tudo com menos dor.


=====================================================================
Fim do documento
=====================================================================
