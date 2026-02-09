# FASE C - TREINAR IA COM CONVERSAS

**Prioridade:** 🔵 BAIXA  
**Tempo Estimado:** 6-8 horas  
**Status:** ⏳ Pendente

---

## 🎯 Objetivo

Permitir que o admin visualize todas as conversas de todos os clientes, marque conversas como "boas" ou "ruins", e use esses dados para melhorar as respostas do bot através de fine-tuning.

---

## 📋 Funcionalidades

### C1: Visualizar Todas as Conversas

**Nova aba lateral:** "Todas as Conversas"

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 💬 Todas as Conversas                                       │
├─────────────────────────────────────────────────────────────┤
│ Filtros:                                                    │
│ Cliente: [Todos ▼]  Status: [Todas ▼]  Avaliação: [Todas ▼]│
│ Buscar: [_______________________] 🔍                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 👤 João Silva - WhatsApp: +55 11 98765-4321            │ │
│ │ 📅 09/02/2026 14:30 | ⭐ Boa | 🤖 ChatGPT              │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ Cliente: Qual o horário de funcionamento?               │ │
│ │ Bot: Nosso horário é de segunda a sexta, das 9h às 18h.│ │
│ │ Cliente: Obrigado!                                      │ │
│ │                                                          │ │
│ │ [👍 Marcar como Boa] [👎 Marcar como Ruim] [Ver Mais]  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 👤 Maria Costa - WhatsApp: +55 11 91234-5678           │ │
│ │ 📅 09/02/2026 13:15 | ⚠️  Sem avaliação | 🤖 Claude    │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ Cliente: Vocês fazem entrega?                           │ │
│ │ Bot: Desculpe, não encontrei informações sobre isso.    │ │
│ │ Cliente: Ok                                             │ │
│ │                                                          │ │
│ │ [👍 Marcar como Boa] [👎 Marcar como Ruim] [Ver Mais]  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 👤 Pedro Santos - WhatsApp: +55 11 99876-5432          │ │
│ │ 📅 08/02/2026 16:45 | ❌ Ruim | 🤖 ChatGPT             │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ Cliente: Quanto custa o produto X?                      │ │
│ │ Bot: Não tenho essa informação no momento.              │ │
│ │ Cliente: Que chatbot ruim!                              │ │
│ │                                                          │ │
│ │ [👍 Marcar como Boa] [👎 Marcar como Ruim] [Ver Mais]  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│                                    [Carregar Mais]          │
└─────────────────────────────────────────────────────────────┘
```

**Funcionalidades:**
- Listar todas as conversas de todos os clientes
- Filtrar por cliente específico
- Filtrar por status (ativa, finalizada, aguardando)
- Filtrar por avaliação (boa, ruim, sem avaliação)
- Buscar por palavra-chave
- Paginação (20 conversas por página)
- Ver conversa completa (expandir)

---

### C2: Marcar Conversas

**Avaliações possíveis:**
- ⭐ **Boa** - Bot respondeu bem, cliente satisfeito
- ❌ **Ruim** - Bot respondeu mal, cliente insatisfeito
- ⚠️  **Sem avaliação** - Ainda não foi avaliada

**Comportamento:**
- Admin pode marcar/desmarcar a qualquer momento
- Marcação é salva no banco
- Contador mostra: "15 boas, 3 ruins, 82 sem avaliação"

---

### C3: Análise de Conversas

**Nova seção na página:** "Análise de Treinamento"

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Análise de Treinamento                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Resumo Geral                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Total de conversas: 100                                 │ │
│ │ Conversas boas: 15 (15%)                                │ │
│ │ Conversas ruins: 3 (3%)                                 │ │
│ │ Sem avaliação: 82 (82%)                                 │ │
│ │                                                          │ │
│ │ Recomendação: Avalie mais conversas para melhorar o     │ │
│ │ treinamento. Mínimo recomendado: 50 conversas.          │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Problemas Mais Comuns (conversas ruins)                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ • Bot não encontrou informação (2 vezes)                │ │
│ │ • Resposta genérica demais (1 vez)                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Tópicos Mais Bem Respondidos (conversas boas)              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ • Horário de funcionamento (5 vezes)                    │ │
│ │ • Formas de pagamento (4 vezes)                         │ │
│ │ • Localização (3 vezes)                                 │ │
│ │ • Produtos disponíveis (3 vezes)                        │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Fine-tuning                                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Status: ⚠️  Não iniciado                                │ │
│ │                                                          │ │
│ │ Conversas marcadas: 18                                  │ │
│ │ Mínimo necessário: 50                                   │ │
│ │ Progresso: ████░░░░░░░ 36%                              │ │
│ │                                                          │ │
│ │ [Iniciar Fine-tuning] (desabilitado)                    │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

### C4: Fine-tuning Automático

**Quando ativar:**
- Mínimo de 50 conversas marcadas (boas + ruins)
- Pelo menos 30 conversas boas
- Pelo menos 10 conversas ruins

**Processo:**
1. Admin clica "Iniciar Fine-tuning"
2. Sistema prepara dados no formato JSONL
3. Envia para OpenAI Fine-tuning API
4. Aguarda conclusão (pode levar horas)
5. Atualiza modelo usado pelo bot
6. Notifica admin quando concluído

**Formato dos dados (JSONL):**
```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "Qual o horário?"}, {"role": "assistant", "content": "Nosso horário é..."}]}
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "Fazem entrega?"}, {"role": "assistant", "content": "Sim, fazemos entrega..."}]}
```

**Observações:**
- Apenas conversas marcadas como "boas" são usadas
- Conversas "ruins" são analisadas mas não usadas no treinamento
- Fine-tuning é feito por cliente (cada cliente tem seu modelo)
- Custo do fine-tuning é do admin (OpenAI cobra por isso)

---

## 🗄️ Alterações no Banco de Dados

### Tabela `conversas` - Adicionar campos:

```sql
ALTER TABLE conversas ADD COLUMN avaliacao VARCHAR(10);
-- Valores: 'boa', 'ruim', NULL (sem avaliação)

