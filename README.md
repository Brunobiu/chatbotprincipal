# 🤖 WhatsApp AI Bot SaaS

> Sistema SaaS multi-tenant de chatbot WhatsApp com Inteligência Artificial e RAG

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

---

## 📋 Sobre o Projeto

Sistema completo de **chatbot WhatsApp com IA** que permite criar e gerenciar múltiplos bots personalizados. Cada cliente pode ter seu próprio bot com base de conhecimento exclusiva, configurações personalizadas e integração total com WhatsApp.

### ✨ Principais Funcionalidades

- 🤖 **IA Avançada**: Integração com OpenAI GPT-4 para respostas inteligentes
- 📚 **RAG (Retrieval-Augmented Generation)**: Base de conhecimento personalizada por cliente
- 💬 **WhatsApp Integration**: Conexão via Evolution API
- 👥 **Multi-tenant**: Múltiplos clientes isolados
- 🎯 **Sistema de Confiança**: Fallback automático para atendimento humano
- 💳 **Pagamentos**: Integração com Stripe
- 📊 **Painel Admin**: Gestão completa de clientes e métricas
- 🔐 **Segurança**: Autenticação JWT, bcrypt, bloqueio de IP

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Painel Admin │  │Painel Cliente│  │    Landing   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                    REST API (HTTPS)
                          │
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │   Auth   │  │    IA    │  │   RAG    │  │ Stripe │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   PostgreSQL          Redis           ChromaDB
```

---

## 🚀 Tecnologias

### Backend
- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL** - Banco de dados relacional
- **Redis** - Cache e sessões
- **ChromaDB** - Banco vetorial para RAG
- **OpenAI API** - GPT-4 para IA
- **Evolution API** - Integração WhatsApp
- **Stripe** - Processamento de pagamentos
- **APScheduler** - Jobs agendados

### Frontend
- **Next.js 14** - Framework React com App Router
- **React 18** - Biblioteca UI
- **Tailwind CSS** - Estilização
- **TypeScript** - Tipagem estática

### DevOps
- **Docker & Docker Compose** - Containerização
- **Alembic** - Migrations de banco
- **Git** - Controle de versão

---

## 📦 Instalação

### Pré-requisitos

- Docker e Docker Compose instalados
- Conta OpenAI com API key
- Conta Stripe (para pagamentos)
- Evolution API configurada

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/Brunobiu/chatbotprincipal.git
cd chatbotprincipal
```

2. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
```

Edite o `.env` com suas credenciais:
- `OPENAI_API_KEY` - Sua chave da OpenAI
- `STRIPE_SECRET_KEY` - Chave secreta do Stripe
- `STRIPE_WEBHOOK_SECRET` - Secret do webhook Stripe
- `EVOLUTION_AUTHENTICATION_API_KEY` - API key da Evolution
- `JWT_SECRET_KEY` - Chave secreta para JWT

3. **Adicione documentos para RAG**
```bash
# Coloque seus documentos em:
rag_files/
```

4. **Suba os containers**
```bash
docker-compose up -d --build
```

5. **Acesse as aplicações**
- Frontend Cliente: http://localhost:3000
- Frontend Admin: http://localhost:3001/admin
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Evolution API: http://localhost:8080

6. **Configure o webhook no Evolution API**
```
URL: http://bot:8000/webhook
Evento: MESSAGES_UPSERT
```

---

## 🎯 Funcionalidades Implementadas

### ✅ FASE 1-11: Sistema Base
- Autenticação e cadastro
- Integração Stripe
- Integração WhatsApp (Evolution API)
- Sistema RAG com ChromaDB
- Configurações personalizadas por cliente
- Buffer de mensagens e memória

### ✅ FASE 12: Sistema de Confiança e Fallback
- Score de confiança da IA (0-1)
- Fallback automático para humano
- Detecção de solicitação manual
- Notificações por email
- Timeout de 24h com retorno automático

### ✅ FASE 16.1: Painel Admin - Login
- Autenticação admin com JWT
- Bloqueio de IP após tentativas falhadas
- Layout admin com sidebar
- Dashboard básico

### 🚧 FASE 16.2-16.16: Painel Admin (Em Desenvolvimento)
- Dashboard com métricas (MRR, clientes, conversões)
- Gestão completa de clientes
- Monitoramento de uso OpenAI
- Sistema de tickets de suporte
- Tutoriais em vídeo
- Relatórios PDF/Excel
- E muito mais...

---

## 📚 Documentação

Toda a documentação está organizada em `.kiro/`:

- **[INDEX.md](.kiro/INDEX.md)** - Índice completo do projeto
- **[RESUMO_EXECUTIVO.md](.kiro/RESUMO_EXECUTIVO.md)** - Resumo rápido
- **[COMO_RETOMAR.md](.kiro/COMO_RETOMAR.md)** - Guia para retomar o trabalho
- **[ESTRUTURA_VISUAL.md](.kiro/ESTRUTURA_VISUAL.md)** - Mapa de pastas

### Specs (Planejamento)
- `.kiro/specs/fase-12-confianca-fallback/` - Sistema de confiança (completo)
- `.kiro/specs/fase-16-painel-admin/` - Painel admin (em andamento)

---

## 🔐 Credenciais Padrão

### Admin Root
```
URL: http://localhost:3001/admin/login
Login: brunobiuu
Senha: santana7996@
```

### Clientes de Teste
```
teste@teste.com / 123456
teste1@teste.com / 123456
teste2@teste.com / 123456
```

---

## 🛠️ Comandos Úteis

### Docker
```bash
# Iniciar containers
docker-compose up -d

# Ver logs
docker logs bot --tail 50

# Reiniciar backend
docker restart bot

# Parar tudo
docker-compose down
```

### Migrations
```bash
# Rodar migrations
docker exec bot alembic upgrade head

# Criar nova migration
docker exec bot alembic revision --autogenerate -m "descrição"
```

### Criar Admin
```bash
docker exec bot python /app/apps/backend/criar_admin_inicial.py
```

---

## 📊 Status do Projeto

- **Fases Completas**: 13/16 (81%)
- **FASE 16**: 5/79 tasks (6.3%)
- **Última Atualização**: 07/02/2026
- **Branch Ativa**: fix/critical-issues

---

## 🤝 Contribuindo

Este é um projeto privado em desenvolvimento ativo. Para contribuir:

1. Leia a documentação em `.kiro/`
2. Siga o spec-driven development
3. Faça commits após cada mini-fase
4. Mantenha a documentação atualizada

---

## 📝 Licença

Projeto privado - Todos os direitos reservados

---

## 👨‍💻 Autor

**Bruno Biuu**

---

## 🔗 Links Úteis

- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Evolution API](https://doc.evolution-api.com/)
- [OpenAI API](https://platform.openai.com/docs)
- [Stripe Docs](https://stripe.com/docs)

---

**Última Atualização**: 07/02/2026 | **Versão**: 1.0.0
