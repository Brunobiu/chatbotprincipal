# 🧪 TESTE DA MINI-FASE 3 - SEGURANÇA

## 📋 Passo a Passo

### 1️⃣ Parar e Rebuild Containers

```powershell
# Parar containers
docker-compose down

# Subir com rebuild (vai instalar slowapi e python-jose)
docker-compose up -d --build
```

**Aguarde uns 2-3 minutos para o build completar.**

---

### 2️⃣ Ver Logs de Inicialização

```powershell
docker logs bot --tail 50
```

**O que você DEVE ver:**
```
🚀 Aplicação iniciada com segurança habilitada
🔒 CORS configurado para: ['http://localhost:3000', 'http://localhost:8000']
⏱️ Rate limit: 60 req/min
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Se aparecer erro de import ou módulo não encontrado:**
- Significa que o build não instalou as dependências
- Rode: `docker-compose build --no-cache`
- Depois: `docker-compose up -d`

---

### 3️⃣ Testar Health Check

```powershell
curl http://localhost:8000/health
```

**Resultado esperado:**
```json
{"status":"ok","service":"whatsapp-ai-bot"}
```

---

### 4️⃣ Testar Health DB

```powershell
curl http://localhost:8000/health/db
```

**Resultado esperado:**
```json
{"status":"ok","database":"connected","test_query":1}
```

---

### 5️⃣ Testar Rate Limiting (OPCIONAL)

**Fazer 5 requisições rápidas:**
```powershell
for ($i=1; $i -le 5; $i++) {
    curl http://localhost:8000/health
    Write-Host "Request $i"
}
```

**Resultado esperado:**
- Todas devem retornar: `{"status":"ok","service":"whatsapp-ai-bot"}`

**Para testar o limite (61 requisições):**
```powershell
for ($i=1; $i -le 61; $i++) {
    $response = curl http://localhost:8000/health 2>&1
    Write-Host "Request $i : $response"
}
```

**A 61ª deve retornar erro 429 (Too Many Requests)**

---

### 6️⃣ Ver Logs de Requisições

```powershell
docker logs bot --tail 20
```

**O que você DEVE ver:**
```
📥 GET /health
📤 GET /health | Status: 200 | Time: 0.003s
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Marque o que funcionou:

- [ ] Containers subiram sem erros
- [ ] Logs mostram "🚀 Aplicação iniciada com segurança habilitada"
- [ ] Logs mostram "🔒 CORS configurado"
- [ ] Logs mostram "⏱️ Rate limit: 60 req/min"
- [ ] `/health` retorna 200
- [ ] `/health/db` retorna 200
- [ ] Logs mostram requisições com emojis (📥 📤)
- [ ] Logs mostram tempo de processamento

---

## ❌ TROUBLESHOOTING

### Erro: "ModuleNotFoundError: No module named 'slowapi'"

**Solução:**
```powershell
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Erro: "ValidationError" no config.py

**Solução:**
- Verifique se todas as variáveis obrigatórias estão no `.env`
- Veja o erro específico nos logs: `docker logs bot`

### Container não sobe

**Solução:**
```powershell
# Ver erro completo
docker logs bot

# Rebuild forçado
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🎉 SUCESSO!

Se tudo funcionou:
1. ✅ MINI-FASE 3 está completa e validada
2. ✅ Segurança básica implementada
3. ✅ Pronto para fazer commit

**Me avise quando terminar os testes!** 🚀
