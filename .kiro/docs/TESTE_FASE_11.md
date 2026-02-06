# 🧪 GUIA DE TESTE - FASE 11: Pipeline IA Completo

## 📋 Pré-requisitos

Antes de começar, verifique se tudo está rodando:

```bash
docker-compose ps
```

Deve mostrar:
- ✅ bot (backend) - rodando
- ✅ postgres - rodando
- ✅ redis - rodando
- ✅ chromadb - rodando
- ✅ evolution-api - rodando

---

## 🎯 O QUE VAMOS TESTAR

A FASE 11 conecta TUDO:
1. WhatsApp recebe mensagem
2. Sistema busca contexto no conhecimento (RAG)
3. Usa histórico da conversa (memória)
4. Chama OpenAI com prompt personalizado
5. Responde no WhatsApp

---

## 📝 PASSO A PASSO DO TESTE

### PASSO 1: Verificar se você tem um cliente ativo

```bash
# Entrar no container do backend
docker exec -it bot bash

# Dentro do container
cd /app/apps/backend
python3

# No Python
from app.db.session import SessionLocal
from app.db.models.cliente import Cliente

db = SessionLocal()
clientes = db.query(Cliente).all()
for c in clientes:
    print(f"ID: {c.id} | Email: {c.email} | Status: {c.status}")
db.close()
exit()
```

**Anote o ID do cliente** (exemplo: ID=1)

Se não tiver cliente, crie um:
```bash
python3 criar_usuario_teste.py
```

---

### PASSO 2: Fazer login no dashboard

1. Abrir: http://localhost:3001/login
2. Fazer login com o email/senha do cliente
3. Deve entrar no dashboard

---

### PASSO 3: Cadastrar conhecimento

1. Ir em: **Meu Conhecimento**
2. Adicionar texto de exemplo:

```
Horário de Funcionamento:
Nossa empresa funciona de segunda a sexta, das 9h às 18h.
Aos sábados atendemos das 9h às 13h.
Domingos e feriados não atendemos.

Produtos:
Vendemos notebooks, desktops e acessórios.
Temos garantia de 1 ano em todos os produtos.
Aceitamos cartão de crédito, débito e PIX.

Entrega:
Entregamos em todo o Brasil.
Prazo de entrega: 5 a 10 dias úteis.
Frete grátis para compras acima de R$ 500.
```

3. Clicar em **Salvar**
4. Aguardar mensagem de sucesso

**Verificar logs do backend**:
```bash
docker-compose logs bot -f
```

Deve aparecer:
- "Criando vectorstore para cliente X com Y chunks"
- "Vectorstore criado com sucesso"

---

### PASSO 4: Configurar tom do bot

1. Ir em: **Configurações do Bot**
2. Escolher um tom (exemplo: **Casual**)
3. Clicar em **Salvar**

---

### PASSO 5: Conectar WhatsApp

1. Ir em: **Conectar WhatsApp**
2. Clicar em **Criar Nova Instância**
3. Aguardar QR Code aparecer
4. Escanear com WhatsApp (WhatsApp → Configurações → Aparelhos conectados → Conectar aparelho)
5. Aguardar status mudar para **Conectado**

**Anote o número do WhatsApp conectado** (exemplo: 5511999999999)

---

### PASSO 6: Testar busca no vectorstore (opcional)

Antes de testar no WhatsApp, vamos verificar se a busca está funcionando:

```bash
# No navegador ou Postman
GET http://localhost:8000/api/v1/knowledge/search?q=horário&k=3

# Headers:
Authorization: Bearer SEU_TOKEN_JWT
```

Deve retornar chunks relevantes sobre horário de funcionamento.

---

### PASSO 7: Enviar mensagem no WhatsApp

**IMPORTANTE**: Use outro celular ou WhatsApp Web para enviar mensagem PARA o número conectado.

1. Abrir WhatsApp
2. Enviar mensagem para o número conectado
3. Exemplo: **"Qual o horário de funcionamento?"**

---

### PASSO 8: Acompanhar logs em tempo real

```bash
docker-compose logs bot -f
```

**O que você deve ver**:

```
📥 Mensagem recebida: 5511888888888@s.whatsapp.net | Instance: ...
✅ Cliente identificado: ID=1 | Email=...
[BUFFER] Mensagem adicionada ao buffer de 5511888888888@s.whatsapp.net: Qual o horário de funcionamento?
[BUFFER] Iniciando debounce para 5511888888888@s.whatsapp.net
[BUFFER] Processando mensagem para 5511888888888@s.whatsapp.net: Qual o horário de funcionamento?
[BUFFER] Usando tom: casual
INFO:app.services.ai.ai_service:Processando mensagem para cliente 1: 'Qual o horário de funcionamento?...'
INFO:app.services.rag.vectorstore:Buscando no vectorstore do cliente 1: 'Qual o horário de funcionamento?'
INFO:app.services.rag.vectorstore:Encontrados 5 resultados
INFO:app.services.ai.ai_service:Contexto encontrado: 5 chunks, confiança: 0.85
INFO:app.services.ai.ai_service:Histórico: 0 mensagens
INFO:app.services.ai.ai_service:Resposta gerada: 'Olá! Nosso horário de funcionamento é...'
[BUFFER] Resposta gerada (confiança: 0.85): Olá! Nosso horário de funcionamento é de segunda a sexta, das 9h às 18h...
[BUFFER] Resposta enviada para 5511888888888@s.whatsapp.net
✅ Mensagem processada para cliente 1
```

