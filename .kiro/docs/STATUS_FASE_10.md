# STATUS FASE 10 - Integração Evolution API + QR no Dashboard

## ✅ CONCLUÍDO

### Backend

**Model** (`apps/backend/app/db/models/instancia_whatsapp.py`)
- ✅ Tabela `instancias_whatsapp` já existia
- ✅ Campos: instance_id, numero, status, qr_code
- ✅ Enum `InstanciaStatus`: PENDENTE, CONECTADA, DESCONECTADA, ERRO
- ✅ Relacionamento com Cliente

**Service** (`apps/backend/app/services/whatsapp/whatsapp_service.py`)
- ✅ `criar_instancia()` - Cria instância na Evolution API
- ✅ `buscar_instancia()` - Busca instância do cliente
- ✅ `obter_qrcode()` - Obtém QR Code da Evolution API
- ✅ `obter_status()` - Obtém status da conexão
- ✅ `atualizar_status()` - Atualiza status no banco
- ✅ `desconectar_instancia()` - Desconecta WhatsApp

**Endpoints** (`apps/backend/app/api/v1/whatsapp.py`)
- ✅ `POST /api/v1/whatsapp/instance` - Cria instância
- ✅ `GET /api/v1/whatsapp/instance` - Retorna instância
- ✅ `GET /api/v1/whatsapp/qrcode` - Obtém QR Code
- ✅ `GET /api/v1/whatsapp/status` - Obtém status da conexão
- ✅ `DELETE /api/v1/whatsapp/instance` - Desconecta
- ✅ Autenticação obrigatória (JWT)

**Integração**
- ✅ Router registrado no `main.py`
- ✅ Comunicação com Evolution API via HTTP

### Frontend

**Página WhatsApp** (`apps/frontend/app/dashboard/whatsapp/page.tsx`)
- ✅ Botão "Criar Instância"
- ✅ Exibição de QR Code (base64)
- ✅ Polling de status a cada 5 segundos (quando pendente)
- ✅ Estados visuais:
  - Sem instância: botão criar
  - Pendente: QR Code + instruções
  - Conectada: confirmação + número + botão desconectar
  - Desconectada: aviso + botão reconectar
- ✅ Instruções de como escanear QR
- ✅ Mensagens de sucesso/erro
- ✅ Loading states

## 📋 Critérios de Aceite (FASE 10)

- [x] Tabela instancias_whatsapp criada
- [x] Endpoints para criar instância e pegar QR
- [x] Frontend exibe QR e status
- [x] Filtro de mensagens de grupo (já implementado no webhook)
- [x] Polling automático de status
- [x] Botão desconectar funcional
- [x] Instruções claras para o usuário

## 🎯 Próximas Fases

**FASE 11** - Pipeline IA (RAG + Memória) respondendo no WhatsApp
- Webhook recebe mensagem
- Buscar contexto no vectorstore (RAG)
- Buscar memória das últimas 10 mensagens (Redis)
- Montar prompt com contexto
- Chamar OpenAI
- Enviar resposta via Evolution API
- Registrar histórico

**FASE 12** - Confiança + Fallback para Humano
- Calcular confiança da resposta
- Se < 0.5: enviar fallback e transferir para humano
- Estados: IA_ATIVA, AGUARDANDO_HUMANO, HUMANO_RESPONDEU
- Dashboard: tela de conversas pendentes
- Interface de chat para resposta manual

## 📝 Notas Técnicas

**Evolution API:**
- Endpoint criar: `/instance/create`
- Endpoint QR: `/instance/connect/{instance_id}`
- Endpoint status: `/instance/connectionState/{instance_id}`
- Endpoint logout: `/instance/logout/{instance_id}`
- Autenticação: header `apikey`

**Instance ID:**
- Formato: `cliente_{cliente_id}`
- Único por cliente
- Usado para identificar instância na Evolution API

**QR Code:**
- Retornado em base64
- Válido por tempo limitado
- Precisa ser escaneado pelo WhatsApp do celular

**Status Mapping:**
- Evolution "open" → CONECTADA
- Evolution "close" → DESCONECTADA
- Outros → PENDENTE

**Polling:**
- Frontend faz polling a cada 5 segundos
- Apenas quando status = PENDENTE
- Para automaticamente quando conecta

**Webhook:**
- Já implementado no `main.py`
- Filtra mensagens de grupo (`@g.us`)
- Identifica cliente por `instance_id`
- Valida assinatura ativa

## 🧪 Testes Pendentes

- [ ] Testar criar instância
- [ ] Testar exibição de QR Code
- [ ] Testar escanear QR e conectar
- [ ] Testar polling de status
- [ ] Testar desconectar
- [ ] Testar reconectar
- [ ] Testar filtro de mensagens de grupo
- [ ] Testar webhook recebendo mensagens

## 🔍 Debug

**Ver instâncias na Evolution API:**
```bash
curl -H "apikey: {API_KEY}" \
  http://localhost:8080/instance/fetchInstances
```

**Ver status de uma instância:**
```bash
curl -H "apikey: {API_KEY}" \
  http://localhost:8080/instance/connectionState/cliente_1
```

**Testar webhook manualmente:**
```bash
curl -X POST http://localhost:8000/webhook \
  -H "X-API-Key: {WEBHOOK_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "instance": "cliente_1",
    "data": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net"
      },
      "message": {
        "conversation": "teste"
      }
    }
  }'
```

---

**Data de Conclusão:** 05/02/2026
**Status:** ✅ FASE 10 COMPLETA - Pronto para FASE 11
