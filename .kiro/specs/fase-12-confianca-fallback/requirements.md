# FASE 12: Sistema de Confiança e Fallback Humano

## 📋 Visão Geral

Implementar sistema de confiança nas respostas da IA e fallback para atendimento humano quando a confiança for baixa ou quando o cliente solicitar.

## 🎯 Objetivos

1. Calcular score de confiança para cada resposta da IA
2. Implementar fallback automático quando confiança < threshold
3. Permitir cliente solicitar atendimento humano a qualquer momento
4. Notificar humano quando fallback for acionado
5. Gerenciar fila de atendimento humano

## 📝 User Stories

### US 12.1: Score de Confiança
**Como** sistema  
**Quero** calcular um score de confiança para cada resposta da IA  
**Para** saber quando a resposta é confiável ou não

**Critérios de Aceitação**:
- Score entre 0.0 e 1.0
- Baseado em:
  - Similaridade dos documentos recuperados (RAG)
  - Presença de palavras-chave relevantes
  - Tamanho da resposta gerada
- Score salvo junto com a mensagem no banco

### US 12.2: Fallback Automático
**Como** sistema  
**Quero** acionar fallback humano automaticamente quando confiança < 0.6  
**Para** evitar respostas incorretas ou insatisfatórias

**Critérios de Aceitação**:
- Threshold configurável (padrão: 0.6)
- Envia mensagem de fallback configurada
- Marca conversa como "aguardando_humano"
- Não envia mais respostas automáticas até humano assumir

### US 12.3: Solicitação Manual de Humano
**Como** cliente  
**Quero** poder solicitar atendimento humano a qualquer momento  
**Para** falar com uma pessoa real quando necessário

**Critérios de Aceitação**:
- Palavras-chave detectadas: "falar com humano", "atendente", "pessoa real"
- Envia mensagem de fallback
- Marca conversa como "aguardando_humano"
- Funciona mesmo com alta confiança

### US 12.4: Notificação de Fallback
**Como** atendente humano  
**Quero** ser notificado quando um cliente precisar de atendimento  
**Para** poder assumir a conversa rapidamente

**Critérios de Aceitação**:
- Webhook ou email para notificar humano
- Informações incluídas:
  - Nome do cliente
  - Última mensagem
  - Motivo do fallback (baixa confiança / solicitação manual)
  - Link para assumir conversa

### US 12.5: Fila de Atendimento
**Como** sistema  
**Quero** gerenciar uma fila de conversas aguardando humano  
**Para** organizar o atendimento

**Critérios de Aceitação**:
- Lista de conversas em "aguardando_humano"
- Ordenadas por tempo de espera
- Mostra motivo do fallback
- Permite humano "assumir" conversa

### US 12.6: Retorno Automático após 24h
**Como** sistema  
**Quero** enviar mensagem de retorno após 24h sem resposta humana  
**Para** não deixar cliente sem resposta

**Critérios de Aceitação**:
- Após 24h em "aguardando_humano" sem resposta
- Envia mensagem configurada (mensagem_retorno_24h)
- Volta para modo automático
- Registra evento no histórico

## 🔧 Requisitos Técnicos

### Banco de Dados

**Nova tabela: `conversas`**
```sql
CREATE TABLE conversas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    numero_whatsapp VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'ativa', -- ativa, aguardando_humano, finalizada
    motivo_fallback VARCHAR(50), -- baixa_confianca, solicitacao_manual
    ultima_mensagem_em TIMESTAMP,
    assumida_por VARCHAR(100), -- email do atendente
    assumida_em TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Atualizar tabela: `mensagens`**
```sql
ALTER TABLE mensagens ADD COLUMN confidence_score DECIMAL(3,2);
ALTER TABLE mensagens ADD COLUMN fallback_triggered BOOLEAN DEFAULT FALSE;
```

### Serviços

**`ConfiancaService`**:
- `calcular_confianca(query, documentos, resposta) -> float`
- `deve_acionar_fallback(score, threshold) -> bool`
- `detectar_solicitacao_humano(mensagem) -> bool`

**`FallbackService`**:
- `acionar_fallback(conversa_id, motivo)`
- `notificar_humano(conversa_id)`
- `assumir_conversa(conversa_id, atendente_email)`
- `verificar_timeout_24h()` (job agendado)

### Configurações

Adicionar em `ConfiguracaoBot`:
- `threshold_confianca` (padrão: 0.6)
- `palavras_chave_humano` (lista de palavras)
- `notificar_email` (email do atendente)

## 📊 Métricas

- Taxa de fallback (% de conversas que acionaram fallback)
- Tempo médio de espera por humano
- Taxa de resolução automática vs humana
- Score médio de confiança

## 🧪 Testes

### Testes Unitários
- Cálculo de score de confiança
- Detecção de palavras-chave
- Lógica de threshold

### Testes de Integração
- Fluxo completo de fallback
- Notificação de humano
- Retorno automático após 24h

### Testes Manuais
- Enviar mensagem com baixa confiança
- Solicitar "falar com humano"
- Verificar notificação
- Assumir conversa
- Aguardar 24h (simular)

## 📚 Referências

- LangChain: Confidence Scoring
- RAG: Retrieval Quality Metrics
- WhatsApp Business: Best Practices for Handoff

## 🚀 Entregáveis

1. Migrations do banco de dados
2. Models: Conversa, atualização em Mensagem
3. Services: ConfiancaService, FallbackService
4. Endpoints API:
   - GET /api/v1/conversas/aguardando-humano
   - POST /api/v1/conversas/{id}/assumir
   - GET /api/v1/conversas/{id}/historico
5. Job agendado: verificar timeout 24h
6. Testes unitários e de integração
7. Documentação de uso

## ⏱️ Estimativa

- Desenvolvimento: 6-8 horas
- Testes: 2-3 horas
- Total: 8-11 horas
