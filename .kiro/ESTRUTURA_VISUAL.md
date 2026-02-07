# 🗂️ ESTRUTURA VISUAL DO PROJETO

> Mapa visual de onde está cada coisa

---

## 📁 ESTRUTURA DE PASTAS

```
whatsapp_ai_bot/
│
├── 📄 LEIA-ME-PRIMEIRO.md          ← COMECE AQUI!
├── 📄 arquiterura.md                ← Visão geral das 16 fases
├── 📄 PROBLEMAS_WHATSAPP_SOLUCOES.md
│
├── 📁 .kiro/                        ← DOCUMENTAÇÃO CENTRAL
│   │
│   ├── 📄 INDEX.md                  ← ÍNDICE COMPLETO (leia!)
│   ├── 📄 RESUMO_EXECUTIVO.md       ← Resumo rápido
│   ├── 📄 ESTRUTURA_VISUAL.md       ← Este arquivo
│   │
│   ├── 📁 specs/                    ← ESPECIFICAÇÕES (planejamento)
│   │   │
│   │   ├── 📁 fase-12-confianca-fallback/  ✅ COMPLETO
│   │   │   ├── requirements.md      (6 requisitos)
│   │   │   ├── design.md            (arquitetura)
│   │   │   └── tasks.md             (60/60 tasks ✅)
│   │   │
│   │   └── 📁 fase-16-painel-admin/        🚧 EM ANDAMENTO
│   │       ├── requirements.md      (18 requisitos)
│   │       ├── design.md            (59 propriedades)
│   │       └── tasks.md             (5/79 tasks - 6.3%)
│   │
│   └── 📁 docs/                     ← DOCUMENTAÇÃO GERAL
│       ├── STATUS_ATUAL_07_02_2026.md
│       ├── PROGRESSO_FASES.md
│       ├── COMANDOS_RAPIDOS.md
│       ├── COMO_TESTAR_LOGIN.md
│       └── [40+ outros arquivos]
│
├── 📁 apps/
│   │
│   ├── 📁 backend/                  ← BACKEND (FastAPI)
│   │   │
│   │   ├── 📄 FASE_12_CONFIANCA_FALLBACK.md
│   │   ├── 📄 FASE_16_MINI_FASE_1_COMPLETA.md
│   │   │
│   │   ├── 📁 app/
│   │   │   ├── 📁 api/v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── billing.py
│   │   │   │   ├── configuracoes.py
│   │   │   │   ├── conhecimento.py
│   │   │   │   ├── conversas.py
│   │   │   │   ├── whatsapp.py
│   │   │   │   └── 📁 admin/
│   │   │   │       └── auth.py      ← Endpoints admin
│   │   │   │
│   │   │   ├── 📁 db/
│   │   │   │   ├── 📁 models/
│   │   │   │   │   ├── cliente.py
│   │   │   │   │   ├── conversa.py
│   │   │   │   │   ├── mensagem.py
│   │   │   │   │   ├── admin.py     ← Modelos admin
│   │   │   │   │   └── ...
│   │   │   │   │
│   │   │   │   └── 📁 migrations/versions/
│   │   │   │       ├── 001_initial.py
│   │   │   │       ├── 002_add_stripe_fields.py
│   │   │   │       ├── ...
│   │   │   │       ├── 009_add_config_fields.py
│   │   │   │       └── 010_add_admin_tables.py  ← Admin tables
│   │   │   │
│   │   │   ├── 📁 services/
│   │   │   │   ├── 📁 ai/
│   │   │   │   ├── 📁 auth/
│   │   │   │   ├── 📁 clientes/
│   │   │   │   ├── 📁 confianca/    ← FASE 12
│   │   │   │   ├── 📁 fallback/     ← FASE 12
│   │   │   │   ├── 📁 admin/        ← FASE 16
│   │   │   │   │   └── auth_service.py
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── 📁 workers/
│   │   │   │   └── scheduler.py     ← APScheduler (timeout 24h)
│   │   │   │
│   │   │   └── main.py
│   │   │
│   │   └── 📁 tests/
│   │       ├── test_confianca_service.py
│   │       ├── test_fallback_service.py
│   │       └── ...
│   │
│   └── 📁 frontend/                 ← FRONTEND (Next.js 14)
│       │
│       └── 📁 app/
│           │
│           ├── 📁 dashboard/        ← Painel Cliente
│           │   ├── page.tsx
│           │   ├── 📁 configuracoes/
│           │   ├── 📁 conhecimento/
│           │   ├── 📁 conversas/
│           │   ├── 📁 perfil/
│           │   └── 📁 whatsapp/
│           │
│           ├── 📁 admin/            ← Painel Admin (FASE 16)
│           │   ├── layout.tsx       ← Layout com sidebar
│           │   ├── 📁 login/
│           │   │   └── page.tsx     ← Login admin
│           │   └── 📁 dashboard/
│           │       └── page.tsx     ← Dashboard admin
│           │
│           ├── 📁 login/
│           └── page.tsx
│
├── 📁 infra/
│   └── docker-compose.yml
│
└── 📁 docs/                         ← Docs legados
    └── 📁 legacy/
```

