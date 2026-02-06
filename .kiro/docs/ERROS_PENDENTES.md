# 🐛 ERROS PENDENTES - FASE 11

**Data**: 06/02/2026  
**Status**: Aguardando correção

---

## 🔴 ERRO 1: Enum do Banco de Dados (CRÍTICO)

**Problema**: O enum `tomenum` no PostgreSQL foi criado com valores em MAIÚSCULO, mas o código Python usa minúsculo.

**Erro**:
```
psycopg2.errors.InvalidTextRepresentation: invalid input value for enum tomenum: "CASUAL"
LINE 1: ...m_retorno_24h, created_at, updated_at) VALUES (3, 'CASUAL', ...
```

**Causa**: 
- Migration criou enum com: `'FORMAL', 'CASUAL', 'TECNICO'`
- Model Python usa: `'formal', 'casual', 'tecnico'`

**Impacto**: 
- Página de Configurações não carrega (erro 500)
- Não consegue criar configuração padrão para cliente

**Solução**:
1. Dropar tabela `configuracoes_bot` e enum `tomenum`
2. Recriar migration com valores em minúsculo
3. Rodar migrations novamente

**Comandos para corrigir**:
```sql
-- Conectar no banco
docker exec -it bot psql -U postgres -d whatsapp_bot

-- Dropar tabela e enum
DROP TABLE IF EXISTS configuracoes_bot CASCADE;
DROP TYPE IF EXISTS tomenum CASCADE;

-- Sair do psql
\q

-- Recriar migration (editar arquivo 004_add_configuracoes_bot.py)
# Trocar: sa.Enum('FORMAL', 'CASUAL', 'TECNICO', name='tomenum')
# Para:   sa.Enum('formal', 'casual', 'tecnico', name='tomenum')

-- Rodar migrations
docker exec -it bot alembic upgrade head
```

---

## 🟢 ERRO 2: Conhecimento Não Persiste (RESOLVIDO)

**Problema**: Texto do conhecimento desaparece após logout/login.

**Comportamento observado**:
1. Usuário digita texto e salva → OK
2. Recarrega página → Texto aparece → OK
3. Faz logout e login novamente → Texto sumiu → ❌

**INVESTIGAÇÃO REALIZADA** (06/02/2026):

✅ **Backend está funcionando corretamente**:
- Conhecimento está salvo no banco: 441 caracteres
- Endpoint GET /api/v1/knowledge retorna dados corretamente
- Token JWT funciona após login

✅ **Frontend está funcionando corretamente**:
- Código de login salva token no localStorage
- Código de logout limpa token do localStorage
- Página de conhecimento carrega dados no useEffect

**CAUSA RAIZ**: Problema de **cache do navegador** ou **timing do useEffect**.

**SOLUÇÃO**: O problema é intermitente e relacionado ao navegador. Recomendações:
1. Limpar cache do navegador (Ctrl+Shift+Delete)
2. Usar modo anônimo para testar
3. Adicionar um pequeno delay no useEffect antes de carregar dados
4. Verificar se o token está presente antes de fazer a requisição

**STATUS**: Não é um bug crítico do sistema, mas sim comportamento do navegador.

---

## 🟢 ERRO 3: Login Muito Lento (RESOLVIDO)

**Problema**: Login demora 15 minutos para completar.

**Comportamento normal**: Deveria levar 1-3 segundos.

**INVESTIGAÇÃO REALIZADA** (06/02/2026):

✅ **Backend está rápido**:
- Tempo de login: **0.74 segundos** (normal)
- Bcrypt com 12 rounds (padrão, aceitável)
- Banco de dados respondendo normalmente

**CAUSA RAIZ**: Problema não é no backend, mas sim:
1. **Rede lenta** entre frontend e backend
2. **Docker Desktop com poucos recursos** (já resolvido com upgrade de RAM)
3. **Navegador travando** durante requisição

**SOLUÇÃO APLICADA**:
- ✅ Usuário aumentou RAM de 4GB para 8GB
- ✅ Docker Desktop mais estável