---

### PASSO 9: Verificar resposta no WhatsApp

O bot deve responder em **3-5 segundos** com informação baseada no conhecimento cadastrado.

**Exemplo de resposta esperada**:
```
Olá! Nosso horário de funcionamento é de segunda a sexta, das 9h às 18h. 
Aos sábados atendemos das 9h às 13h. 
Domingos e feriados não atendemos. 😊
```

---

### PASSO 10: Testar memória da conversa

Envie uma sequência de mensagens:

1. **Você**: "Meu nome é João"
2. **Bot**: Responde algo
3. **Você**: "Qual é o meu nome?"
4. **Bot**: Deve lembrar que é João

**Verificar logs**:
```
INFO:app.services.ai.ai_service:Histórico: 2 mensagens
```

---

### PASSO 11: Testar pergunta fora do conhecimento

Envie: **"Qual a previsão do tempo hoje?"**

**Resposta esperada**:
```
Desculpe, não tenho essa informação disponível no momento.
```

**Verificar logs**:
```
INFO:app.services.ai.ai_service:Contexto encontrado: 5 chunks, confiança: 0.15
```

Confiança baixa = resposta genérica

---

### PASSO 12: Testar diferentes tons

#### Tom Casual (já testado)
- Resposta amigável e descontraída

#### Tom Formal
1. Ir no dashboard → Configurações
2. Mudar para **Formal**
3. Salvar
4. Enviar: "Qual o horário?"
5. Resposta deve ser mais formal e profissional

#### Tom Técnico
1. Mudar para **Técnico**
2. Enviar: "Como funciona a garantia?"
3. Resposta deve ser mais técnica e detalhada

---

## ✅ CHECKLIST DE SUCESSO

- [ ] Backend rodando sem erros
- [ ] ChromaDB rodando
- [ ] Cliente criado e ativo
- [ ] Login funcionando
- [ ] Conhecimento salvo (embeddings gerados)
- [ ] WhatsApp conectado (QR Code)
- [ ] Mensagem enviada no WhatsApp
- [ ] Bot respondeu em 3-5 segundos
- [ ] Resposta usa conhecimento cadastrado
- [ ] Logs mostram busca no vectorstore
- [ ] Logs mostram confiança calculada
- [ ] Memória funciona (lembra contexto)
- [ ] Pergunta fora do conhecimento retorna "não sei"
- [ ] Diferentes tons funcionam

---

## 🐛 TROUBLESHOOTING

### Bot não responde

**Verificar**:
1. Logs do backend: `docker-compose logs bot -f`
2. Status da instância: Dashboard → Conectar WhatsApp
3. Cliente está ativo: verificar no banco
4. Conhecimento foi salvo: verificar logs de embeddings

**Possíveis causas**:
- Instância desconectada
- Cliente inativo
- Erro na OpenAI (verificar API key e créditos)
- ChromaDB não está rodando

### Resposta genérica (não usa conhecimento)

**Verificar**:
1. Embeddings foram gerados: `docker-compose logs bot | grep "Vectorstore criado"`
2. Busca funciona: testar endpoint `/api/v1/knowledge/search`
3. ChromaDB está acessível: `docker-compose ps chromadb`

**Solução**:
- Salvar conhecimento novamente
- Reiniciar ChromaDB: `docker-compose restart chromadb`

### Erro "Cliente não encontrado"

**Causa**: Instância não está vinculada ao cliente

**Solução**:
1. Verificar tabela `instancias_whatsapp`
2. Recriar instância pelo dashboard

### Erro ao chamar OpenAI

**Verificar**:
1. OPENAI_API_KEY no .env
2. Créditos disponíveis na conta OpenAI
3. Modelo configurado existe (gpt-4, gpt-3.5-turbo)

**Logs**:
```
ERROR:app.services.ai.ai_service:Erro ao gerar resposta: ...
```

### Mensagem de grupo sendo processada

**Verificar logs**:
```
⚠️ Mensagem de grupo ignorada: 5511999999999-1234567890@g.us
```

Se não aparecer, verificar código do webhook em `main.py`.

---

## 📊 MÉTRICAS ESPERADAS

### Performance
- Tempo de resposta: **3-5 segundos**
- Busca no vectorstore: **< 1 segundo**
- Chamada OpenAI: **2-4 segundos**

### Confiança
- Pergunta no conhecimento: **> 0.7**
- Pergunta fora do conhecimento: **< 0.3**

### Logs
- Cada mensagem deve gerar ~10-15 linhas de log
- Sem erros ou warnings (exceto grupos ignorados)

---

## 🎉 TESTE COMPLETO

Se todos os itens do checklist passaram, a FASE 11 está **100% funcional**!

Próximo passo: **Comitar** e seguir para FASE 12 (Fallback para humano).

---

**Data**: 2026-02-05
**Testador**: _______________________
**Resultado**: [ ] ✅ Passou  [ ] ❌ Falhou
**Observações**: _______________________