---

## 🎯 ONDE ENCONTRAR CADA COISA

### 📋 Planejamento e Specs

| O que | Onde |
|-------|------|
| Spec FASE 12 (completo) | `.kiro/specs/fase-12-confianca-fallback/` |
| Spec FASE 16 (em andamento) | `.kiro/specs/fase-16-painel-admin/` |
| Arquitetura geral (16 fases) | `arquiterura.md` |

### 📚 Documentação

| O que | Onde |
|-------|------|
| Índice completo | `.kiro/INDEX.md` |
| Resumo executivo | `.kiro/RESUMO_EXECUTIVO.md` |
| Status atual | `.kiro/docs/STATUS_ATUAL_07_02_2026.md` |
| Progresso fases | `.kiro/docs/PROGRESSO_FASES.md` |
| Comandos úteis | `.kiro/docs/COMANDOS_RAPIDOS.md` |
| Doc FASE 12 | `apps/backend/FASE_12_CONFIANCA_FALLBACK.md` |
| Doc Mini-Fase 16.1 | `apps/backend/FASE_16_MINI_FASE_1_COMPLETA.md` |

### 💻 Código Backend

| O que | Onde |
|-------|------|
| Endpoints API | `apps/backend/app/api/v1/` |
| Endpoints Admin | `apps/backend/app/api/v1/admin/` |
| Modelos DB | `apps/backend/app/db/models/` |
| Migrations | `apps/backend/app/db/migrations/versions/` |
| Serviços | `apps/backend/app/services/` |
| Serviços Admin | `apps/backend/app/services/admin/` |
| Scheduler | `apps/backend/app/workers/scheduler.py` |
| Testes | `apps/backend/app/tests/` |

### 🎨 Código Frontend

| O que | Onde |
|-------|------|
| Painel Cliente | `apps/frontend/app/dashboard/` |
| Painel Admin | `apps/frontend/app/admin/` |
| Login Admin | `apps/frontend/app/admin/login/page.tsx` |
| Layout Admin | `apps/frontend/app/admin/layout.tsx` |
| Dashboard Admin | `apps/frontend/app/admin/dashboard/page.tsx` |

---

## 🔍 BUSCA RÁPIDA

### "Quero entender o projeto"
```
1. LEIA-ME-PRIMEIRO.md
2. .kiro/RESUMO_EXECUTIVO.md
3. .kiro/INDEX.md
```

### "Quero ver o que foi feito"
```
1. arquiterura.md (visão geral)
2. .kiro/docs/PROGRESSO_FASES.md
3. apps/backend/FASE_12_CONFIANCA_FALLBACK.md
4. apps/backend/FASE_16_MINI_FASE_1_COMPLETA.md
```

### "Quero continuar desenvolvendo"
```
1. .kiro/specs/fase-16-painel-admin/tasks.md
2. Procurar: "Mini-Fase 16.2"
3. Implementar tasks 6-9
```

### "Quero testar o sistema"
```
1. .kiro/docs/COMO_TESTAR_LOGIN.md
2. http://localhost:3001/admin/login
3. Login: brunobiuu / santana7996@
```

### "Tenho um problema"
```
1. PROBLEMAS_WHATSAPP_SOLUCOES.md
2. .kiro/docs/CORRECOES_APLICADAS.md
3. .kiro/docs/SOLUCAO_*.md
```

---

## 📊 FLUXO DE TRABALHO

```
┌─────────────────────────────────────────────────────────────┐
│                    INÍCIO DE NOVA SESSÃO                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ LEIA-ME-PRIMEIRO │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ RESUMO_EXECUTIVO │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │    INDEX.md      │
                    └──────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  JÁ SEI ONDE ESTÁ TUDO!                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Ver próxima     │
                    │  task no spec    │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Implementar     │
                    │  mini-fase       │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Testar          │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Commit          │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Atualizar docs  │
                    └──────────────────┘
```

---

## 🎨 LEGENDA DE ÍCONES

- 📄 Arquivo markdown
- 📁 Pasta/diretório
- ✅ Completo
- 🚧 Em andamento
- ⏳ Pendente
- 🎯 Próximo passo
- 📋 Planejamento
- 📚 Documentação
- 💻 Código
- 🎨 Frontend
- 🔧 Backend

---

## 📞 ATALHOS IMPORTANTES

```bash
# Documentação principal
.kiro/INDEX.md
.kiro/RESUMO_EXECUTIVO.md
LEIA-ME-PRIMEIRO.md

# Specs ativos
.kiro/specs/fase-12-confianca-fallback/
.kiro/specs/fase-16-painel-admin/

# Status e progresso
.kiro/docs/STATUS_ATUAL_07_02_2026.md
.kiro/docs/PROGRESSO_FASES.md

# Documentação de fases
apps/backend/FASE_12_CONFIANCA_FALLBACK.md
apps/backend/FASE_16_MINI_FASE_1_COMPLETA.md

# Código principal
apps/backend/app/main.py
apps/frontend/app/admin/layout.tsx
```

---

**Última Atualização**: 07/02/2026 23:00
