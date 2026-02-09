SaaS Chatbot WhatsApp com IA (Multi-tenant) — Documento de Estrutura + Plano em Fases
Versão: 2.0
Data: 06/02/2026
Status: Aprovado para Implementação (Execução por Fases)
Atualização: Adicionado FASE 16 (Painel Admin Completo) com 16 mini-fases


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
[X] [X] FASE 1 — Organização do Repositório (sem mudar comportamento)
---------------------------------------------------------------------
Objetivo:
- Adotar a estrutura monorepo (apps/backend, infra, docs) sem quebrar o que já existe.


Tarefas:
1) [X] Criar pastas: apps/backend/app, infra, docs, apps/frontend (vazio por enquanto).
2) [X] Mover código atual para apps/backend (mantendo o projeto rodando).
3) [X] Criar apps/backend/app/main.py como entrypoint (se hoje é app.py, adaptar).
4) [X] Padronizar .env.example (sem colocar chaves reais).
5) [X] Ajustar docker-compose para apontar para o backend no novo caminho (se já usa).
6) [X] Criar endpoint GET /health no backend.


Aceite:
- [X] docker-compose up (ou python) sobe sem erro.
- [X] GET /health retorna 200.
- [X] Seu fluxo atual com Evolution (o que já funciona hoje) continua funcionando.


---------------------------------------------------------------------
[X] FASE 2 — Infra local mínima (Postgres + Redis) + Base de Config
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
[X] FASE 3 — Frontend inicial (Landing Page simples) + Rotas base
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
[X] FASE 4 — Checkout (Pagamento) em modo teste + Webhook recebendo evento
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
[X] FASE 5 — Cadastro automático pós-pagamento + Email de boas-vindas
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
[X] FASE 6 — Dashboard base (UI) + Proteção (login obrigatório)
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
[X] FASE 7 — Configurações do Bot (CRUD) + Templates de mensagens
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
[X] FASE 8 — Editor de Conhecimento (50k) + Chunking (sem embeddings ainda)
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
[X] FASE 9 — Embeddings + Vector DB (ChromaDB) + Multi-tenant (coleção por cliente)
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
[X] FASE 10 — Integração Evolution API (instância por cliente) + QR no dashboard
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
[X] FASE 11 — Pipeline IA (RAG + Memória 10 mensagens) respondendo no WhatsApp
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
[X] FASE 12 — Confiança + Fallback para Humano (Estado da conversa)
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
[X] FASE 13 — Retorno automático em 24h + Notificações por Email
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
FASE 16 — PAINEL ADMIN COMPLETO (Gestão do SaaS)
---------------------------------------------------------------------
Objetivo:
- Criar painel administrativo completo para o dono do SaaS gerenciar clientes,
  vendas, suporte, tutoriais, segurança e todas as operações do negócio.

IMPORTANTE: Esta fase está dividida em MINI-FASES para execução segura.
Cada mini-fase deve ser testada e comitada antes de avançar.


---------------------------------------------------------------------
[X] MINI-FASE 16.1 — Estrutura Base + Login Admin
---------------------------------------------------------------------
Objetivo:
- Criar estrutura separada para painel admin com autenticação própria.

Tarefas:
1) Criar tabela "admins" no banco:
   - id, nome, email, senha_hash, role (super_admin, admin), created_at
2) Criar seed para primeiro admin (você)
3) Backend:
   - POST /api/v1/admin/auth/login (retorna JWT com role=admin)
   - GET /api/v1/admin/auth/me (valida token admin)
