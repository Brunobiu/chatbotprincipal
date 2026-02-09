# FASE F - ANALYTICS E RELATÓRIOS

**Prioridade:** 🔵 BAIXA  
**Tempo Estimado:** 4-6 horas  
**Status:** ⏳ Pendente

---

## 🎯 Objetivo

Implementar sistema de analytics avançado com relatórios detalhados, gráficos e exportação de dados.

---

## 📋 Funcionalidades

### F1: Dashboard de Analytics

**Nova aba lateral:** "Analytics"

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Analytics                                                │
├─────────────────────────────────────────────────────────────┤
│ Período: [Últimos 30 dias ▼] [01/01/2026] até [09/02/2026] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Resumo Geral                                               │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│ │ Clientes │ │ Conversas│ │ Mensagens│ │Taxa Conv.│      │
│ │    45    │ │   1.234  │ │  8.567   │ │   18%    │      │
│ │  +12%    │ │  +25%    │ │  +15%    │ │  -2%     │      │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│                                                             │
│ Crescimento de Clientes (últimos 6 meses)                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [Gráfico de linha: Clientes ao longo do tempo]         │ │
│ │ 50 ┤                                              ╭─    │ │
│ │ 40 ┤                                        ╭─────╯     │ │
│ │ 30 ┤                              ╭─────────╯           │ │
│ │ 20 ┤                    ╭─────────╯                     │ │
│ │ 10 ┤          ╭─────────╯                               │ │
│ │  0 ┼──────────┴──────────────────────────────────────   │ │
│ │    Set  Out  Nov  Dez  Jan  Fev                        │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Receita Mensal (MRR)                                       │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [Gráfico de barras: Receita por mês]                   │ │
│ │ R$ 5k ┤                                           ███   │ │
│ │ R$ 4k ┤                                     ███   ███   │ │
│ │ R$ 3k ┤                               ███   ███   ███   │ │
│ │ R$ 2k ┤                         ███   ███   ███   ███   │ │
│ │ R$ 1k ┤                   ███   ███   ███   ███   ███   │ │
│ │ R$ 0  ┼───────────────────────────────────────────────   │ │
│ │       Set  Out  Nov  Dez  Jan  Fev                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Distribuição de Planos                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [Gráfico de pizza: % por plano]                        │ │
│ │                                                          │ │
│ │         Mensal: 45% (20 clientes)                       │ │
│ │         Trimestral: 35% (16 clientes)                   │ │
│ │         Semestral: 20% (9 clientes)                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Taxa de Conversão (Trial → Pago)                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [Gráfico de linha: Taxa de conversão ao longo do tempo]│ │
│ │ 30% ┤                                                    │ │
│ │ 25% ┤     ╭───╮                                         │ │
│ │ 20% ┤ ╭───╯   ╰───╮     ╭───╮                          │ │
│ │ 15% ┤─╯           ╰─────╯   ╰───                        │ │
│ │ 10% ┤                                                    │ │
│ │  5% ┤                                                    │ │
│ │  0% ┼────────────────────────────────────────────────    │ │
│ │     Set  Out  Nov  Dez  Jan  Fev                       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Top 10 Clientes (por uso)                                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Cliente              | Mensagens | Conversas | Custo    │ │
│ │ ──────────────────────────────────────────────────────  │ │
│ │ João Silva           | 1.234     | 45        | R$ 52,00 │ │
│ │ Maria Costa          | 987       | 38        | R$ 45,00 │ │
│ │ Pedro Santos         | 856       | 32        | R$ 38,00 │ │
│ │ ...                  | ...       | ...       | ...      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│                      [Exportar Relatório PDF] [Exportar CSV]│
└─────────────────────────────────────────────────────────────┘
```

---

### F2: Métricas Disponíveis

**Clientes:**
- Total de clientes
- Clientes ativos (pagos)
- Clientes em trial
- Clientes cancelados
- Crescimento mensal
- Taxa de churn

**Conversas:**
- Total de conversas
- Conversas por cliente (média)
- Conversas por dia
- Conversas com fallback (%)
- Tempo médio de resposta

**Mensagens:**
- Total de mensagens
- Mensagens por conversa (média)
- Mensagens do bot vs humano
- Taxa de satisfação (se implementado)

**Financeiro:**
- MRR (Monthly Recurring Revenue)
- Receita total
- Ticket médio
- Custo OpenAI
- Lucro líquido
- Margem de lucro

**Conversão:**
- Taxa de conversão (trial → pago)
- Tempo médio até conversão
- Plano mais escolhido
- Cancelamentos por mês

---

### F3: Filtros e Períodos

**Períodos pré-definidos:**
- Últimos 7 dias
- Últimos 30 dias
- Últimos 3 meses
- Últimos 6 meses
- Último ano
- Personalizado (data início e fim)

**Filtros:**
- Por plano (mensal, trimestral, semestral)
- Por status (trial, ativo, cancelado)
- Por modelo de IA usado
- Por cliente específico

---

### F4: Exportação de Relatórios

**Formatos:**
- PDF (relatório completo com gráficos)
- CSV (dados brutos para análise)
- Excel (planilha formatada)

**Conteúdo do PDF:**
- Capa com logo e período
- Resumo executivo
- Todos os gráficos
- Tabelas de dados
- Insights e recomendações

---

## 🗄️ Alterações no Banco de Dados

### Nova Tabela: `metricas_diarias`

```sql
CREATE TABLE metricas_diarias (
    id SERIAL PRIMARY KEY,
    data DATE UNIQUE,
    total_clientes INTEGER DEFAULT 0,
    clientes_ativos INTEGER DEFAULT 0,
    clientes_trial INTEGER DEFAULT 0,
    clientes_cancelados INTEGER DEFAULT 0,
    novos_clientes INTEGER DEFAULT 0,
    conversoes INTEGER DEFAULT 0,
    cancelamentos INTEGER DEFAULT 0,
    total_conversas INTEGER DEFAULT 0,
    total_mensagens INTEGER DEFAULT 0,
    receita_dia DECIMAL(10,2) DEFAULT 0,
    custo_openai_dia DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_metricas_data ON metricas_diarias(data DESC);
```

### Views para facilitar queries:

```sql
-- View de crescimento mensal
CREATE VIEW crescimento_mensal AS
SELECT 
    DATE_TRUNC('month', data) as mes,
    MAX(total_clientes) as clientes_fim_mes,
    SUM(novos_clientes) as novos_mes,
    SUM(cancelamentos) as cancelamentos_mes,
    SUM(receita_dia) as receita_mes
FROM metricas_diarias
GROUP BY DATE_TRUNC('month', data)
ORDER BY mes DESC;

-- View de taxa de conversão
CREATE VIEW taxa_conversao AS
SELECT 
    DATE_TRUNC('month', data) as mes,
    SUM(conversoes) as total_conversoes,
    SUM(novos_clientes) as total_trials,
    CASE 
        WHEN SUM(novos_clientes) > 0 
        THEN (SUM(conversoes)::float / SUM(novos_clientes) * 100)
        ELSE 0 
    END as taxa_conversao_percent
FROM metricas_diarias
GROUP BY DATE_TRUNC('month', data)
ORDER BY mes DESC;
```

---

## 🔧 Implementação Técnica

### Backend

**1. Serviço de Analytics:**

**Arquivo:** `apps/backend/app/services/analytics_service.py`

```python
class AnalyticsService:
    async def calcular_metricas_diarias(self, data: date):
        """Calcula e salva métricas do dia"""
        # Total de clientes
        # Clientes ativos, trial, cancelados
        # Novos clientes do dia
        # Conversões do dia
        # Cancelamentos do dia
        # Total de conversas
        # Total de mensagens
        # Receita do dia
        # Custo OpenAI do dia
        
    async def get_resumo_geral(self, data_inicio: date, data_fim: date):
        """Retorna resumo geral do período"""
        # Somar métricas do período
        # Calcular crescimento
        # Calcular médias
        
    async def get_crescimento_clientes(self, meses: int = 6):
        """Retorna dados para gráfico de crescimento"""
        # Buscar últimos N meses
        # Retornar array de [mes, total_clientes]
        
    async def get_receita_mensal(self, meses: int = 6):
        """Retorna dados para gráfico de receita"""
        # Buscar últimos N meses
        # Retornar array de [mes, receita]
        
    async def get_distribuicao_planos(self):
        """Retorna distribuição de clientes por plano"""
        # Contar clientes por plano
        # Calcular percentuais
        
    async def get_taxa_conversao(self, meses: int = 6):
        """Retorna taxa de conversão ao longo do tempo"""
        # Usar view taxa_conversao
        
    async def get_top_clientes(self, limit: int = 10):
        """Retorna top clientes por uso"""
        # Ordenar por mensagens/conversas
        # Incluir custo OpenAI
        
    async def exportar_pdf(self, data_inicio: date, data_fim: date):
        """Gera relatório PDF"""
        # Usar biblioteca reportlab ou weasyprint
        # Incluir todos os gráficos
        # Retornar arquivo PDF
        
    async def exportar_csv(self, data_inicio: date, data_fim: date):
        """Gera arquivo CSV"""
        # Buscar dados brutos
        # Formatar como CSV
        # Retornar arquivo
```

**2. Cron Job para calcular métricas:**

```python
# Executar todo dia à meia-noite
@scheduler.scheduled_job('cron', hour=0, minute=0)
async def calcular_metricas_diarias():
    service = AnalyticsService()
    ontem = date.today() - timedelta(days=1)
    await service.calcular_metricas_diarias(ontem)
```

**3. Rotas da API:**

```
GET /api/v1/admin/analytics/resumo
Query: ?data_inicio=2026-01-01&data_fim=2026-02-09
Response: {
  "total_clientes": 45,
  "crescimento_clientes": 12,
  "total_conversas": 1234,
  "crescimento_conversas": 25,
  "total_mensagens": 8567,
  "crescimento_mensagens": 15,
  "taxa_conversao": 18
}

GET /api/v1/admin/analytics/crescimento-clientes
Query: ?meses=6
Response: {
  "labels": ["Set", "Out", "Nov", "Dez", "Jan", "Fev"],
  "data": [10, 15, 22, 30, 38, 45]
}

GET /api/v1/admin/analytics/receita-mensal
Query: ?meses=6
Response: {
  "labels": ["Set", "Out", "Nov", "Dez", "Jan", "Fev"],
  "data": [1470, 2205, 3234, 4410, 5586, 6615]
}

GET /api/v1/admin/analytics/distribuicao-planos
Response: {
  "labels": ["Mensal", "Trimestral", "Semestral"],
  "data": [20, 16, 9],
  "percentuais": [45, 35, 20]
}

GET /api/v1/admin/analytics/taxa-conversao
Query: ?meses=6
Response: {
  "labels": ["Set", "Out", "Nov", "Dez", "Jan", "Fev"],
  "data": [15, 22, 18, 25, 20, 18]
}

GET /api/v1/admin/analytics/top-clientes
Query: ?limit=10
Response: {
  "clientes": [
    {
      "nome": "João Silva",
      "mensagens": 1234,
      "conversas": 45,
      "custo": 52.00
    },
    ...
  ]
}

GET /api/v1/admin/analytics/exportar-pdf
Query: ?data_inicio=2026-01-01&data_fim=2026-02-09
Response: (arquivo PDF)

GET /api/v1/admin/analytics/exportar-csv
Query: ?data_inicio=2026-01-01&data_fim=2026-02-09
Response: (arquivo CSV)
```

---

### Frontend

**1. Página de Analytics:**

**Componente:** `apps/frontend/app/admin/analytics/page.tsx`

**Funcionalidades:**
- Filtros de período
- Cards de resumo
- Gráficos (Recharts)
- Tabela de top clientes
- Botões de exportação

**2. Componentes de Gráficos:**

**Componente:** `apps/frontend/components/admin/charts/LineChart.tsx`
- Gráfico de linha (crescimento, taxa de conversão)

**Componente:** `apps/frontend/components/admin/charts/BarChart.tsx`
- Gráfico de barras (receita mensal)

**Componente:** `apps/frontend/components/admin/charts/PieChart.tsx`
- Gráfico de pizza (distribuição de planos)

**3. Componente de Filtros:**

**Componente:** `apps/frontend/components/admin/AnalyticsFilters.tsx`

**Funcionalidades:**
- Dropdown de períodos pré-definidos
- Date pickers para período personalizado
- Filtros adicionais (plano, status)
- Botão "Aplicar Filtros"

---

## ✅ Checklist de Implementação

### Backend
- [ ] Criar tabela `metricas_diarias`
- [ ] Criar views `crescimento_mensal` e `taxa_conversao`
- [ ] Criar serviço `AnalyticsService`
- [ ] Implementar cálculo de métricas diárias
- [ ] Criar rota `GET /api/v1/admin/analytics/resumo`
- [ ] Criar rota `GET /api/v1/admin/analytics/crescimento-clientes`
- [ ] Criar rota `GET /api/v1/admin/analytics/receita-mensal`
- [ ] Criar rota `GET /api/v1/admin/analytics/distribuicao-planos`
- [ ] Criar rota `GET /api/v1/admin/analytics/taxa-conversao`
- [ ] Criar rota `GET /api/v1/admin/analytics/top-clientes`
- [ ] Criar rota `GET /api/v1/admin/analytics/exportar-pdf`
- [ ] Criar rota `GET /api/v1/admin/analytics/exportar-csv`
- [ ] Configurar cron job para métricas diárias
- [ ] Instalar biblioteca para PDF (reportlab ou weasyprint)

### Frontend
- [ ] Criar página `/admin/analytics`
- [ ] Criar componente `AnalyticsFilters`
- [ ] Criar componente `LineChart`
- [ ] Criar componente `BarChart`
- [ ] Criar componente `PieChart`
- [ ] Criar componente `TopClientesTable`
- [ ] Implementar filtros de período
- [ ] Implementar exportação PDF
- [ ] Implementar exportação CSV
- [ ] Adicionar link no menu lateral

### Testes
- [ ] Testar cálculo de métricas diárias
- [ ] Testar resumo geral
- [ ] Testar gráfico de crescimento
- [ ] Testar gráfico de receita
- [ ] Testar distribuição de planos
- [ ] Testar taxa de conversão
- [ ] Testar top clientes
- [ ] Testar exportação PDF
- [ ] Testar exportação CSV
- [ ] Testar filtros de período

---

## 🧪 Casos de Teste

### CT1: Cálculo de Métricas Diárias
1. Executar cron job
2. Verificar tabela `metricas_diarias`
3. **Esperado:** Registro criado com métricas do dia anterior

### CT2: Resumo Geral
1. Acessar página de analytics
2. Selecionar "Últimos 30 dias"
3. **Esperado:** Cards mostram métricas corretas

### CT3: Gráfico de Crescimento
1. Ver gráfico de crescimento de clientes
2. **Esperado:** Linha mostra evolução dos últimos 6 meses

### CT4: Distribuição de Planos
1. Ver gráfico de pizza
2. **Esperado:** Percentuais corretos por plano

### CT5: Top Clientes
1. Ver tabela de top 10 clientes
2. **Esperado:** Ordenado por mensagens, com custo correto

### CT6: Exportar PDF
1. Clicar "Exportar Relatório PDF"
2. **Esperado:** Download de PDF com todos os gráficos

### CT7: Exportar CSV
1. Clicar "Exportar CSV"
2. **Esperado:** Download de CSV com dados brutos

### CT8: Filtro Personalizado
1. Selecionar período personalizado (01/01 a 31/01)
2. **Esperado:** Métricas atualizadas para o período

---

## 📝 Notas Importantes

1. **Métricas diárias** - Calcular todo dia à meia-noite
2. **Performance** - Usar views e índices para queries rápidas
3. **Gráficos responsivos** - Usar Recharts com responsividade
4. **Exportação** - PDF deve incluir todos os gráficos
5. **Filtros** - Permitir análise de períodos específicos
6. **Cache** - Cachear métricas pesadas (1 hora)

---

## 🚀 Próximos Passos

Após completar FASE F:
- [ ] Marcar como completa no README.md
- [ ] Passar para FASE C (Treinar IA)

---

**Status:** ⏳ Aguardando implementação