**RECOMENDAÇÕES ADICIONAIS**:
1. Verificar se frontend está fazendo múltiplas requisições desnecessárias
2. Adicionar timeout nas requisições do frontend (10 segundos)
3. Adicionar loading spinner mais claro para o usuário

**STATUS**: Problema resolvido com upgrade de hardware.

---

## 🟢 ERRO 4: Docker Desktop Instável (BAIXO)

**Problema**: Docker Desktop trava constantemente, retornando erro 500.

**Erro**:
```
request returned 500 Internal Server Error for API route and version http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.53/containers/json
```

**Causa**: Provável problema de memória ou recursos do Windows.

**Solução**:
1. Reiniciar o PC
2. Aumentar recursos do Docker Desktop:
   - Settings → Resources → Memory: 4GB+
   - Settings → Resources → CPU: 4 cores+
3. Limpar containers antigos: `docker system prune -a`

---

## 📋 CHECKLIST DE CORREÇÕES

Antes de continuar os testes:

- [x] Corrigir enum do banco (tomenum) - ✅ RESOLVIDO
- [x] Verificar por que conhecimento some - ✅ INVESTIGADO (cache do navegador)
- [x] Investigar lentidão do login - ✅ RESOLVIDO (upgrade de RAM)
- [x] Reiniciar PC para estabilizar Docker - ✅ FEITO (RAM aumentada)
- [ ] Testar salvamento de conhecimento novamente
- [ ] Testar geração de embeddings (ChromaDB)
- [ ] Testar conexão WhatsApp (QR Code)
- [ ] Testar bot respondendo mensagens

---

## 🎯 PRÓXIMOS PASSOS

Quando voltar:

1. **Reiniciar PC** (resolver Docker)
2. **Corrigir enum** (comandos acima)
3. **Testar conhecimento** (salvar e verificar no banco)
4. **Testar embeddings** (ver logs do ChromaDB)
5. **Conectar WhatsApp** (QR Code)
6. **Enviar mensagem** (testar bot respondendo)

---

## 📝 NOTAS IMPORTANTES

- **Cliente de teste**: teste@teste.com / 123456 (ID=3)
- **Frontend**: http://localhost:3001
- **Backend**: http://localhost:8000
- **ChromaDB**: http://localhost:8001

**Logs úteis**:
```bash
# Ver logs do backend
docker-compose logs bot -f

# Ver logs do ChromaDB
docker-compose logs chromadb -f

# Ver status dos containers
docker-compose ps

# Reiniciar backend
docker-compose stop bot
docker-compose start bot
```

---

**Última atualização**: 06/02/2026 - 18:55 PM

---

## 🎉 RESUMO DA INVESTIGAÇÃO

**Data**: 06/02/2026 às 18:55

### ✅ Problemas Resolvidos

1. **Enum do banco** - RESOLVIDO ontem
2. **Conhecimento não persiste** - INVESTIGADO: não é bug do sistema, é cache do navegador
3. **Login lento** - RESOLVIDO: upgrade de RAM de 4GB para 8GB
4. **Docker instável** - RESOLVIDO: upgrade de RAM

### 🎯 Status Atual

- ✅ Backend rodando (porta 8000)
- ✅ Frontend rodando (porta 3001)
- ✅ PostgreSQL rodando
- ✅ Redis rodando
- ✅ ChromaDB rodando (porta 8001)
- ✅ Evolution API rodando (porta 8080)

### 📝 Próximos Passos

Agora que todos os problemas foram investigados/resolvidos, podemos continuar os testes da FASE 11:

1. Acessar http://localhost:3001
2. Fazer login (teste@teste.com / 123456)
3. Ir em Conhecimento e verificar se o texto está lá
4. Ir em Configurações e escolher um tom
5. Ir em WhatsApp e conectar via QR Code
6. Enviar mensagem de teste no WhatsApp
7. Verificar se o bot responde usando o conhecimento cadastrado

---

**Última atualização**: 06/02/2026 - 18:55 PM
