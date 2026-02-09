# FASE B - IA ASSISTENTE DO ADMIN

**Prioridade:** ⭐ ALTA  
**Tempo Estimado:** 12-14 horas  
**Status:** ⏳ Pendente

---

## 🎯 Objetivo

Implementar assistente de IA no dashboard do admin que fornece resumos diários, análises financeiras, dicas de conversão e histórico de mensagens.

---

## 📋 Funcionalidades

### B1: Widget IA no Topo do Dashboard

**Localização:** Logo acima das estatísticas atuais do dashboard admin

**Layout:**
```
┌──────────────────────────────────────────────────────────────┐
│ 🤖 ASSISTENTE IA - Resumo de Hoje (09/02/2026)              │
├──────────────────────────────────────────────────────────────┤
│ 📊 NOVOS CLIENTES (2)                                        │
│   • João Silva - cadastrou às 10:30                         │
│   • Maria Costa - cadastrou às 14:15                        │
│                                                              │
│ ⚠️  TRIALS EXPIRANDO (3)                                     │
│   • Pedro Santos - expira em 1 dia                          │
│   • Ana Lima - expira em 2 dias                             │
│   • Carlos Souza - expira em 2 dias                         │
│                                                              │
│ ❌ CANCELAMENTOS (1)                                         │
│   • Lucas Oliveira - cancelou hoje às 09:00                 │
│                                                              │
│ 💡 DICAS DE IA                                               │
│   • Sua taxa de conversão está em 15% (média: 20%)          │
│   • Recomendação: Envie email para trials expirando         │
│   • 3 clientes não configuraram o bot ainda                 │
│                                                              │
│ 💰 ANÁLISE FINANCEIRA                                        │
│   • Receita mensal: R$ 2.970,00 (33 clientes pagos)        │
│   • Custo OpenAI: R$ 450,00 (15% da receita)               │
│   • Lucro líquido: R$ 2.520,00 (margem: 85%)               │
│   • ROI recomendado para anúncios: até R$ 890 (30%)        │
│                                                              │
│                                    [Ver Histórico Completo] │
└──────────────────────────────────────────────────────────────┘
```

**Atualização:**
- Atualiza automaticamente a cada 1 hora
- Botão "Atualizar Agora" (ícone de refresh)
- Mostra última atualização: "Atualizado há 15 minutos"

---

### B2: Histórico de Mensagens da IA

**Nova aba lateral:** "Mensagens da IA"

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 Histórico de Mensagens da IA                             │
├─────────────────────────────────────────────────────────────┤
│ Filtros: [Todas] [Novos Clientes] [Cancelamentos] [Dicas]  │
│ Buscar: [________________] 🔍                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📅 09/02/2026 - 09:00                                   │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ 📊 Novos clientes: João Silva, Maria Costa             │ │
│ │ ⚠️  3 trials expirando em 2 dias                        │ │
│ │ 💡 Dica: Taxa de conversão em 15%                       │ │
│ │ 💰 Receita: R$ 2.970 | Lucro: R$ 2.520 (85%)           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📅 08/02/2026 - 09:00                                   │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ 📊 Novos clientes: Pedro Alves                          │ │
│ │ ❌ Cancelamento: Lucas Oliveira                         │ │
│ │ 💡 Dica: 5 clientes sem configurar bot                  │ │
│ │ 💰 Receita: R$ 2.823 | Lucro: R$ 2.400 (85%)           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📅 07/02/2026 - 09:00                                   │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ 📊 Novos clientes: Ana Santos, Carlos Lima             │ │
│ │ ⚠️  2 trials expirando em 1 dia                         │ │
│ │ 💰 Receita: R$ 2.823 | Lucro: R$ 2.380 (84%)           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│                                    [Carregar Mais]          │
└─────────────────────────────────────────────────────────────┘
```

**Funcionalidades:**
- Listar todas as mensagens geradas pela IA
- Filtrar por tipo (novos clientes, cancelamentos, dicas, financeiro)
- Buscar por palavra-chave
- Paginação (20 mensagens por página)
- Exportar histórico (CSV, PDF)
- Ordenar por data (mais recente primeiro)

---

### B3: Configurações de Objetivos

**Nova aba lateral:** "Meus Objetivos"

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🎯 Meus Objetivos                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Meta Mensal de Clientes                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Objetivo: [10] clientes/mês                             │ │
│ │ Progresso: 7/10 (70%) ████████░░                        │ │
│ │ Faltam: 3 clientes para bater a meta!                   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Meta Mensal de Receita                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Objetivo: R$ [5.000,00]/mês                             │ │
│ │ Progresso: R$ 2.970/5.000 (59%) ██████░░░░              │ │
│ │ Faltam: R$ 2.030 para bater a meta!                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Limites de Custos                                          │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Máximo para anúncios: [30]% da receita                  │ │
│ │ Valor atual: R$ 890,00                                  │ │
│ │                                                          │ │
│ │ Máximo custo OpenAI: [20]% da receita                   │ │
│ │ Valor atual: R$ 450,00 (15%) ✅ Dentro do limite        │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Taxa de Conversão Esperada                                 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Objetivo: [20]%                                         │ │
│ │ Atual: 15% ⚠️  Abaixo da meta                           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│                                          [Salvar Objetivos] │
└─────────────────────────────────────────────────────────────┘
```

