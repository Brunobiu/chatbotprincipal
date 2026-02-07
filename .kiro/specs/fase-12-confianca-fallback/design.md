# FASE 12: Design - Sistema de Confiança e Fallback Humano

## 🏗️ Arquitetura

### Fluxo de Mensagem com Confiança

```
Cliente envia mensagem
    ↓
Webhook recebe
    ↓
RAG busca documentos
    ↓
LLM gera resposta
    ↓
ConfiancaService.calcular_confianca()
    ↓
Score < threshold? ──→ SIM ──→ FallbackService.acionar_fallback()
    ↓ NÃO                              ↓
Envia resposta                    Envia mensagem_fallback
    ↓                                  ↓
Salva com score                   Marca conversa "aguardando_humano"
                                       ↓
                                  Notifica humano
```

### Detecção de Solicitação Manual

```
Cliente envia mensagem
    ↓
ConfiancaService.detectar_solicitacao_humano()
    ↓
Contém palavras-chave? ──→ SIM ──→ FallbackService.acionar_fallback()
    ↓ NÃO
Continua fluxo normal
```

## 📊 Modelos de Dados

### Model: Conversa

```python
class StatusConversa(str, enum.Enum):
    ATIVA = "ativa"
    AGUARDANDO_HUMANO = "aguardando_humano"
    FINALIZADA = "finalizada"

class MotivoFallback(str, enum.Enum):
    BAIXA_CONFIANCA = "baixa_confianca"
    SOLICITACAO_MANUAL = "solicitacao_manual"

class Conversa(Base):
    __tablename__ = "conversas"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    numero_whatsapp = Column(String(20), nullable=False)
    status = Column(SQLEnum(StatusConversa), default=StatusConversa.ATIVA)
    motivo_fallback = Column(SQLEnum(MotivoFallback), nullable=True)
    ultima_mensagem_em = Column(DateTime, default=datetime.utcnow)
    assumida_por = Column(String(100), nullable=True)
    assumida_em = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="conversas")
    mensagens = relationship("Mensagem", back_populates="conversa")
```

### Atualização: Mensagem

```python
class Mensagem(Base):
    # ... campos existentes ...
    
    # Novos campos
    confidence_score = Column(Float, nullable=True)
    fallback_triggered = Column(Boolean, default=False)
    conversa_id = Column(Integer, ForeignKey("conversas.id"))
    
    # Relacionamento
    conversa = relationship("Conversa", back_populates="mensagens")
```

## 🧮 Cálculo de Confiança

### Algoritmo

```python
def calcular_confianca(
    query: str,
    documentos: List[Document],
    resposta: str
) -> float:
    """
    Calcula score de confiança baseado em múltiplos fatores
    
    Retorna: float entre 0.0 e 1.0
    """
    scores = []
    
    # 1. Similaridade média dos documentos (peso: 0.5)
    if documentos:
        similarity_scores = [doc.metadata.get('score', 0.5) for doc in documentos]
        avg_similarity = sum(similarity_scores) / len(similarity_scores)
        scores.append(('similarity', avg_similarity, 0.5))
    else:
        scores.append(('similarity', 0.0, 0.5))
    
    # 2. Presença de palavras-chave da query na resposta (peso: 0.3)
    query_words = set(query.lower().split())
    resposta_words = set(resposta.lower().split())
    keyword_overlap = len(query_words & resposta_words) / len(query_words) if query_words else 0
    scores.append(('keywords', keyword_overlap, 0.3))
    
    # 3. Tamanho da resposta (peso: 0.2)
    # Respostas muito curtas (<20 chars) ou muito longas (>500 chars) têm score menor
    resposta_len = len(resposta)
    if 20 <= resposta_len <= 500:
        length_score = 1.0
    elif resposta_len < 20:
        length_score = resposta_len / 20
    else:
        length_score = max(0.5, 1.0 - (resposta_len - 500) / 1000)
    scores.append(('length', length_score, 0.2))
    
    # Calcular score final ponderado
    final_score = sum(score * weight for _, score, weight in scores)
    
    return round(final_score, 2)
```

### Threshold

- **Padrão**: 0.6
- **Configurável** por cliente
- **Recomendações**:
  - 0.7-0.8: Conservador (mais fallbacks)
  - 0.5-0.6: Balanceado
  - 0.3-0.4: Agressivo (menos fallbacks)

## 🔍 Detecção de Solicitação Manual

### Palavras-chave Padrão

```python
PALAVRAS_CHAVE_HUMANO = [
    "falar com humano",
    "falar com atendente",
    "falar com pessoa",
    "atendente humano",
    "pessoa real",
    "quero falar com alguém",
    "preciso de ajuda humana",
    "transferir para humano",
    "não quero robô",
    "quero pessoa"
]
```

### Algoritmo

```python
def detectar_solicitacao_humano(mensagem: str) -> bool:
    """
    Detecta se cliente está solicitando atendimento humano
    """
    mensagem_lower = mensagem.lower()
    
    for palavra_chave in PALAVRAS_CHAVE_HUMANO:
        if palavra_chave in mensagem_lower:
            return True
    
    return False
```

## 📧 Notificação de Humano

### Opções

