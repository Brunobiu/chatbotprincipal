# 🧪 TESTE DA MINI-FASE 4 - TESTES AUTOMATIZADOS

## 📋 Passo a Passo

### 1️⃣ Rebuild Container (Instalar Pytest)

```powershell
# Parar containers
docker-compose down

# Subir com rebuild (vai instalar pytest e dependências)
docker-compose up -d --build
```

**Aguarde uns 2-3 minutos para o build completar.**

---

### 2️⃣ Verificar que Container Subiu

```powershell
docker ps
docker logs bot --tail 20
```

**Deve mostrar:**
```
🚀 Aplicação iniciada com segurança habilitada
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### 3️⃣ Entrar no Container

```powershell
docker exec -it bot bash
```

---

### 4️⃣ Navegar para Diretório de Testes

```bash
cd /app/apps/backend
```

---

### 5️⃣ Rodar TODOS os Testes

```bash
pytest -v
```

**O que você DEVE ver:**
```
========================= test session starts =========================
collected 34 items

app/tests/test_cliente_service.py::TestClienteService::test_gerar_senha_aleatoria PASSED
app/tests/test_cliente_service.py::TestClienteService::test_hash_senha PASSED
app/tests/test_cliente_service.py::TestClienteService::test_criar_cliente_from_stripe PASSED
...
========================= 34 passed in X.XXs =========================
```

---

### 6️⃣ Rodar Testes com Coverage

```bash
pytest --cov=app --cov-report=term-missing
```

**Vai mostrar:**
- Quais arquivos foram testados
- Porcentagem de cobertura
- Linhas que NÃO foram testadas

---

### 7️⃣ Rodar Testes por Categoria

```bash
# Apenas testes unitários
pytest -m unit -v

# Apenas testes de integração
pytest -m integration -v
```

---

### 8️⃣ Rodar Teste Específico

```bash
# Testar apenas ClienteService
pytest app/tests/test_cliente_service.py -v

# Testar apenas Vectorstore
pytest app/tests/test_vectorstore.py -v

# Testar apenas Webhook
pytest app/tests/test_webhook.py -v

# Testar apenas Segurança
pytest app/tests/test_security.py -v
```

---

### 9️⃣ Sair do Container

```bash
exit
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Marque o que funcionou:

- [ ] Container subiu sem erros
- [ ] Pytest instalado corretamente
- [ ] Todos os 34 testes passaram
- [ ] Coverage report gerado
- [ ] Testes unitários passaram (17 testes)
- [ ] Testes de integração passaram (17 testes)
- [ ] Nenhum teste falhou
- [ ] Coverage acima de 70%

---

## ❌ TROUBLESHOOTING

### Erro: "ModuleNotFoundError: No module named 'pytest'"

**Solução:**
```bash
# Dentro do container
pip install pytest pytest-asyncio pytest-cov httpx faker
```

### Erro: "No module named 'app'"

**Solução:**
```bash
# Certifique-se de estar no diretório correto
cd /app/apps/backend
pytest -v
```

### Erro: "ImportError: cannot import name 'X'"

**Solução:**
```bash
# Verificar se todos os arquivos existem
ls -la app/tests/
ls -la app/services/clientes/
```

### Alguns testes falharam

**Solução:**
- Veja qual teste falhou
- Leia a mensagem de erro
- Me mande o output completo do pytest

---

## 📊 RESULTADO ESPERADO

