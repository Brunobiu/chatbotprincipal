# FASE 12: Sistema de Confiança e Fallback Humano

## Visão Geral

Sistema que calcula a confiança das respostas da IA e aciona fallback para atendimento humano quando necessário.

## Funcionalidades

### 1. Cálculo de Confiança
- **Score de 0.0 a 1.0** baseado em:
  - Similaridade dos documentos (peso 50%)
  - Overlap de palavras-chave (peso 30%)
  - Tamanho da resposta (peso 20%)

### 2. Fallback Automático
- Acionado quando `confidence_score < threshold` (padrão: 0.6)
- Motivos:
  - `BAIXA_CONFIANCA`: Score abaixo do threshold
  - `SOLICITACAO_MANUAL`: Cliente pediu atendimento humano
  - `ERRO_SISTEMA`: Erro no processamento

### 3. Detecção de Solicitação Manual
Detecta 17 frases-chave como:
- "quero falar com humano"
- "preciso de atendente"
- "falar com pessoa"
- etc.

### 4. Notificação de Atendentes
- Email automático quando fallback é acionado
- Configurável por cliente via `notificar_email`

### 5. Timeout de 24h
- Job automático executa a cada 1 hora
- Retorna conversas ao modo automático após 24h sem resposta

## Configurações

### Threshold de Confiança
```python
# Padrão: 0.6 (60%)
# Ajustável por cliente via API
PUT /api/v1/config
{
  "threshold_confianca": 0.7  # Mais rigoroso
}
```

### Email de Notificação
```python
PUT /api/v1/config
{
  "notificar_email": "atendente@empresa.com"
}
```

## API Endpoints

### Listar Conversas Aguardando
```http
GET /api/v1/conversas/aguardando-humano?cliente_id=1
```

**Response:**
```json
[
  {
    "id": 1,
    "cliente_id": 1,
    "cliente_nome": "Empresa X",
    "numero_whatsapp": "5511999999999",
    "status": "aguardando_humano",
    "motivo_fallback": "baixa_confianca",
    "tempo_espera_minutos": 45,
    "ultima_mensagem": "Como faço para...",
    "created_at": "2026-02-07T20:00:00"
  }
]
```

### Assumir Conversa
```http
POST /api/v1/conversas/1/assumir?cliente_id=1
{
  "atendente_email": "joao@empresa.com"
}
```

### Histórico da Conversa
```http
GET /api/v1/conversas/1/historico?cliente_id=1
```

**Response:**
```json
[
  {
    "id": 1,
    "remetente": "5511999999999",
    "conteudo": "Como faço para...",
    "tipo": "recebida",
    "confidence_score": 0.45,
    "fallback_triggered": true,
    "created_at": "2026-02-07T20:00:00"
  }
]
```

## Banco de Dados

### Tabela: conversas
```sql
CREATE TABLE conversas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    numero_whatsapp VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- ativa, aguardando_humano, em_atendimento
    motivo_fallback VARCHAR(50),
    atendente_email VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Tabela: mensagens (campos adicionados)
```sql
ALTER TABLE mensagens ADD COLUMN confidence_score FLOAT;
ALTER TABLE mensagens ADD COLUMN fallback_triggered BOOLEAN DEFAULT FALSE;
ALTER TABLE mensagens ADD COLUMN conversa_id INTEGER REFERENCES conversas(id);
```

### Tabela: configuracoes_bot (campos adicionados)
```sql
ALTER TABLE configuracoes_bot ADD COLUMN threshold_confianca FLOAT DEFAULT 0.6;
ALTER TABLE configuracoes_bot ADD COLUMN notificar_email VARCHAR(255);
```

## Fluxo de Processamento

```
1. Mensagem recebida via webhook
   ↓
2. Verificar se conversa está aguardando humano
   ↓ (não)
3. Verificar se cliente solicitou humano
   ↓ (não)
4. Processar com IA (RAG + LLM)
   ↓
5. Calcular confidence_score
   ↓
6. Score < threshold?
   ↓ (sim)
7. Acionar fallback
   - Criar/atualizar conversa
   - Enviar mensagem_fallback
   - Notificar atendente via email
   ↓ (não)
8. Enviar resposta normalmente
   - Salvar mensagem com confidence_score
```

## Testes

### Testes Unitários
- ✅ ConfiancaService: 17 testes passando
- ✅ FallbackService: 5 testes implementados

### Testes Manuais
1. Enviar mensagem que gera baixa confiança
2. Enviar "quero falar com humano"
3. Verificar email de notificação
4. Assumir conversa via API
5. Simular timeout de 24h

## Monitoramento

### Logs Importantes
```
[CONFIANÇA] Score calculado: 0.45 (threshold: 0.6)
[CONFIANÇA] Baixa confiança (0.45) - acionando fallback
[CONFIANÇA] Cliente solicitou atendimento humano
[SCHEDULER] Iniciando verificação de timeout 24h
[SCHEDULER] 3 conversas retornaram ao modo automático
```

### Métricas Sugeridas
- Taxa de fallback por cliente
- Tempo médio de espera
- Taxa de conversão (fallback → atendimento)
- Distribuição de confidence_scores

## Próximos Passos

1. Implementar dashboard de métricas
2. Adicionar webhooks para notificações em tempo real
3. Integrar com sistemas de ticketing (Zendesk, Freshdesk)
4. Machine learning para ajuste automático de threshold