**Campos configuráveis:**
- Meta mensal de clientes (número)
- Meta mensal de receita (R$)
- % máxima para gastar com anúncios
- % máxima de custo OpenAI
- Taxa de conversão esperada (%)

**Alertas no Dashboard:**
- Se abaixo da meta: "⚠️ Você está 30% abaixo da meta de clientes"
- Se acima da meta: "🎉 Parabéns! Você bateu a meta de receita!"
- Se custo alto: "⚠️ Custo OpenAI está em 25% (limite: 20%)"

---

### B4: Análise Financeira Detalhada

**Nova aba lateral:** "Financeiro"

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 💰 Análise Financeira                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Resumo Mensal                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Receita Total (MRR): R$ 2.970,00                        │ │
│ │ Clientes Pagos: 33                                      │ │
│ │ Ticket Médio: R$ 90,00                                  │ │
│ │                                                          │ │
│ │ Custos:                                                  │ │
│ │   • OpenAI: R$ 450,00 (15%)                             │ │
│ │   • Infraestrutura: R$ 0,00 (estimado)                  │ │
│ │   • Total: R$ 450,00                                    │ │
│ │                                                          │ │
│ │ Lucro Líquido: R$ 2.520,00                              │ │
│ │ Margem: 85% ✅                                           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Custo por Cliente (OpenAI)                                 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Cliente                    | Custo Mensal | Status       │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ João Silva                 | R$ 45,00     | ⚠️  Alto     │ │
│ │ Maria Costa                | R$ 12,00     | ✅ Normal    │ │
│ │ Pedro Santos               | R$ 8,00      | ✅ Normal    │ │
│ │ Ana Lima                   | R$ 52,00     | 🔴 Muito Alto│ │
│ │ ...                        | ...          | ...          │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Recomendações da IA                                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 💡 Ana Lima está com custo muito alto (R$ 52/mês)       │ │
│ │    Recomendação: Verificar uso excessivo do bot         │ │
│ │                                                          │ │
│ │ 💡 Você pode investir até R$ 890 em anúncios (30%)      │ │
│ │    Atual: R$ 0 investido                                │ │
│ │                                                          │ │
│ │ 💡 Margem de lucro excelente (85%)                       │ │
│ │    Continue monitorando custos OpenAI                   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Gráfico de Evolução (últimos 6 meses)                      │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [Gráfico de linha: Receita vs Custos vs Lucro]         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│                                    [Exportar Relatório PDF] │
└─────────────────────────────────────────────────────────────┘
```

**Métricas:**
- Receita total (MRR)
- Clientes pagos
- Ticket médio
- Custos (OpenAI, infraestrutura)
- Lucro líquido
- Margem de lucro
- Custo por cliente
- Clientes com gasto alto (alerta)
- Recomendações de otimização
- Gráfico de evolução

---

## 🗄️ Alterações no Banco de Dados

### Nova Tabela: `ia_mensagens`

```sql
CREATE TABLE ia_mensagens (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50),
    -- Valores: 'resumo_diario', 'novo_cliente', 'cancelamento', 
    --          'trial_expirando', 'dica', 'financeiro'
    conteudo TEXT,
    dados_json JSONB,
    -- Armazena dados estruturados da mensagem
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ia_mensagens_tipo ON ia_mensagens(tipo);
CREATE INDEX idx_ia_mensagens_created_at ON ia_mensagens(created_at DESC);
```

### Nova Tabela: `admin_objetivos`

```sql
CREATE TABLE admin_objetivos (
    id SERIAL PRIMARY KEY,
    meta_clientes_mes INTEGER DEFAULT 10,
    meta_receita_mes DECIMAL(10,2) DEFAULT 5000.00,
    max_anuncios_percent INTEGER DEFAULT 30,
    max_openai_percent INTEGER DEFAULT 20,
    taxa_conversao_esperada INTEGER DEFAULT 20,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Inserir valores padrão
INSERT INTO admin_objetivos (id) VALUES (1);
```

### Nova Tabela: `uso_openai_cliente`

```sql
CREATE TABLE uso_openai_cliente (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    mes_referencia VARCHAR(7),
    -- Formato: '2026-02'
    tokens_usados INTEGER DEFAULT 0,
    custo_estimado DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(cliente_id, mes_referencia)
);

CREATE INDEX idx_uso_openai_mes ON uso_openai_cliente(mes_referencia);
```

---

## 🔧 Implementação Técnica

### Backend

**1. Serviço de IA Assistente:**

**Arquivo:** `apps/backend/app/services/ia_assistente.py`

```python
class IAAssistenteService:
    async def gerar_resumo_diario(self):
        """Gera resumo diário e salva no banco"""
        # Buscar novos clientes (hoje)
        # Buscar trials expirando (próximos 3 dias)
        # Buscar cancelamentos (hoje)
        # Calcular métricas financeiras
        # Gerar dicas baseadas em dados
        # Salvar em ia_mensagens
        
    async def calcular_metricas_financeiras(self):
        """Calcula receita, custos, lucro"""
        # MRR
        # Custo OpenAI total
        # Lucro líquido
        # Margem
        
    async def gerar_dicas(self):
        """Gera dicas baseadas em dados"""
        # Taxa de conversão
        # Clientes sem configurar bot
        # Trials expirando sem contato
        # Custos altos
        
    async def analisar_custo_por_cliente(self):
        """Analisa custo OpenAI por cliente"""
        # Buscar uso do mês atual
        # Identificar clientes com gasto alto
        # Gerar alertas
```

**2. Rotas da API:**

```
GET /api/v1/admin/ia/resumo-atual
Response: {
  "novos_clientes": [...],
  "trials_expirando": [...],
  "cancelamentos": [...],
  "dicas": [...],
  "financeiro": {...},
  "ultima_atualizacao": "2026-02-09T14:30:00"
}

GET /api/v1/admin/ia/historico
Query: ?tipo=&busca=&page=1&limit=20
Response: {
  "mensagens": [...],
  "total": 150,
  "page": 1,
  "pages": 8
}

GET /api/v1/admin/objetivos
Response: {
  "meta_clientes_mes": 10,
  "meta_receita_mes": 5000,
  ...
}

PUT /api/v1/admin/objetivos
Body: {
  "meta_clientes_mes": 15,
  "meta_receita_mes": 7000,
  ...
}

GET /api/v1/admin/financeiro/analise
Response: {
  "mrr": 2970,
  "clientes_pagos": 33,
  "ticket_medio": 90,
  "custos": {...},
  "lucro": 2520,
  "margem": 85,
  "custo_por_cliente": [...]
}

GET /api/v1/admin/financeiro/evolucao
Query: ?meses=6
Response: {
  "meses": ["2025-09", "2025-10", ...],
  "receita": [1500, 1800, ...],
  "custos": [200, 250, ...],
  "lucro": [1300, 1550, ...]
}
```

**3. Cron Job para gerar resumo diário:**

```python
# Executar todo dia às 09:00
@scheduler.scheduled_job('cron', hour=9, minute=0)
async def gerar_resumo_diario():
    service = IAAssistenteService()
    await service.gerar_resumo_diario()
```

---

### Frontend

**1. Widget IA no Dashboard:**

**Componente:** `apps/frontend/components/admin/IAWidget.tsx`

**Funcionalidades:**
- Buscar resumo atual via API
- Atualizar automaticamente a cada 1 hora
- Botão "Atualizar Agora"
- Link para "Ver Histórico Completo"

**2. Página de Histórico:**

**Componente:** `apps/frontend/app/admin/ia-mensagens/page.tsx`

**Funcionalidades:**
- Listar mensagens com paginação
- Filtros por tipo
- Busca por palavra-chave
- Exportar histórico

**3. Página de Objetivos:**

**Componente:** `apps/frontend/app/admin/objetivos/page.tsx`

**Funcionalidades:**
- Formulário de configuração
- Mostrar progresso em tempo real
- Alertas visuais

**4. Página de Análise Financeira:**

**Componente:** `apps/frontend/app/admin/financeiro/page.tsx`

**Funcionalidades:**
- Resumo mensal
- Tabela de custo por cliente
- Recomendações da IA
- Gráfico de evolução (Recharts)
- Exportar relatório PDF

---

## ✅ Checklist de Implementação

### Backend
- [ ] Criar tabela `ia_mensagens`
- [ ] Criar tabela `admin_objetivos`
- [ ] Criar tabela `uso_openai_cliente`
- [ ] Criar serviço `IAAssistenteService`
- [ ] Criar rota `GET /api/v1/admin/ia/resumo-atual`
- [ ] Criar rota `GET /api/v1/admin/ia/historico`
- [ ] Criar rota `GET /api/v1/admin/objetivos`
- [ ] Criar rota `PUT /api/v1/admin/objetivos`
- [ ] Criar rota `GET /api/v1/admin/financeiro/analise`
- [ ] Criar rota `GET /api/v1/admin/financeiro/evolucao`
- [ ] Configurar cron job para resumo diário
- [ ] Implementar rastreamento de uso OpenAI por cliente

### Frontend
- [ ] Criar componente `IAWidget`
- [ ] Criar página `/admin/ia-mensagens`
- [ ] Criar página `/admin/objetivos`
- [ ] Criar página `/admin/financeiro`
- [ ] Criar componente `ProgressBar`
- [ ] Criar componente `FinanceChart` (Recharts)
- [ ] Adicionar auto-refresh no widget (1 hora)
- [ ] Implementar exportação de histórico
- [ ] Implementar exportação de relatório PDF

### Testes
- [ ] Testar geração de resumo diário
- [ ] Testar cálculo de métricas financeiras
- [ ] Testar geração de dicas
- [ ] Testar histórico com filtros
- [ ] Testar configuração de objetivos
- [ ] Testar análise financeira
- [ ] Testar gráfico de evolução
- [ ] Testar alertas de custo alto

---

## 🧪 Casos de Teste

### CT1: Resumo Diário
1. Criar 2 novos clientes hoje
2. Criar 3 clientes com trial expirando em 2 dias
3. Cancelar 1 assinatura hoje
4. Executar cron job
5. **Esperado:** Resumo gerado com todos os dados

### CT2: Histórico de Mensagens
1. Gerar vários resumos diários
2. Acessar página de histórico
3. Filtrar por "Novos Clientes"
4. **Esperado:** Apenas mensagens de novos clientes

### CT3: Configurar Objetivos
1. Acessar página de objetivos
2. Definir meta de 15 clientes/mês
3. Salvar
4. **Esperado:** Dashboard mostra progresso atualizado

### CT4: Análise Financeira
1. Acessar página financeiro
2. Ver custo por cliente
3. **Esperado:** Clientes com gasto alto destacados

### CT5: Alerta de Custo Alto
1. Cliente usa muito OpenAI (>R$ 50/mês)
2. Gerar resumo diário
3. **Esperado:** Dica da IA alertando sobre custo alto

---

## 📝 Notas Importantes

1. **Resumo diário automático** - Executar todo dia às 09:00
2. **Histórico permanente** - Nunca deletar mensagens antigas
3. **Métricas em tempo real** - Calcular sempre que solicitado
4. **Alertas inteligentes** - IA deve identificar problemas
5. **Exportação** - Permitir exportar histórico e relatórios
6. **Performance** - Cachear métricas pesadas

---

## 🚀 Próximos Passos

Após completar FASE B:
- [ ] Marcar como completa no README.md
- [ ] Passar para FASE D (Gerenciar APIs)

---

**Status:** ⏳ Aguardando implementação
