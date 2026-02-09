# Estrutura do Projeto - WhatsApp AI Bot SaaS

## 📁 Estrutura de Diretórios

```
chatbotprincipal/
├── .git/                          # Controle de versão Git
├── .kiro/                         # Documentação e configurações Kiro
│   ├── docs/                      # Documentação do projeto
│   ├── scripts/                   # Scripts utilitários
│   └── specs/                     # Especificações de fases
├── .vscode/                       # Configurações VS Code
├── apps/                          # Aplicações do projeto
│   ├── backend/                   # API FastAPI
│   └── frontend/                  # Interface Next.js
├── infra/                         # Infraestrutura (Docker, etc)
├── rag_files/                     # Arquivos processados para RAG
│   └── processed/                 # Arquivos já processados
├── vectorstore_data/              # Dados do ChromaDB (vetores)
├── .env                           # Variáveis de ambiente (NÃO COMMITAR)
├── .env.example                   # Exemplo de variáveis de ambiente
├── .gitignore                     # Arquivos ignorados pelo Git
├── arquiterura.md                 # Arquitetura completa do sistema
├── docker-compose.yml             # Orquestração de containers
└── README.md                      # Documentação principal
```

## 📂 Detalhamento das Pastas

### `/apps/backend` - API Backend (FastAPI)
```
backend/
├── app/
│   ├── api/                       # Endpoints da API
│   │   └── v1/                    # Versão 1 da API
│   │       ├── admin/             # Endpoints admin
│   │       ├── auth.py            # Autenticação cliente
│   │       ├── billing.py         # Pagamentos Stripe
│   │       ├── configuracoes.py   # Configurações bot
│   │       ├── conhecimento.py    # Base de conhecimento
│   │       ├── conversas.py       # Conversas WhatsApp
│   │       ├── tickets.py         # Sistema de tickets
│   │       └── whatsapp.py        # Integração WhatsApp
│   ├── core/                      # Configurações core
│   │   ├── config.py              # Configurações gerais
│   │   ├── middleware.py          # Middlewares
│   │   └── security.py            # Segurança e JWT
│   ├── db/                        # Banco de dados
│   │   ├── migrations/            # Migrações Alembic
│   │   ├── models/                # Modelos SQLAlchemy
│   │   ├── base.py                # Base declarativa
│   │   └── session.py             # Sessão do banco
│   ├── services/                  # Lógica de negócio
│   │   ├── admin/                 # Serviços admin
│   │   ├── ai/                    # Serviços IA (OpenAI)
│   │   ├── auth/                  # Autenticação
│   │   ├── avisos/                # Avisos e anúncios
│   │   ├── clientes/              # Gestão de clientes
│   │   ├── confianca/             # Sistema de confiança
│   │   ├── configuracoes/         # Configurações
│   │   ├── conhecimento/          # Base de conhecimento
│   │   ├── conversations/         # Conversas
│   │   ├── historico/             # Histórico completo
│   │   ├── notificacoes/          # Notificações
│   │   ├── relatorios/            # Relatórios
│   │   ├── seguranca/             # Segurança e auditoria
│   │   ├── sistema/               # Monitoramento sistema
│   │   ├── tickets/               # Tickets suporte
│   │   ├── tutoriais/             # Tutoriais
│   │   ├── uso/                   # Uso OpenAI
│   │   ├── vendas/                # Vendas e assinaturas
│   │   └── whatsapp/              # WhatsApp
│   ├── workers/                   # Workers background
│   │   └── scheduler.py           # Agendador de tarefas
│   ├── main.py                    # Entrada da aplicação
│   └── scripts/                   # Scripts utilitários
├── alembic.ini                    # Configuração Alembic
├── Dockerfile                     # Imagem Docker backend
├── entrypoint_fixed.sh            # Script de inicialização
└── requirements.txt               # Dependências Python
```

### `/apps/frontend` - Interface Web (Next.js 14)
```
frontend/
├── app/                           # App Router Next.js 14
│   ├── admin/                     # Painel Admin
│   │   ├── avisos/                # Gestão de avisos
│   │   ├── clientes/              # Gestão de clientes
│   │   │   └── [id]/              # Detalhes do cliente
│   │   │       └── historico/     # Histórico completo
│   │   ├── components/            # Componentes admin
│   │   ├── dashboard/             # Dashboard admin
│   │   ├── login/                 # Login admin
│   │   ├── notificacoes/          # Notificações
│   │   ├── relatorios/            # Relatórios
│   │   ├── seguranca/             # Segurança
│   │   ├── sistema/               # Monitoramento
│   │   ├── tickets/               # Tickets
│   │   ├── tutoriais/             # Tutoriais
│   │   ├── uso/                   # Uso OpenAI
│   │   ├── vendas/                # Vendas
│   │   └── layout.tsx             # Layout admin
│   ├── checkout/                  # Checkout Stripe
│   ├── dashboard/                 # Dashboard cliente
│   │   ├── configuracoes/         # Configurações bot
│   │   ├── conhecimento/          # Base conhecimento
│   │   ├── conversas/             # Conversas
│   │   ├── perfil/                # Perfil cliente
│   │   └── whatsapp/              # WhatsApp
│   ├── login/                     # Login cliente
│   ├── globals.css                # Estilos globais
│   ├── layout.tsx                 # Layout raiz
│   └── page.tsx                   # Página inicial
├── public/                        # Arquivos públicos
├── Dockerfile                     # Imagem Docker frontend
├── next.config.js                 # Configuração Next.js
├── package.json                   # Dependências Node
├── postcss.config.js              # PostCSS
├── tailwind.config.ts             # Tailwind CSS
└── tsconfig.json                  # TypeScript
```

