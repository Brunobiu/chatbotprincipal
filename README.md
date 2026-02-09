# 🤖 WhatsApp AI Bot SaaS - Multi-tenant

Sistema SaaS completo de chatbot WhatsApp com IA (OpenAI GPT-4), base de conhecimento RAG, sistema de confiança, fallback para humano e painel administrativo completo.

## 🎯 Visão Geral

Plataforma multi-tenant que permite clientes criarem e gerenciarem seus próprios chatbots WhatsApp com inteligência artificial, incluindo:

- 🤖 **IA Conversacional** - GPT-4 com contexto personalizado
- 📚 **Base de Conhecimento** - RAG com ChromaDB para respostas precisas
- 🎯 **Sistema de Confiança** - Fallback automático para humano quando necessário
- 💬 **WhatsApp Integration** - Via Evolution API
- 💳 **Pagamentos** - Stripe para assinaturas
- 👨‍💼 **Painel Admin** - Gestão completa de clientes, vendas, tickets, relatórios
- 📊 **Monitoramento** - Uso OpenAI, métricas, logs de auditoria
- 🎨 **Tema Dark/Light** - Interface moderna e responsiva

## 🏗️ Arquitetura

### Stack Tecnológico

**Backend:**
- FastAPI (Python 3.13)
- PostgreSQL 15
- Redis
- ChromaDB (vetores)
- OpenAI GPT-4
- Stripe API
- Evolution API (WhatsApp)

**Frontend:**
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Recharts (gráficos)

**Infraestrutura:**
- Docker & Docker Compose
- Nginx (futuro)
- Alembic (migrações)

## 🚀 Quick Start

### Pré-requisitos

- Docker Desktop instalado
- Git
- Chaves de API:
  - OpenAI API Key
  - Stripe Secret Key
  - Evolution API configurada

### Instalação

1. **Clone o repositório**
```bash
git clone <repo-url>
cd chatbotprincipal
```

2. **Configure variáveis de ambiente**
```bash
cp .env.example .env
# Edite .env com suas chaves de API
```

3. **Inicie os containers**
```bash
docker-compose up -d
```

4. **Aguarde inicialização** (30-60 segundos)

5. **Acesse as aplicações**
- Frontend Cliente: http://localhost:3000
- Painel Admin: http://localhost:3000/admin
- API Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Credenciais Padrão

**Admin:**
- Email: `brunobiuu`
- Senha: `admin123`

**Cliente Teste:**
- Email: `teste@teste.com`
- Senha: `teste123`

> ⚠️ **Importante:** Altere as credenciais em produção!

## 📁 Estrutura do Projeto

```
chatbotprincipal/
├── apps/
│   ├── backend/          # API FastAPI
│   └── frontend/         # Interface Next.js
├── .kiro/
│   ├── docs/             # Documentação técnica
│   ├── scripts/          # Scripts utilitários
│   └── specs/            # Especificações de fases
├── infra/                # Infraestrutura
├── rag_files/            # Arquivos RAG processados
├── vectorstore_data/     # Dados ChromaDB
├── arquiterura.md        # Arquitetura completa
├── docker-compose.yml    # Orquestração containers
└── README.md             # Este arquivo
```

Ver `.kiro/docs/ESTRUTURA_PROJETO.md` para detalhes completos.

## 🎓 Funcionalidades

### Para Clientes (SaaS)
- ✅ Cadastro e login
- ✅ Configuração do bot (tom, saudação, fallback)
- ✅ Base de conhecimento (upload de textos)
- ✅ Integração WhatsApp (QR Code)
- ✅ Visualização de conversas
- ✅ Sistema de tickets
- ✅ Perfil e configurações
- ✅ Tema dark/light

### Para Administradores
- ✅ Dashboard com métricas (MRR, clientes, conversões)
- ✅ Gestão completa de clientes (CRUD, suspender, resetar senha)
- ✅ Monitoramento de uso OpenAI (tokens, custos)
- ✅ Sistema de tickets com IA
- ✅ Gestão de tutoriais em vídeo
- ✅ Avisos e anúncios
- ✅ Relatórios avançados (Excel, PDF)
- ✅ Segurança e auditoria (logs, IPs bloqueados)
- ✅ Notificações em tempo real
- ✅ Acesso à própria ferramenta
- ✅ Gestão de vendas e assinaturas Stripe
- ✅ Histórico completo do cliente
- ✅ Monitoramento de sistema (saúde dos serviços)
- ✅ Interface responsiva (mobile-friendly)