```
========================= test session starts =========================
platform linux -- Python 3.11.x, pytest-8.3.4
collected 34 items

app/tests/test_cliente_service.py::TestClienteService::test_gerar_senha_aleatoria PASSED [  2%]
app/tests/test_cliente_service.py::TestClienteService::test_hash_senha PASSED [  5%]
app/tests/test_cliente_service.py::TestClienteService::test_criar_cliente_from_stripe PASSED [  8%]
app/tests/test_cliente_service.py::TestClienteService::test_criar_cliente_duplicado PASSED [ 11%]
app/tests/test_cliente_service.py::TestClienteService::test_atualizar_status_subscription_ativo PASSED [ 14%]
app/tests/test_cliente_service.py::TestClienteService::test_atualizar_status_subscription_cancelado PASSED [ 17%]
app/tests/test_cliente_service.py::TestClienteService::test_atualizar_status_subscription_inexistente PASSED [ 20%]
app/tests/test_cliente_service.py::TestClienteService::test_buscar_por_email PASSED [ 23%]
app/tests/test_cliente_service.py::TestClienteService::test_buscar_por_email_inexistente PASSED [ 26%]
app/tests/test_cliente_service.py::TestClienteService::test_buscar_por_id PASSED [ 29%]
app/tests/test_cliente_service.py::TestClienteService::test_buscar_por_id_inexistente PASSED [ 32%]

app/tests/test_vectorstore.py::TestVectorstoreMultiTenant::test_get_collection_name PASSED [ 35%]
app/tests/test_vectorstore.py::TestVectorstoreMultiTenant::test_collection_names_diferentes PASSED [ 38%]
app/tests/test_vectorstore.py::TestVectorstoreMultiTenant::test_criar_vectorstore_cliente PASSED [ 41%]
app/tests/test_vectorstore.py::TestVectorstoreMultiTenant::test_criar_vectorstore_clientes_diferentes PASSED [ 44%]
app/tests/test_vectorstore.py::TestVectorstoreMultiTenant::test_deletar_vectorstore_cliente PASSED [ 47%]
app/tests/test_vectorstore.py::TestVectorstoreMultiTenant::test_chunk_size_e_overlap PASSED [ 50%]

app/tests/test_webhook.py::TestWebhookWhatsApp::test_webhook_sem_dados PASSED [ 52%]
app/tests/test_webhook.py::TestWebhookWhatsApp::test_webhook_mensagem_grupo PASSED [ 55%]
app/tests/test_webhook.py::TestWebhookWhatsApp::test_webhook_cliente_nao_encontrado PASSED [ 58%]
app/tests/test_webhook.py::TestWebhookWhatsApp::test_webhook_cliente_inativo PASSED [ 61%]
app/tests/test_webhook.py::TestWebhookWhatsApp::test_webhook_cliente_ativo_processa_mensagem PASSED [ 64%]
app/tests/test_webhook.py::TestWebhookWhatsApp::test_webhook_lookup_por_numero PASSED [ 67%]

app/tests/test_security.py::TestSecurity::test_health_check_retorna_200 PASSED [ 70%]
app/tests/test_security.py::TestSecurity::test_health_check_tem_process_time_header PASSED [ 73%]
app/tests/test_security.py::TestSecurity::test_health_db_retorna_200 PASSED [ 76%]
app/tests/test_security.py::TestSecurity::test_cors_headers_presentes PASSED [ 79%]
app/tests/test_security.py::TestSecurity::test_webhook_sem_api_key_retorna_403 PASSED [ 82%]
app/tests/test_security.py::TestSecurity::test_webhook_com_api_key_invalida_retorna_403 PASSED [ 85%]
app/tests/test_security.py::TestSecurity::test_endpoint_inexistente_retorna_404 PASSED [ 88%]
app/tests/test_security.py::TestSecurity::test_rate_limiting_configurado PASSED [ 91%]
app/tests/test_security.py::TestSecurityFunctions::test_config_tem_allowed_origins PASSED [ 94%]
app/tests/test_security.py::TestSecurityFunctions::test_config_tem_rate_limit PASSED [ 97%]
app/tests/test_security.py::TestSecurityFunctions::test_get_allowed_origins_list PASSED [100%]

========================= 34 passed in 5.23s =========================
```

---

## 🎉 SUCESSO!

Se todos os 34 testes passaram:
1. ✅ MINI-FASE 4 está completa e validada
2. ✅ Testes automatizados funcionando
3. ✅ Pronto para fazer commit

**Me mande o output do pytest quando terminar!** 🚀

Se algum teste falhar, me mande o erro completo que eu corrijo!
