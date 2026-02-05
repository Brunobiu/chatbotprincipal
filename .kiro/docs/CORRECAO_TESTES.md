# 🔧 CORREÇÃO DOS TESTES

## Problema Identificado

O `conftest.py` estava no lugar errado (`apps/backend/conftest.py`).
Pytest não conseguia encontrar as fixtures `db_session` e `client`.

## Solução Aplicada

✅ Movido `conftest.py` para `apps/backend/app/tests/conftest.py`
✅ Removido `--strict-markers` do pytest.ini (causava warnings)

---

## 🧪 TESTE NOVAMENTE

### Dentro do container (você já está lá):

```bash
# Rodar testes novamente
pytest -v
```

**Agora DEVE funcionar!** ✅

---

## 📊 RESULTADO ESPERADO

```
========================= 34 passed in X.XXs =========================
```

---

## Se ainda der erro:

Me mande o output completo!