### `/.kiro` - Documentação e Configurações
```
.kiro/
├── docs/                          # Documentação técnica
│   ├── ACESSO_LOGIN.md            # Credenciais de acesso
│   ├── COMANDOS_RAPIDOS.md        # Comandos úteis
│   ├── CORRECOES_APLICADAS.md     # Histórico de correções
│   ├── ESTRUTURA_PROJETO.md       # Este arquivo
│   ├── LEIA-ME-PRIMEIRO.md        # Guia inicial
│   ├── PROBLEMAS_WHATSAPP_SOLUCOES.md  # Soluções WhatsApp
│   └── STATUS_*.md                # Status de cada fase
├── scripts/                       # Scripts utilitários
│   ├── check_chromadb.py          # Verificar ChromaDB
│   ├── docker-helper.bat          # Helper Docker
│   ├── fix_passwords.sql          # Corrigir senhas
│   ├── force-clean-restart.bat    # Restart limpo
│   ├── restart-clean.bat          # Restart rápido
│   ├── resumo_conhecimento.py     # Resumir conhecimento
│   ├── run_test.sh                # Executar testes
│   ├── test_limpeza_texto.py      # Testar limpeza
│   └── test_openai.py             # Testar OpenAI
└── specs/                         # Especificações de fases
    ├── fase-12-confianca-fallback/
    └── fase-16-painel-admin/
```

## 🗄️ Banco de Dados (PostgreSQL)

### Tabelas Principais
- `clientes` - Clientes do SaaS
- `admins` - Administradores do sistema
- `instancias_whatsapp` - Instâncias WhatsApp
- `configuracoes_bot` - Configurações do bot
- `conhecimentos` - Base de conhecimento
- `conhecimentos_estruturados` - Conhecimento estruturado
- `conversas` - Conversas WhatsApp
- `mensagens` - Mensagens das conversas
- `tickets` - Tickets de suporte
- `ticket_mensagens` - Mensagens dos tickets
- `ticket_categorias` - Categorias de tickets
- `tutoriais` - Tutoriais do sistema
- `avisos` - Avisos e anúncios
- `uso_openai` - Rastreamento uso OpenAI
- `audit_log` - Log de auditoria
- `login_attempts` - Tentativas de login
- `ips_bloqueados` - IPs bloqueados
- `notificacoes_admin` - Notificações admin

## 🐳 Containers Docker

### Serviços Ativos
1. **postgres** - Banco de dados PostgreSQL 15
2. **redis** - Cache e sessões
3. **chromadb** - Banco vetorial para RAG
4. **evolution_api** - API WhatsApp
5. **bot** - Backend FastAPI (porta 8000)
6. **frontend** - Frontend Next.js (porta 3000)

## 🔑 Variáveis de Ambiente

Ver `.env.example` para lista completa. Principais:
- `DATABASE_URL` - Conexão PostgreSQL
- `REDIS_URL` - Conexão Redis
- `OPENAI_API_KEY` - Chave OpenAI
- `STRIPE_SECRET_KEY` - Chave Stripe
- `EVOLUTION_API_URL` - URL Evolution API
- `JWT_SECRET_KEY` - Chave JWT
- `ADMIN_JWT_SECRET_KEY` - Chave JWT Admin

## 📝 Arquivos Importantes na Raiz

- **arquiterura.md** - Documentação completa da arquitetura (MANTER)
- **docker-compose.yml** - Orquestração dos containers
- **README.md** - Documentação principal do projeto
- **.env** - Variáveis de ambiente (NÃO COMMITAR)
- **.env.example** - Exemplo de variáveis
- **.gitignore** - Arquivos ignorados pelo Git

## 🚀 Comandos Rápidos

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f bot
docker-compose logs -f frontend

# Rebuild específico
docker-compose build bot
docker-compose build frontend

# Restart específico
docker-compose restart bot
docker-compose restart frontend

# Parar tudo
docker-compose down

# Limpar tudo (cuidado!)
docker-compose down -v
```

## 📊 Status do Projeto

### Fases Completas
- ✅ FASE 1-11: Sistema base completo
- ✅ FASE 12: Sistema de confiança e fallback
- ✅ FASE 16: Painel admin completo (16.1 - 16.16)

### Próximas Fases
- ⏭️ FASE 17: Deploy produção + Backup + Monitoramento

## 🔗 URLs Importantes

- Frontend Cliente: http://localhost:3000
- Frontend Admin: http://localhost:3000/admin
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Evolution API: http://localhost:8080

## 👤 Credenciais de Acesso

Ver `.kiro/docs/ACESSO_LOGIN.md` para credenciais completas.

---

**Última atualização:** 08/02/2026
**Versão:** 1.0