4) Frontend:
   - Criar /admin/login (página separada do cliente)
   - Criar /admin/dashboard (layout base com sidebar)
   - Middleware: só admin pode acessar /admin/*

Aceite:
- Login admin funciona
- Redireciona para /admin/dashboard
- Cliente não consegue acessar área admin


---------------------------------------------------------------------
[X] MINI-FASE 16.2 — Dashboard Overview (Métricas Principais)
---------------------------------------------------------------------
Objetivo:
- Página inicial do admin com KPIs e gráficos principais.

Tarefas:
1) [X] Backend - Criar endpoint GET /api/v1/admin/dashboard/metrics:
   - Total de clientes (ativos, suspensos, pendentes)
   - MRR (Monthly Recurring Revenue)
   - Novos clientes (hoje, semana, mês)
   - Cancelamentos (hoje, semana, mês)
   - Taxa de conversão
   - Ticket médio
2) [X] Frontend:
   - Cards com métricas principais
   - Gráfico de vendas por dia (últimos 30 dias)
   - Gráfico de receita mensal (últimos 6 meses)
   - Lista de últimos 5 clientes cadastrados

Aceite:
- [X] Dashboard mostra métricas em tempo real
- [X] Gráficos renderizam corretamente
- [X] Dados batem com banco de dados


---------------------------------------------------------------------
MINI-FASE -+ — Gestão de Clientes (CRUD Completo)
---------------------------------------------------------------------
Objetivo:
- Visualizar, editar, suspender e gerenciar todos os clientes.

Tarefas:
1) Backend - Endpoints:
   - GET /api/v1/admin/clientes (lista com filtros e paginação)
   - GET /api/v1/admin/clientes/:id (detalhes completos)
   - PUT /api/v1/admin/clientes/:id (editar dados)
   - POST /api/v1/admin/clientes/:id/suspender
   - POST /api/v1/admin/clientes/:id/ativar
   - POST /api/v1/admin/clientes/:id/resetar-senha
2) Tabela adicionar campos:
   - ultimo_login, ip_ultimo_login, total_mensagens_enviadas
3) Frontend:
   - Tabela de clientes com filtros (status, data, nome, email)
   - Página de detalhes do cliente (histórico completo)
   - Botões: Editar, Suspender, Ativar, Resetar Senha
   - Modal de confirmação para ações críticas

Aceite:
- Lista todos os clientes com paginação
- Filtros funcionam
- Edição salva corretamente
- Suspender/Ativar atualiza status
- Resetar senha gera nova senha e envia email


---------------------------------------------------------------------
MINI-FASE 16.4 — Monitoramento de Uso (Créditos OpenAI)
---------------------------------------------------------------------
Objetivo:
- Rastrear uso de créditos OpenAI por cliente para controle de custos.

Tarefas:
1) Criar tabela "uso_openai":
   - cliente_id, data, tokens_usados, custo_estimado, mensagens_processadas
2) Modificar AIService para logar uso:
   - Salvar tokens de cada chamada (prompt + completion)
   - Calcular custo baseado no modelo usado
3) Backend - Endpoints:
   - GET /api/v1/admin/uso/resumo (top 10 clientes que mais gastam)
   - GET /api/v1/admin/uso/cliente/:id (histórico detalhado)
   - GET /api/v1/admin/uso/alertas (clientes acima do threshold)
4) Frontend:
   - Dashboard com ranking de uso
   - Gráfico de custo por cliente
   - Alertas de clientes gastando muito
   - Configurar threshold de alerta

Aceite:
- Cada mensagem processada registra uso
- Dashboard mostra top gastadores
- Alertas disparam quando threshold ultrapassado
- Histórico detalhado por cliente disponível


---------------------------------------------------------------------
MINI-FASE 16.5 — Sistema de Tickets/Suporte (Cliente → Admin)
---------------------------------------------------------------------
Objetivo:
- Clientes abrem tickets, IA responde primeiro, admin responde se necessário.

Tarefas:
1) Criar tabelas:
   - "tickets" (id, cliente_id, assunto, categoria, status, prioridade, created_at)
   - "ticket_mensagens" (ticket_id, remetente_tipo, remetente_id, mensagem, anexos, created_at)
   - "ticket_categorias" (id, nome, descricao) - Financeiro, Técnico, Dúvida, etc.
2) Backend - Cliente:
   - POST /api/v1/tickets (criar ticket com até 10 anexos)
   - GET /api/v1/tickets (listar meus tickets)
   - POST /api/v1/tickets/:id/mensagens (responder ticket)
3) Backend - Admin:
   - GET /api/v1/admin/tickets (todos os tickets com filtros)
   - POST /api/v1/admin/tickets/:id/responder
   - PUT /api/v1/admin/tickets/:id/status (aberto, em_andamento, resolvido, fechado)
   - POST /api/v1/admin/tickets/:id/atribuir (atribuir para admin específico)
4) IA Responde Primeiro:
   - Quando ticket criado, IA analisa com base em conhecimento admin
   - Se confiança > 0.7: responde automaticamente
   - Se confiança < 0.7: marca como "aguardando_admin"
5) Frontend - Cliente:
   - Widget de chat flutuante no dashboard
   - Botão "Abrir Ticket" quando IA não sabe
   - Modal com formulário (categoria, assunto, descrição, anexos)
   - Visualizar tickets abertos e histórico
6) Frontend - Admin:
   - Página "Suporte" com lista de tickets
   - Badge de notificação (tickets não lidos)
   - Interface de chat para responder
   - Filtros: status, categoria, prioridade, data

Aceite:
- Cliente abre ticket pelo dashboard
- IA responde automaticamente quando sabe
- Admin recebe notificação de novos tickets
- Admin responde e cliente vê resposta
- Anexos funcionam (upload e download)
- Status atualiza corretamente


---------------------------------------------------------------------
MINI-FASE 16.6 — Gestão de Tutoriais (Vídeos para Clientes)
---------------------------------------------------------------------
Objetivo:
- Admin adiciona vídeos de tutorial que aparecem para todos os clientes.

Tarefas:
1) Criar tabelas:
   - "tutoriais" (id, titulo, descricao, video_url, thumbnail_url, ordem, ativo, created_at)
   - "tutorial_comentarios" (id, tutorial_id, cliente_id, comentario, created_at)
   - "tutorial_visualizacoes" (tutorial_id, cliente_id, visualizado_em)
2) Backend - Admin:
   - POST /api/v1/admin/tutoriais (criar tutorial)
   - PUT /api/v1/admin/tutoriais/:id (editar)
   - DELETE /api/v1/admin/tutoriais/:id
   - PUT /api/v1/admin/tutoriais/reordenar (mudar ordem)
3) Backend - Cliente:
   - GET /api/v1/tutoriais (listar ativos)
   - POST /api/v1/tutoriais/:id/visualizar (marcar como visto)
   - POST /api/v1/tutoriais/:id/comentarios (comentar)
   - GET /api/v1/tutoriais/:id/comentarios (listar comentários)
4) Notificações:
   - Quando novo tutorial publicado, criar notificação para todos os clientes
5) Frontend - Admin:
   - Página "Tutoriais" com lista
   - Formulário: título, descrição, URL do vídeo (YouTube/Vimeo), thumbnail
   - Drag-and-drop para reordenar
   - Toggle ativo/inativo
   - Ver estatísticas (quantos visualizaram, comentários)
6) Frontend - Cliente:
   - Página "Tutoriais" no menu do dashboard
   - Grid de vídeos com thumbnail
   - Player de vídeo (embed YouTube/Vimeo)
   - Seção de comentários abaixo
   - Badge "Novo" em tutoriais não visualizados

Aceite:
- Admin cria tutorial e aparece para todos os clientes
- Clientes recebem notificação de novo tutorial
- Vídeo reproduz corretamente
- Comentários funcionam
- Admin vê estatísticas de visualização


---------------------------------------------------------------------
MINI-FASE 16.7 — Avisos e Anúncios do Sistema
---------------------------------------------------------------------
Objetivo:
- Admin cria avisos que aparecem para todos os clientes (banner no topo).

Tarefas:
1) Criar tabela "avisos":
   - id, tipo (info, warning, error, success), titulo, mensagem, ativo, data_inicio, data_fim
2) Backend:
   - POST /api/v1/admin/avisos (criar aviso)
   - GET /api/v1/avisos/ativos (clientes veem avisos ativos)
   - PUT /api/v1/admin/avisos/:id (editar)
   - DELETE /api/v1/admin/avisos/:id
3) Frontend - Admin:
   - Página "Avisos" com lista
   - Formulário: tipo, título, mensagem, período de exibição
   - Preview do aviso
4) Frontend - Cliente:
   - Banner no topo do dashboard (fixo ou dismissível)
   - Cores diferentes por tipo (azul=info, amarelo=warning, vermelho=error)
   - Botão X para fechar (se dismissível)

Aceite:
- Admin cria aviso e aparece para todos os clientes
- Aviso respeita período de exibição
- Clientes podem fechar aviso (se configurado)
- Múltiplos avisos empilham corretamente


---------------------------------------------------------------------
MINI-FASE 16.8 — Relatórios Avançados (Exportação PDF/Excel)
---------------------------------------------------------------------
Objetivo:
- Gerar relatórios detalhados e exportar em PDF ou Excel.

Tarefas:
1) Backend - Endpoints:
   - GET /api/v1/admin/relatorios/vendas (filtros: data_inicio, data_fim, formato)
   - GET /api/v1/admin/relatorios/clientes (filtros: status, plano, formato)
   - GET /api/v1/admin/relatorios/uso-openai (filtros: cliente_id, periodo, formato)
   - GET /api/v1/admin/relatorios/tickets (filtros: status, categoria, formato)
2) Implementar geração:
   - PDF: usar ReportLab ou WeasyPrint
   - Excel: usar openpyxl ou xlsxwriter
3) Frontend:
   - Página "Relatórios" com formulários de filtros
   - Botões "Exportar PDF" e "Exportar Excel"
   - Preview de dados antes de exportar
   - Histórico de relatórios gerados (últimos 10)

Aceite:
- Relatórios geram corretamente em PDF e Excel
- Filtros funcionam
- Download inicia automaticamente
- Dados no relatório batem com dashboard


---------------------------------------------------------------------
MINI-FASE 16.9 — Segurança e Auditoria
---------------------------------------------------------------------
Objetivo:
- Monitorar tentativas de login, IPs suspeitos e atividades.

Tarefas:
1) Criar tabelas:
   - "login_attempts" (email, ip, sucesso, user_agent, timestamp)
   - "ips_bloqueados" (ip, motivo, bloqueado_ate)
   - "audit_log" (admin_id, acao, recurso, detalhes, ip, timestamp)
2) Implementar:
   - Logar todas as tentativas de login (admin e cliente)
   - Bloquear IP após 5 tentativas falhas em 15 minutos
   - Logar todas as ações de admin (criar, editar, deletar, suspender)
3) Backend:
   - GET /api/v1/admin/seguranca/tentativas-login
   - GET /api/v1/admin/seguranca/ips-bloqueados
   - POST /api/v1/admin/seguranca/desbloquear-ip
   - GET /api/v1/admin/seguranca/audit-log
4) Frontend:
   - Página "Segurança" com abas:
     - Tentativas de Login (últimas 100)
     - IPs Bloqueados (com botão desbloquear)
     - Log de Auditoria (todas as ações de admin)
   - Filtros por data, IP, email, ação

Aceite:
- Tentativas de login são logadas
- IPs bloqueados após 5 falhas
- Admin pode desbloquear IP
- Audit log registra todas as ações de admin
- Dashboard de segurança mostra atividades suspeitas


---------------------------------------------------------------------
MINI-FASE 16.10 — Notificações para Admin
---------------------------------------------------------------------
Objetivo:
- Admin recebe notificações de eventos importantes.

Tarefas:
1) Criar tabela "notificacoes_admin":
   - id, tipo, titulo, mensagem, lida, link, created_at
2) Eventos que geram notificação:
   - Novo cliente cadastrado
   - Pagamento recusado
   - Plano expirado
   - Novo ticket aberto
   - Cliente gastando muito crédito OpenAI
   - Tentativa de invasão (múltiplas falhas de login)
3) Backend:
   - GET /api/v1/admin/notificacoes (últimas 50)
   - PUT /api/v1/admin/notificacoes/:id/ler
   - PUT /api/v1/admin/notificacoes/ler-todas
4) Frontend:
   - Ícone de sino no header com badge (quantidade não lidas)
   - Dropdown com lista de notificações
   - Click na notificação: marca como lida e redireciona
   - Página "Todas as Notificações" com histórico completo

Aceite:
- Notificações aparecem em tempo real
- Badge atualiza automaticamente
- Click marca como lida
- Link redireciona para recurso correto


---------------------------------------------------------------------
MINI-FASE 16.11 — Admin Usa Própria Ferramenta
---------------------------------------------------------------------
Objetivo:
- Admin tem acesso à ferramenta completa sem precisar pagar.

Tarefas:
1) Criar cliente especial para admin:
   - Ao criar admin, criar cliente vinculado automaticamente
   - Status sempre ATIVO, sem cobrança
2) Backend:
   - GET /api/v1/admin/minha-ferramenta/acessar (retorna token de cliente admin)
3) Frontend:
   - Menu "Minha Ferramenta" no painel admin
   - Click: faz login automático como cliente e redireciona para /dashboard
   - Admin pode usar conhecimento, WhatsApp, conversas, etc.
   - Botão "Voltar para Admin" no dashboard do cliente

Aceite:
- Admin acessa ferramenta sem pagar
- Pode conectar WhatsApp e usar todas as features
- Dados do admin não misturam com clientes reais
- Fácil alternar entre painel admin e ferramenta


---------------------------------------------------------------------
MINI-FASE 16.12 — Tema Dark/Light (Só Admin)
---------------------------------------------------------------------
Objetivo:
- Admin pode escolher tema escuro ou claro no painel.

Tarefas:
1) Adicionar campo "tema" na tabela admins (dark, light)
2) Backend:
   - PUT /api/v1/admin/preferencias (salvar tema)
3) Frontend:
   - Toggle no header (ícone de sol/lua)
   - Salvar preferência no backend e localStorage
   - Aplicar tema em todas as páginas do admin
   - CSS variables para cores (fácil trocar)

Aceite:
- Toggle muda tema instantaneamente
- Tema persiste após reload
- Todas as páginas respeitam tema escolhido
- Contraste adequado em ambos os temas


---------------------------------------------------------------------
MINI-FASE 16.13 — Monitoramento de Sistema (Saúde)
---------------------------------------------------------------------
Objetivo:
- Ver status dos serviços e saúde do sistema.

Tarefas:
1) Backend - Endpoints:
   - GET /api/v1/admin/sistema/saude (status de todos os serviços)
     - PostgreSQL (conectado, latência)
     - Redis (conectado, memória usada)
     - ChromaDB (conectado, coleções)
     - Evolution API (conectado, instâncias ativas)
     - OpenAI (API key válida, últimas chamadas)
   - GET /api/v1/admin/sistema/metricas
     - Uso de CPU, memória, disco
     - Tempo de resposta médio (últimas 1000 requests)
     - Requests por minuto
     - Erros por minuto
2) Frontend:
   - Página "Sistema" com cards de status
   - Indicador verde/amarelo/vermelho por serviço
   - Gráficos de uso de recursos
   - Alertas se algo estiver fora do normal

Aceite:
- Dashboard mostra status de todos os serviços
- Alertas aparecem se serviço cair
- Métricas atualizam em tempo real
- Fácil identificar problemas


---------------------------------------------------------------------
MINI-FASE 16.14 — Gestão de Vendas e Assinaturas
---------------------------------------------------------------------
Objetivo:
- Ver todas as transações, assinaturas e gerenciar cobranças.

Tarefas:
1) Backend:
   - GET /api/v1/admin/vendas (todas as transações)
   - GET /api/v1/admin/assinaturas (todas as assinaturas)
   - GET /api/v1/admin/assinaturas/:id/cancelar (cancelar assinatura)
   - GET /api/v1/admin/assinaturas/:id/reativar
   - POST /api/v1/admin/vendas/:id/reembolsar
2) Frontend:
   - Página "Vendas" com tabela de transações
   - Filtros: status, data, valor, cliente
   - Página "Assinaturas" com lista
   - Ações: Cancelar, Reativar, Ver Histórico
   - Modal de confirmação para reembolso

Aceite:
- Lista todas as vendas e assinaturas
- Filtros funcionam
- Cancelar assinatura atualiza status
- Reembolso processa corretamente via Stripe


---------------------------------------------------------------------
MINI-FASE 16.15 — Histórico Completo do Cliente
---------------------------------------------------------------------
Objetivo:
- Ver tudo sobre um cliente em uma única página.

Tarefas:
1) Backend:
   - GET /api/v1/admin/clientes/:id/historico-completo
     - Dados cadastrais
     - Histórico de pagamentos
     - Conversas do WhatsApp (últimas 100)
     - Tickets abertos
     - Uso de OpenAI
     - Logins (últimos 30 dias)
     - Ações realizadas
2) Frontend:
   - Página "Detalhes do Cliente" com abas:
     - Visão Geral (resumo)
     - Pagamentos
     - Conversas
     - Tickets
     - Uso de Créditos
     - Atividade
   - Timeline de eventos
   - Gráficos de uso ao longo do tempo

Aceite:
- Página carrega todos os dados do cliente
- Abas funcionam corretamente
- Timeline mostra eventos em ordem cronológica
- Fácil entender comportamento do cliente


---------------------------------------------------------------------
MINI-FASE 16.16 — Responsividade Completa (Admin + Cliente)
---------------------------------------------------------------------
Objetivo:
- Garantir que admin e cliente funcionem perfeitamente em mobile.

Tarefas:
1) Frontend - Admin:
   - Sidebar colapsa em hamburger menu no mobile
   - Tabelas viram cards empilhados
   - Gráficos responsivos
   - Formulários adaptam layout
2) Frontend - Cliente:
   - Menu lateral vira bottom navigation
   - Chat de suporte vira fullscreen no mobile
   - Textarea de conhecimento adapta altura
   - QR Code centraliza e aumenta tamanho
3) Testar em:
   - Desktop (1920x1080)
   - Tablet (768x1024)
   - Mobile (375x667)

Aceite:
- Todas as páginas funcionam em mobile
- Nenhum elemento quebra layout
- Touch targets têm tamanho adequado (min 44px)
- Navegação intuitiva em todos os tamanhos


=====================================================================
FIM DA FASE 16 - PAINEL ADMIN COMPLETO
=====================================================================


---------------------------------------------------------------------
FASE 17 — Deploy Produção (VPS) + Backup + Monitoramento
---------------------------------------------------------------------
Objetivo:
- Colocar online 24/7 com segurança.

Tarefas:
1) VPS Ubuntu + Docker + Docker Compose.
2) Nginx reverse proxy + SSL.
3) DNS e domínio.
4) Backups automáticos Postgres (diário).
5) Monitoramento uptime (UptimeRobot ou similar).
6) Configurar variáveis de ambiente de produção.
7) Configurar SMTP real (SendGrid).
8) Configurar Stripe em modo produção.

Aceite:
- Sistema acessível pelo domínio.
- SSL ativo (HTTPS).
- Backups executando diariamente.
- Emails sendo enviados.
- Pagamentos funcionando em produção.
- Monitoramento ativo.


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
