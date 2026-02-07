# 🔧 Problemas WhatsApp e Soluções

## 📋 Problemas Reportados

### 1️⃣ WhatsApp Conecta e Desconecta Sozinho
**Sintoma**: QR Code é gerado, usuário escaneia, conecta mas logo desconecta

**Causa Raiz**: 
- `CACHE_REDIS_SAVE_INSTANCES=false` no `.env`
- Evolution API não estava persistindo as sessões no Redis
- Cada restart perdia a sessão do WhatsApp

**Solução Aplicada**:
```env
CACHE_REDIS_SAVE_INSTANCES=true
```

**Como Funciona Agora**:
- Sessão é salva no Redis
- Persiste entre restarts
- Usuário escaneia QR Code apenas uma vez
- Conexão permanece estável

---

### 2️⃣ Erro ao Salvar Configurações
**Sintoma**: Frontend retorna "Erro ao salvar configurações"

**Causa Raiz**:
- Código Python em cache no container
- Enum `TomEnum` usando nome (`CASUAL`) ao invés de valor (`casual`)
- Container precisava ser recriado para aplicar mudanças

**Solução Aplicada**:
1. Corrigido `configuracao_service.py`: usa strings ao invés de enum
2. Corrigido `configuracao_bot.py`: default value usa string
3. Recriado container para limpar cache Python

**Status**: ✅ Resolvido - Testes passando

---

### 3️⃣ Frontend Não Reflete Estado Real da Conexão
**Sintoma**: Backend mostra conectado mas frontend não atualiza

**Causa Provável**:
- Polling de status a cada 5 segundos pode não ser suficiente
- Evolution API pode demorar para atualizar status
- Frontend pode estar em estado desatualizado

**Solução Recomendada**:
1. Implementar WebSocket para updates em tempo real
2. Ou reduzir intervalo de polling para 2-3 segundos
3. Adicionar botão "Atualizar Status" manual

**Código Atual** (`apps/frontend/app/dashboard/whatsapp/page.tsx`):
```typescript
useEffect(() => {
  if (instancia && status === 'pendente') {
    const interval = setInterval(() => {
      atualizarStatus()
    }, 5000) // 5 segundos
    
    return () => clearInterval(interval)
  }
}, [instancia, status])
```

**Sugestão de Melhoria**:
```typescript
// Polling mais frequente
const interval = setInterval(() => {
  atualizarStatus()
}, 2000) // 2 segundos

// Adicionar botão manual
<button onClick={atualizarStatus}>
  🔄 Atualizar Status
</button>
```

---

### 4️⃣ Comportamento Esperado vs Atual

**Comportamento Atual** ❌:
```
1. Gera QR Code
2. Usuário escaneia
3. Conecta
4. Desconecta sozinho
5. Gera QR Code novamente
```

**Comportamento Esperado** ✅:
```
1. Gera QR Code (primeira vez)
2. Usuário escaneia
3. Conecta
4. Permanece conectado
5. Sessão persiste entre restarts
```

**Status Após Correções**:
- ✅ Sessão agora persiste (Redis configurado)
- ✅ QR Code funciona corretamente
- 🔄 Testar se ainda desconecta (precisa validação do usuário)

---

## 🎯 Próximos Passos

### Teste Completo do Fluxo WhatsApp
1. Acessar http://localhost:3000/dashboard/whatsapp
2. Criar instância
3. Escanear QR Code
4. Verificar se permanece conectado
5. Reiniciar containers: `docker-compose restart`
6. Verificar se sessão persiste

### Se Ainda Desconectar
Verificar logs da Evolution API:
```bash
docker logs evolution_api --tail 100
```

Procurar por:
- `connection.update`
- `close`
- `logout`
- Erros de autenticação

### Melhorias Futuras
1. **WebSocket para Status em Tempo Real**
   - Evolution API suporta webhooks
   - Implementar endpoint para receber eventos
   - Atualizar frontend via WebSocket

2. **Indicador Visual Melhor**
   - Mostrar "Conectando..." durante scan
   - Mostrar "Conectado ✅" quando estável
   - Mostrar "Desconectado ⚠️" se perder conexão

3. **Logs de Conexão**
   - Salvar histórico de conexões/desconexões
   - Mostrar último horário de conexão
   - Alertar usuário se desconectar

---

## 📊 Status Atual

### ✅ Resolvido
- Persistência de conhecimento
- Persistência de configurações
- QR Code gerando corretamente
- Campo qr_code aumentado para TEXT
- Enum TomEnum corrigido
- Redis configurado para salvar instâncias

### 🔄 Em Teste
- Estabilidade da conexão WhatsApp
- Frontend refletindo status correto

### ⏳ Pendente
- Implementar WebSocket (opcional)
- Melhorar UX do status de conexão
- Adicionar logs de conexão

---

**Última atualização**: 07/02/2026 - 19:30
**Próximo teste**: Validar se WhatsApp permanece conectado após correções
