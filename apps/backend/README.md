# Backend - WhatsApp AI Bot SaaS

Este é o backend do sistema de chatbot WhatsApp com IA.

## Estrutura

```
app/
├── main.py              # Entrypoint FastAPI
├── api/v1/              # Rotas da API (preparado para futuras rotas)
├── core/                # Configurações e utilitários core
│   └── config.py        # Variáveis de ambiente
├── db/                  # Banco de dados (models e migrations)
├── services/            # Regras de negócio
│   ├── conversations/   # Memória e buffer de mensagens
│   ├── llm/            # Chains e prompts LangChain
│   ├── rag/            # Vectorstore e embeddings
│   └── whatsapp/       # Integração Evolution API
└── workers/            # Tasks assíncronas (Celery - futuro)
```

## Endpoints

- `POST /webhook` - Recebe mensagens do WhatsApp via Evolution API
- `GET /health` - Health check

## Como usar

1. Copiar `.env.example` da raiz para `.env` e configurar
2. Rodar: `docker-compose -f infra/docker-compose.yml up --build`

## Funcionamento atual

O fluxo atual mantém a funcionalidade original:
1. Evolution API envia mensagens para `/webhook`
2. Buffer agrupa mensagens (debounce)
3. RAG processa com memória e documentos
4. Resposta enviada via Evolution API

## Próximas fases

- FASE 2: Infraestrutura multi-tenant (PostgreSQL, Redis)
- FASE 3: Frontend inicial
- FASE 4+: Checkout, dashboard, configurações, etc.