### Sistema de IA
- ✅ GPT-4 com contexto personalizado
- ✅ RAG com ChromaDB para respostas precisas
- ✅ Sistema de confiança (0-100%)
- ✅ Fallback automático para humano
- ✅ Memória de conversação
- ✅ Estruturação automática de conhecimento

## 🔧 Comandos Úteis

### Docker
```bash
# Ver logs
docker-compose logs -f bot
docker-compose logs -f frontend

# Rebuild
docker-compose build bot
docker-compose build frontend

# Restart
docker-compose restart bot
docker-compose restart frontend

# Parar tudo
docker-compose down

# Limpar volumes (cuidado!)
docker-compose down -v
```

### Banco de Dados
```bash
# Acessar PostgreSQL
docker exec -it postgres psql -U postgres -d chatbot_db

# Criar migração
docker exec bot alembic revision --autogenerate -m "descrição"

# Aplicar migrações
docker exec bot alembic upgrade head
```

### Scripts Úteis
```bash
# Verificar ChromaDB
python .kiro/scripts/check_chromadb.py

# Testar OpenAI
python .kiro/scripts/test_openai.py

# Restart limpo (Windows)
.kiro/scripts/restart-clean.bat
```

## 📊 Status do Projeto

### ✅ Fases Completas

- **FASE 1-11:** Sistema base completo
  - Autenticação, cadastro, pagamentos
  - WhatsApp integration
  - Base de conhecimento RAG
  - Dashboard cliente

- **FASE 12:** Sistema de Confiança e Fallback
  - Score de confiança 0-100%
  - Fallback automático para humano
  - Gestão de conversas aguardando

- **FASE 16:** Painel Admin Completo (16.1 - 16.16)
  - Login e autenticação admin
  - Dashboard com métricas
  - Gestão de clientes
  - Monitoramento de uso
  - Sistema de tickets
  - Tutoriais e avisos
  - Relatórios avançados
  - Segurança e auditoria
  - Notificações
  - Tema dark/light
  - Monitoramento de sistema
  - Gestão de vendas
  - Histórico completo do cliente
  - Responsividade mobile

- **NOVAS FUNCIONALIDADES (09/02/2026):** 6 Fases Completas
  - **FASE A:** Sistema de Trial Gratuito (7 dias sem cartão)
  - **FASE E:** Billing com 3 Planos (Mensal R$147, Trimestral R$127, Semestral R$97)
  - **FASE B:** IA Assistente para Admin (resumos diários, dicas, análise financeira)
  - **FASE D:** Gerenciamento de APIs (5 provedores: OpenAI, Claude, Gemini, Grok, Ollama)
  - **FASE F:** Analytics e Relatórios (métricas diárias, gráficos, distribuição)
  - **FASE C:** Treinamento de IA (marcar conversas, análise, fine-tuning)

### ⏭️ Próximas Fases

- **FASE 17:** Deploy Produção
  - VPS Ubuntu + Docker
  - Nginx reverse proxy + SSL
  - DNS e domínio
  - Backups automáticos
  - Monitoramento uptime
  - SMTP real (SendGrid)

## 📚 Documentação

- **Arquitetura Completa:** `arquiterura.md`
- **Estrutura do Projeto:** `.kiro/docs/ESTRUTURA_PROJETO.md`
- **Comandos Rápidos:** `.kiro/docs/COMANDOS_RAPIDOS.md`
- **Credenciais de Acesso:** `.kiro/docs/ACESSO_LOGIN.md`
- **Problemas e Soluções:** `.kiro/docs/PROBLEMAS_WHATSAPP_SOLUCOES.md`

## 🐛 Troubleshooting

### Backend não inicia
```bash
docker-compose logs bot
docker-compose restart bot
```

### Frontend não carrega
```bash
docker-compose logs frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Erro de conexão com banco
```bash
docker-compose restart postgres
docker-compose restart bot
```

### ChromaDB não funciona
```bash
docker-compose restart chromadb
python .kiro/scripts/check_chromadb.py
```

Ver mais soluções em `.kiro/docs/`

## 🤝 Contribuindo

Este é um projeto privado. Para contribuir:

1. Crie uma branch para sua feature
2. Faça commit das mudanças
3. Abra um Pull Request

## 📝 Licença

Propriedade privada. Todos os direitos reservados.

## 👨‍💻 Autor

Bruno - WhatsApp AI Bot SaaS

---

**Versão:** 2.0  
**Última atualização:** 09/02/2026  
**Status:** ✅ 6 Novas Funcionalidades Completas - Pronto para Deploy
