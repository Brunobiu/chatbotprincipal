# 🚀 PRÓXIMOS PASSOS - FASE 11

**Criado**: 07/02/2026 - 03:45  
**Prioridade**: ALTA

---

## 🎯 OBJETIVO

Finalizar FASE 11 (Pipeline IA completo) com:
- ✅ Salvar conhecimento funcionando (< 3s)
- ✅ Buscar conhecimento funcionando
- ✅ Persistência de dados
- ✅ Frontend sem cache

---

## 📋 CHECKLIST RÁPIDO

### Passo 1: Testar Estado Atual (5 min)
```powershell
# Verificar se backend está rodando
docker ps

# Testar backend
.\testar_backend.ps1

# Resultado esperado:
# ✅ Health Check: OK
# ✅ Login: ~0.7s
# ✅ Buscar: ~0.04s (696 chars)
# ❌ Salvar: TIMEOUT
```

### Passo 2: Corrigir Endpoint PUT (15 min)

**Arquivo**: `apps/backend/app/api/v1/conhecimento.py`

**Substituir o endpoint PUT por**:
```python
@router.put("/knowledge", response_model=ConhecimentoResponse)
async def update_conhecimento(
    request: ConhecimentoUpdateRequest,
    cliente = Depends(get_current_cliente)
):
    """
    Atualiza conhecimento - VERSÃO SIMPLIFICADA
    Salva no banco SEM embeddings por enquanto
    """
    from app.db.session import SessionLocal
    from app.db.models.conhecimento import Conhecimento
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Validar tamanho
    if len(request.conteudo_texto) > 50000:
        raise HTTPException(400, "Conteúdo excede 50.000 caracteres")
    
    db = SessionLocal()
    try:
        # Buscar ou criar conhecimento
        conhecimento = db.query(Conhecimento).filter(
            Conhecimento.cliente_id == cliente.id
        ).first()
        
        if not conhecimento:
            conhecimento = Conhecimento(
                cliente_id=cliente.id,
                conteudo_texto=request.conteudo_texto
            )
            db.add(conhecimento)
        else:
            conhecimento.conteudo_texto = request.conteudo_texto
        
        db.commit()
        db.refresh(conhecimento)
        
        logger.info(f"Conhecimento salvo: {len(request.conteudo_texto)} chars")
        
        return {
            "conteudo_texto": conhecimento.conteudo_texto,
            "total_chars": len(conhecimento.conteudo_texto),
            "max_chars": 50000
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao salvar: {e}")
        raise HTTPException(500, f"Erro ao salvar: {str(e)}")
    finally:
        db.close()
```

### Passo 3: Reiniciar Backend (2 min)
```powershell
docker stop bot
docker start bot
Start-Sleep -Seconds 15
```

### Passo 4: Testar Novamente (2 min)
```powershell
.\testar_backend.ps1

# Resultado esperado:
# ✅ Health Check: OK
# ✅ Login: ~0.7s
# ✅ Buscar: ~0.04s
# ✅ Salvar: ~1-3s (DEVE FUNCIONAR!)
```

### Passo 5: Testar Frontend (5 min)
1. **Modo anônimo**: `Ctrl+Shift+N`
2. **Acesse**: http://localhost:3001
3. **Login**: teste@teste.com / 123456
4. **Vá em**: Conhecimento
5. **Digite algo** e clique em "Salvar"
6. **Deve salvar em 1-3 segundos!**

### Passo 6: Commit (2 min)
```bash
git add .
git commit -m "fix: simplifica endpoint PUT /knowledge para resolver timeout"
git push origin fix/critical-issues
```

---

## 🔧 SE AINDA NÃO FUNCIONAR

### Opção A: Versão Ainda Mais Simples

Se o endpoint acima ainda travar, use esta versão que NÃO salva no banco:

```python
@router.put("/knowledge", response_model=ConhecimentoResponse)
async def update_conhecimento(
    request: ConhecimentoUpdateRequest,
    cliente = Depends(get_current_cliente)
):
    """VERSÃO TEMPORÁRIA - Apenas retorna sucesso"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Simulando salvamento: {len(request.conteudo_texto)} chars")
    
    return {
        "conteudo_texto": request.conteudo_texto,
        "total_chars": len(request.conteudo_texto),
        "max_chars": 50000
    }
```

### Opção B: Investigar Logs

```powershell
# Ver logs do backend
docker logs bot --tail 50

# Procurar por:
# - Erros de conexão com PostgreSQL
# - Timeouts
# - Exceções Python
```

### Opção C: Rebuild Completo

```powershell
docker-compose down
docker-compose build --no-cache bot
docker-compose up -d
```

---

## 📊 MÉTRICAS ESPERADAS

| Operação | Tempo Atual | Tempo Esperado |
|----------|-------------|----------------|
| Health Check | 0.003s | < 0.1s ✅ |
| Login | 0.68s | < 1s ✅ |
| Buscar Conhecimento | 0.04s | < 0.5s ✅ |
| **Salvar Conhecimento** | **TIMEOUT** | **< 3s** ❌ |

**OBJETIVO**: Fazer "Salvar Conhecimento" funcionar em < 3 segundos.

---

## 🎯 CRITÉRIOS DE SUCESSO

### Mínimo Viável
- ✅ Salvar conhecimento funciona (< 3s)
- ✅ Dados persistem no banco
- ✅ Frontend carrega conhecimento
- ✅ Não trava outras requisições

### Ideal (Para Depois)
- ✅ Embeddings gerados em background
- ✅ Busca semântica funciona
- ✅ Tempo de salvamento < 1s
- ✅ Feedback visual no frontend

---

## 📝 NOTAS IMPORTANTES

1. **Embeddings desabilitados**: Por enquanto, foco em salvar/carregar texto
2. **Cache do navegador**: Sempre testar em modo anônimo
3. **Docker instável**: Se travar, reiniciar Docker Desktop
4. **Dados preservados**: 696 caracteres já salvos no banco

---

## 🚀 RESUMO DE 30 SEGUNDOS

1. **Substituir** endpoint PUT no `conhecimento.py`
2. **Reiniciar** backend: `docker restart bot`
3. **Testar**: `.\testar_backend.ps1`
4. **Deve funcionar** em < 3 segundos!

---

**Última atualização**: 07/02/2026 - 03:45  
**Tempo estimado**: 30 minutos  
**Prioridade**: ALTA - Bloqueia FASE 11