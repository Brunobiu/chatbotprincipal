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

## 🟡 ERRO 2: Conhecimento Não Persiste (MÉDIO)

**Problema**: Texto do conhecimento desaparece após logout/login.

**Comportamento observado**:
1. Usuário digita texto e salva → OK
2. Recarrega página → Texto aparece → OK
3. Faz logout e login novamente → Texto sumiu → ❌

**Log de sucesso**:
```
INFO:app.services.conhecimento.conhecimento_service:Conhecimento atualizado para cliente 3: 418 chars
```

**Possíveis causas**:
- Transação não está commitando corretamente
- Problema com isolamento de cliente_id
- Cache do frontend não está limpando

**Investigar**:
1. Verificar se realmente salvou no banco:
   ```python
   docker exec -it bot python3 -c "from app.db.session import SessionLocal; from app.db.models.conhecimento import Conhecimento; db = SessionLocal(); c = db.query(Conhecimento).filter(Conhecimento.cliente_id == 3).first(); print(c.conteudo_texto if c else 'VAZIO'); db.close()"
   ```

2. Verificar logs do endpoint GET /api/v1/knowledge

3. Verificar se token JWT está correto após login

---

## 🟡 ERRO 3: Login Muito Lento (MÉDIO)

**Problema**: Login demora 15 minutos para completar.

**Comportamento normal**: Deveria levar 1-3 segundos.

**Possíveis causas**:
1. **Bcrypt muito lento** - Configuração de rounds muito alta
2. **Banco de dados travando** - Conexão lenta ou timeout
3. **Endpoint /api/me demorando** - Busca de dados pesada
4. **Frontend esperando timeout** - Retry infinito

**Investigar**:
1. Ver logs do backend durante login
2. Verificar tempo de resposta de cada endpoint:
   - POST /api/v1/auth/login
   - GET /api/v1/auth/me
3. Verificar configuração do bcrypt (rounds)

**Solução temporária**:
- Reduzir rounds do bcrypt de 12 para 10

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

- [ ] Corrigir enum do banco (tomenum)
- [ ] Verificar por que conhecimento some
- [ ] Investigar lentidão do login
- [ ] Reiniciar PC para estabilizar Docker
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

**Última atualização**: 06/02/2026 - 02:10 AM