1. **Email** (implementar primeiro)
2. **Webhook** (futuro)
3. **Dashboard** (futuro)

### Template de Email

```html
Assunto: [WhatsApp Bot] Cliente aguardando atendimento

Olá,

Um cliente precisa de atendimento humano:

Cliente: {cliente_nome}
Número: {numero_whatsapp}
Motivo: {motivo_fallback}
Última mensagem: "{ultima_mensagem}"
Tempo de espera: {tempo_espera}

Acesse o dashboard para assumir a conversa:
{link_dashboard}/conversas/{conversa_id}

---
WhatsApp AI Bot
```

## 🔄 Job Agendado: Timeout 24h

### Implementação

```python
# Usar APScheduler ou Celery

@scheduler.scheduled_job('interval', hours=1)
def verificar_timeout_24h():
    """
    Verifica conversas aguardando humano há mais de 24h
    """
    db = SessionLocal()
    
    try:
        # Buscar conversas aguardando há mais de 24h
        limite = datetime.utcnow() - timedelta(hours=24)
        
        conversas = db.query(Conversa).filter(
            Conversa.status == StatusConversa.AGUARDANDO_HUMANO,
            Conversa.ultima_mensagem_em < limite,
            Conversa.assumida_por == None
        ).all()
        
        for conversa in conversas:
            # Enviar mensagem de retorno
            config = ConfiguracaoService.buscar_ou_criar(db, conversa.cliente_id)
            WhatsAppService.enviar_mensagem(
                conversa.numero_whatsapp,
                config.mensagem_retorno_24h
            )
            
            # Voltar para modo automático
            conversa.status = StatusConversa.ATIVA
            conversa.motivo_fallback = None
            db.commit()
            
            logger.info(f"Conversa {conversa.id} voltou para modo automático após 24h")
    
    finally:
        db.close()
```

## 🛣️ Endpoints API

### GET /api/v1/conversas/aguardando-humano

Lista conversas aguardando atendimento humano

**Response**:
```json
{
  "conversas": [
    {
      "id": 1,
      "numero_whatsapp": "5511999999999",
      "motivo_fallback": "baixa_confianca",
      "ultima_mensagem": "Como faço para...",
      "tempo_espera_minutos": 15,
      "created_at": "2026-02-07T19:00:00Z"
    }
  ],
  "total": 1
}
```

### POST /api/v1/conversas/{id}/assumir

Atendente assume uma conversa

**Request**:
```json
{
  "atendente_email": "atendente@empresa.com"
}
```

**Response**:
```json
{
  "message": "Conversa assumida com sucesso",
  "conversa_id": 1,
  "assumida_por": "atendente@empresa.com"
}
```

### GET /api/v1/conversas/{id}/historico

Busca histórico de mensagens da conversa

**Response**:
```json
{
  "conversa_id": 1,
  "numero_whatsapp": "5511999999999",
  "mensagens": [
    {
      "id": 1,
      "texto": "Olá",
      "de_cliente": true,
      "confidence_score": null,
      "created_at": "2026-02-07T19:00:00Z"
    },
    {
      "id": 2,
      "texto": "Olá! Como posso ajudar?",
      "de_cliente": false,
      "confidence_score": 0.85,
      "created_at": "2026-02-07T19:00:01Z"
    }
  ]
}
```

## 🧪 Testes

### Teste: Cálculo de Confiança

```python
def test_calcular_confianca_alta():
    query = "qual o horário de funcionamento"
    documentos = [
        Document(page_content="Horário: 9h às 18h", metadata={'score': 0.9})
    ]
    resposta = "Nosso horário de funcionamento é de 9h às 18h"
    
    score = ConfiancaService.calcular_confianca(query, documentos, resposta)
    
    assert score >= 0.7

def test_calcular_confianca_baixa():
    query = "qual o horário de funcionamento"
    documentos = []
    resposta = "Não sei"
    
    score = ConfiancaService.calcular_confianca(query, documentos, resposta)
    
    assert score < 0.5
```

### Teste: Detecção de Solicitação Manual

```python
def test_detectar_solicitacao_humano():
    assert ConfiancaService.detectar_solicitacao_humano("quero falar com humano")
    assert ConfiancaService.detectar_solicitacao_humano("preciso de um atendente")
    assert not ConfiancaService.detectar_solicitacao_humano("qual o horário?")
```

## 📈 Melhorias Futuras

1. **Machine Learning para Score**
   - Treinar modelo para prever confiança
   - Usar feedback de humanos

2. **Dashboard de Atendimento**
   - Interface web para atendentes
   - Chat em tempo real
   - Estatísticas de atendimento

3. **Roteamento Inteligente**
   - Distribuir conversas entre múltiplos atendentes
   - Priorizar por urgência

4. **Análise de Sentimento**
   - Detectar frustração do cliente
   - Acionar fallback preventivo

## 🔐 Segurança

- Apenas atendentes autorizados podem assumir conversas
- Logs de todas as ações de fallback
- Dados sensíveis não incluídos em notificações

## 📊 Monitoramento

- Taxa de fallback por cliente
- Tempo médio de resposta humana
- Taxa de conversão (automático → humano → resolvido)
- Score médio de confiança por cliente