ALTER TABLE conversas ADD COLUMN avaliado_em TIMESTAMP;
-- Data/hora da avaliação

ALTER TABLE conversas ADD COLUMN avaliado_por VARCHAR(50) DEFAULT 'admin';
-- Quem avaliou (sempre 'admin' por enquanto)
```

### Nova Tabela: `fine_tuning_jobs`

```sql
CREATE TABLE fine_tuning_jobs (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    openai_job_id VARCHAR(255),
    -- ID do job no OpenAI
    status VARCHAR(20),
    -- Valores: 'pending', 'running', 'succeeded', 'failed'
    conversas_usadas INTEGER,
    -- Quantidade de conversas usadas
    modelo_base VARCHAR(50),
    -- Modelo base usado (ex: 'gpt-3.5-turbo')
    modelo_fine_tuned VARCHAR(100),
    -- Modelo resultante (ex: 'ft:gpt-3.5-turbo:...')
    custo_estimado DECIMAL(10,2),
    -- Custo do fine-tuning
    erro TEXT,
    -- Mensagem de erro (se falhou)
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_fine_tuning_cliente ON fine_tuning_jobs(cliente_id);
CREATE INDEX idx_fine_tuning_status ON fine_tuning_jobs(status);
```

---

## 🔧 Implementação Técnica

### Backend

**1. Serviço de Treinamento:**

**Arquivo:** `apps/backend/app/services/treinamento_service.py`

```python
import openai
import json

class TreinamentoService:
    async def get_todas_conversas(
        self, 
        cliente_id: int = None,
        avaliacao: str = None,
        busca: str = None,
        page: int = 1,
        limit: int = 20
    ):
        """Lista todas as conversas com filtros"""
        # Buscar conversas
        # Aplicar filtros
        # Paginar
        
    async def marcar_conversa(self, conversa_id: int, avaliacao: str):
        """Marca conversa como boa ou ruim"""
        # Validar avaliacao ('boa' ou 'ruim')
        # Atualizar conversa
        # Registrar data e quem avaliou
        
    async def get_analise_treinamento(self):
        """Retorna análise das conversas marcadas"""
        # Contar total, boas, ruins
        # Identificar problemas comuns (conversas ruins)
        # Identificar tópicos bem respondidos (conversas boas)
        # Verificar se pode fazer fine-tuning
        
    async def preparar_dados_fine_tuning(self, cliente_id: int):
        """Prepara dados no formato JSONL"""
        # Buscar conversas boas do cliente
        # Formatar no padrão OpenAI
        # Gerar arquivo JSONL
        # Retornar caminho do arquivo
        
    async def iniciar_fine_tuning(self, cliente_id: int):
        """Inicia processo de fine-tuning"""
        # Verificar mínimo de conversas
        # Preparar dados
        # Upload para OpenAI
        # Criar job de fine-tuning
        # Salvar em fine_tuning_jobs
        # Retornar job_id
        
    async def verificar_status_fine_tuning(self, job_id: int):
        """Verifica status do job no OpenAI"""
        # Buscar job no banco
        # Consultar OpenAI
        # Atualizar status
        # Se concluído, atualizar modelo do cliente
        
    async def aplicar_modelo_fine_tuned(self, cliente_id: int, modelo: str):
        """Aplica modelo fine-tuned ao cliente"""
        # Atualizar configuração do cliente
        # Próximas conversas usarão novo modelo
```

**2. Rotas da API:**

```
GET /api/v1/admin/treinamento/conversas
Query: ?cliente_id=&avaliacao=&busca=&page=1&limit=20
Response: {
  "conversas": [...],
  "total": 100,
  "page": 1,
  "pages": 5
}

POST /api/v1/admin/treinamento/marcar
Body: {
  "conversa_id": 123,
  "avaliacao": "boa"
}
Response: {
  "success": true,
  "message": "Conversa marcada como boa"
}

GET /api/v1/admin/treinamento/analise
Response: {
  "total": 100,
  "boas": 15,
  "ruins": 3,
  "sem_avaliacao": 82,
  "pode_fine_tuning": false,
  "minimo_necessario": 50,
  "problemas_comuns": [...],
  "topicos_bem_respondidos": [...]
}

POST /api/v1/admin/treinamento/iniciar-fine-tuning
Body: {
  "cliente_id": 5
}
Response: {
  "success": true,
  "job_id": 123,
  "message": "Fine-tuning iniciado. Você será notificado quando concluir."
}

GET /api/v1/admin/treinamento/status-fine-tuning/:job_id
Response: {
  "status": "running",
  "progresso": 45,
  "tempo_estimado": "2 horas"
}

GET /api/v1/admin/treinamento/historico-fine-tuning
Response: {
  "jobs": [
    {
      "id": 123,
      "cliente": "João Silva",
      "status": "succeeded",
      "conversas_usadas": 52,
      "modelo": "ft:gpt-3.5-turbo:...",
      "custo": 15.00,
      "created_at": "2026-02-01T10:00:00",
      "completed_at": "2026-02-01T14:30:00"
    },
    ...
  ]
}
```

**3. Cron Job para verificar status:**

```python
# Executar a cada 30 minutos
@scheduler.scheduled_job('cron', minute='*/30')
async def verificar_fine_tuning_jobs():
    service = TreinamentoService()
    # Buscar jobs pendentes ou em execução
    jobs = await db.query(
        "SELECT * FROM fine_tuning_jobs WHERE status IN ('pending', 'running')"
    ).all()
    
    for job in jobs:
        await service.verificar_status_fine_tuning(job.id)
```

---

### Frontend

**1. Página de Todas as Conversas:**

**Componente:** `apps/frontend/app/admin/treinamento/page.tsx`

**Funcionalidades:**
- Listar conversas com paginação
- Filtros (cliente, avaliação, busca)
- Botões para marcar como boa/ruim
- Expandir conversa completa
- Seção de análise de treinamento

**2. Componente de Conversa:**

**Componente:** `apps/frontend/components/admin/ConversaCard.tsx`

**Props:**
```typescript
interface ConversaCardProps {
  conversa: {
    id: number;
    cliente_nome: string;
    whatsapp: string;
    data: string;
    avaliacao: 'boa' | 'ruim' | null;
    modelo_usado: string;
    mensagens: Array<{
      de: 'cliente' | 'bot';
      texto: string;
    }>;
  };
  onMarcar: (id: number, avaliacao: 'boa' | 'ruim') => void;
}
```

**3. Componente de Análise:**

**Componente:** `apps/frontend/components/admin/AnalisetreinamentoCard.tsx`

**Funcionalidades:**
- Mostrar resumo geral
- Mostrar problemas comuns
- Mostrar tópicos bem respondidos
- Barra de progresso para fine-tuning
- Botão "Iniciar Fine-tuning" (habilitado se atingir mínimo)

**4. Modal de Confirmação:**

**Componente:** `apps/frontend/components/admin/ConfirmFineTuningModal.tsx`

**Conteúdo:**
```
┌────────────────────────────────────────┐
│ ⚠️  Iniciar Fine-tuning?              │
├────────────────────────────────────────┤
│ Você está prestes a iniciar o         │
│ fine-tuning do modelo para o cliente  │
│ João Silva.                            │
│                                        │
│ Conversas usadas: 52                  │
│ Custo estimado: R$ 15,00              │
│ Tempo estimado: 2-4 horas             │
│                                        │
│ O processo não pode ser cancelado.    │
│                                        │
│ [Cancelar] [Sim, Iniciar]             │
└────────────────────────────────────────┘
```

**5. Página de Histórico:**

**Componente:** `apps/frontend/app/admin/treinamento/historico/page.tsx`

**Funcionalidades:**
- Listar todos os jobs de fine-tuning
- Mostrar status (pendente, em execução, concluído, falhou)
- Mostrar custo
- Filtrar por cliente
- Filtrar por status

---

## ✅ Checklist de Implementação

### Backend
- [ ] Adicionar campos `avaliacao`, `avaliado_em`, `avaliado_por` em `conversas`
- [ ] Criar tabela `fine_tuning_jobs`
- [ ] Criar serviço `TreinamentoService`
- [ ] Criar rota `GET /api/v1/admin/treinamento/conversas`
- [ ] Criar rota `POST /api/v1/admin/treinamento/marcar`
- [ ] Criar rota `GET /api/v1/admin/treinamento/analise`
- [ ] Criar rota `POST /api/v1/admin/treinamento/iniciar-fine-tuning`
- [ ] Criar rota `GET /api/v1/admin/treinamento/status-fine-tuning/:job_id`
- [ ] Criar rota `GET /api/v1/admin/treinamento/historico-fine-tuning`
- [ ] Implementar preparação de dados JSONL
- [ ] Implementar integração com OpenAI Fine-tuning API
- [ ] Configurar cron job para verificar status
- [ ] Implementar notificação quando fine-tuning concluir

### Frontend
- [ ] Criar página `/admin/treinamento`
- [ ] Criar página `/admin/treinamento/historico`
- [ ] Criar componente `ConversaCard`
- [ ] Criar componente `AnalisetreinamentoCard`
- [ ] Criar componente `ConfirmFineTuningModal`
- [ ] Implementar filtros de conversas
- [ ] Implementar marcação de conversas
- [ ] Implementar iniciar fine-tuning
- [ ] Implementar visualização de status
- [ ] Adicionar link no menu lateral

### Testes
- [ ] Testar listagem de conversas
- [ ] Testar filtros
- [ ] Testar marcação como boa
- [ ] Testar marcação como ruim
- [ ] Testar análise de treinamento
- [ ] Testar preparação de dados JSONL
- [ ] Testar iniciar fine-tuning
- [ ] Testar verificação de status
- [ ] Testar aplicação de modelo fine-tuned
- [ ] Testar histórico de jobs

---

## 🧪 Casos de Teste

### CT1: Listar Todas as Conversas
1. Acessar página de treinamento
2. Ver lista de conversas
3. **Esperado:** Todas as conversas de todos os clientes

### CT2: Marcar Conversa como Boa
1. Clicar "Marcar como Boa"
2. **Esperado:** Conversa marcada, ícone ⭐ aparece

### CT3: Filtrar por Avaliação
1. Selecionar filtro "Boas"
2. **Esperado:** Apenas conversas boas

### CT4: Análise de Treinamento
1. Ver seção de análise
2. **Esperado:** Resumo correto, problemas e tópicos identificados

### CT5: Iniciar Fine-tuning (Insuficiente)
1. Ter menos de 50 conversas marcadas
2. **Esperado:** Botão desabilitado, mensagem de mínimo necessário

### CT6: Iniciar Fine-tuning (Suficiente)
1. Ter 50+ conversas marcadas
2. Clicar "Iniciar Fine-tuning"
3. Confirmar
4. **Esperado:** Job criado, status "pending"

### CT7: Verificar Status
1. Aguardar cron job executar
2. Ver status atualizado
3. **Esperado:** Status muda para "running" ou "succeeded"

### CT8: Modelo Aplicado
1. Fine-tuning concluído
2. Cliente envia mensagem
3. **Esperado:** Resposta usa modelo fine-tuned

---

## 📝 Notas Importantes

1. **Mínimo de conversas** - 50 marcadas (30 boas, 10 ruins)
2. **Custo do fine-tuning** - Admin paga (OpenAI cobra)
3. **Tempo de processamento** - Pode levar 2-4 horas
4. **Modelo por cliente** - Cada cliente pode ter seu modelo
5. **Conversas boas** - Apenas essas são usadas no treinamento
6. **Conversas ruins** - Analisadas mas não usadas
7. **Notificação** - Admin é notificado quando concluir
8. **Não pode cancelar** - Processo não pode ser interrompido

---

## 🚀 Próximos Passos

Após completar FASE C:
- [ ] Marcar como completa no README.md
- [ ] Todas as fases concluídas! 🎉

---

**Status:** ⏳ Aguardando implementação
