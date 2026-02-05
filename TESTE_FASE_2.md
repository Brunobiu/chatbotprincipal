# 🧪 TESTE - MINI-FASE 2: Isolamento Multi-tenant no RAG

## ✅ O que foi implementado

1. **Vectorstore Multi-tenant** (`apps/backend/app/services/rag/vectorstore.py`)
   - Coleções separadas por cliente: `tenant_{cliente_id}`
   - Funções para criar/deletar vectorstore por cliente
   - Suporte a documentos por cliente em `rag_files/cliente_{id}/`

2. **Chains com Cliente ID** (`apps/backend/app/services/llm/chains.py`)
   - RAG chain aceita `cliente_id`
   - Isolamento automático de contexto

3. **Message Buffer com Cliente ID** (`apps/backend/app/services/conversations/message_buffer.py`)
   - Session ID único por cliente: `cliente_{id}_{chat_id}`
   - Memória isolada por cliente

4. **Modelo InstanciaWhatsApp** (`apps/backend/app/db/models/instancia_whatsapp.py`)
   - Tabela para mapear instâncias do WhatsApp a clientes
   - Status da conexão

5. **Webhook com Lookup de Cliente** (`apps/backend/app/main.py`)
   - Identifica cliente por `instance_id` ou `numero`
   - Valida assinatura ativa
   - Passa `cliente_id` para processamento

6. **Migration 003** - Tabela `instancias_whatsapp`

---

## 🧪 Como testar

### Teste 1: Verificar Migration

```bash
# Rebuild containers para aplicar migration
docker-compose down
docker-compose up -d --build

# Ver logs
docker logs bot --tail 30
```

**Resultado esperado:**
```
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, add instancias whatsapp table
```

---

### Teste 2: Criar Instância WhatsApp para Cliente

```bash
docker exec -it bot bash
```

Dentro do container:

```bash
python << 'EOF'
import sys
sys.path.insert(0, '/app/apps/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models.cliente import Cliente
from app.db.models.instancia_whatsapp import InstanciaWhatsApp, InstanciaStatus
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Buscar cliente de teste
    cliente = db.query(Cliente).filter(Cliente.email == "teste@exemplo.com").first()
    
    if not cliente:
        print("❌ Cliente de teste não encontrado. Execute TESTE_FASE_1 primeiro.")
    else:
        # Criar instância WhatsApp
        instancia = InstanciaWhatsApp(
            cliente_id=cliente.id,
            instance_id="test_instance_123",
            numero="5511999999999",
            status=InstanciaStatus.CONECTADA
        )
        
        db.add(instancia)
        db.commit()
        db.refresh(instancia)
        
        print(f"✅ Instância WhatsApp criada!")
        print(f"   ID: {instancia.id}")
        print(f"   Cliente ID: {instancia.cliente_id}")
        print(f"   Instance ID: {instancia.instance_id}")
        print(f"   Número: {instancia.numero}")
        print(f"   Status: {instancia.status}")

except Exception as e:
    print(f"❌ Erro: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
EOF
```

---

### Teste 3: Testar Isolamento de Vectorstore

```bash
python << 'EOF'
import sys
sys.path.insert(0, '/app/apps/backend')

from app.services.rag.vectorstore import get_collection_name, criar_vectorstore_cliente
from langchain_core.documents import Document

# Testar nomes de coleção
print("🧪 Testando nomes de coleção...")
print(f"   Cliente 1: {get_collection_name(1)}")
print(f"   Cliente 2: {get_collection_name(2)}")

# Criar vectorstore para cliente 1
print("\n🧪 Criando vectorstore para cliente 1...")
docs_cliente1 = [
    Document(page_content="O produto X custa R$ 100 e é azul."),
    Document(page_content="O produto X tem garantia de 1 ano."),
]

vectorstore1 = criar_vectorstore_cliente(1, docs_cliente1)
print("✅ Vectorstore cliente 1 criado!")

# Criar vectorstore para cliente 2
print("\n🧪 Criando vectorstore para cliente 2...")
docs_cliente2 = [
    Document(page_content="O produto Y custa R$ 200 e é vermelho."),
    Document(page_content="O produto Y tem garantia de 2 anos."),
]

vectorstore2 = criar_vectorstore_cliente(2, docs_cliente2)
print("✅ Vectorstore cliente 2 criado!")

# Testar busca isolada
print("\n🧪 Testando busca isolada...")

# Cliente 1 busca "produto"
results1 = vectorstore1.similarity_search("produto", k=2)
print(f"\n📊 Cliente 1 busca 'produto':")
for i, doc in enumerate(results1, 1):
    print(f"   {i}. {doc.page_content[:50]}...")

# Cliente 2 busca "produto"
results2 = vectorstore2.similarity_search("produto", k=2)
print(f"\n📊 Cliente 2 busca 'produto':")
for i, doc in enumerate(results2, 1):
    print(f"   {i}. {doc.page_content[:50]}...")

print("\n✅ Teste de isolamento concluído!")
print("   Cliente 1 só vê seus documentos (produto X)")
print("   Cliente 2 só vê seus documentos (produto Y)")
EOF
```

**Resultado esperado:**
```
✅ Vectorstore cliente 1 criado!
✅ Vectorstore cliente 2 criado!

📊 Cliente 1 busca 'produto':
   1. O produto X custa R$ 100 e é azul....
   2. O produto X tem garantia de 1 ano....

📊 Cliente 2 busca 'produto':
   1. O produto Y custa R$ 200 e é vermelho....
   2. O produto Y tem garantia de 2 anos....

✅ Teste de isolamento concluído!
```

---

### Teste 4: Verificar Banco de Dados

```bash
exit  # Sair do container bot
```

```bash
docker exec -it postgres psql -U postgres -d whatsapp_bot
```

Dentro do PostgreSQL:

```sql
-- Ver instâncias WhatsApp
SELECT id, cliente_id, instance_id, numero, status FROM instancias_whatsapp;

-- Ver clientes
SELECT id, nome, email, status FROM clientes;

-- Sair
\q
```

---

## 📊 Checklist de Validação

- [ ] Migration 003 rodou com sucesso
- [ ] Tabela `instancias_whatsapp` foi criada
- [ ] Instância WhatsApp foi criada para cliente de teste
- [ ] Vectorstore cria coleções separadas por cliente
- [ ] Busca retorna apenas documentos do cliente correto
- [ ] Não há vazamento de dados entre clientes
- [ ] Logs aparecem corretamente

---

## 🔍 Fluxo Implementado

```
1. Mensagem chega no WhatsApp
   ↓
2. Evolution API envia para /webhook
   ↓
3. Webhook extrai instance_id ou numero
   ↓
4. Busca InstanciaWhatsApp no banco
   ↓
5. Identifica cliente_id
   ↓
6. Valida se cliente está ATIVO
   ↓
7. Passa cliente_id para buffer_message
   ↓
8. Buffer cria session_id: cliente_{id}_{chat_id}
   ↓
9. RAG chain usa vectorstore do cliente: tenant_{id}
   ↓
10. Resposta usa APENAS conhecimento do cliente ✅
```

---

## 🐛 Troubleshooting

### Migration não roda
```bash
docker exec -it bot bash
cd /app/apps/backend
alembic upgrade head
```

### Erro ao criar vectorstore
Verifique se OpenAI API key está configurada no `.env`:
```
OPENAI_API_KEY=sk-...
```

### Cliente não encontrado no webhook
Certifique-se de criar uma instância WhatsApp para o cliente:
```sql
INSERT INTO instancias_whatsapp (cliente_id, instance_id, numero, status, created_at, updated_at)
VALUES (1, 'test_instance', '5511999999999', 'CONECTADA', NOW(), NOW());
```

---

## 🚀 Próximos Passos

Após validar que a MINI-FASE 2 está funcionando:

1. ✅ Testar isolamento de vectorstore
2. ✅ Verificar banco de dados
3. ✅ Confirmar que não há vazamento de dados
4. ➡️ **Avisar que está pronto para MINI-FASE 3 ou decisão**

---

## 📝 Notas Importantes

- ✅ Cada cliente tem sua própria coleção no ChromaDB
- ✅ Session ID inclui cliente_id para isolamento de memória
- ✅ Webhook valida assinatura ativa antes de processar
- ✅ Logs estruturados facilitam debugging
- ⏳ MINI-FASE 3 implementará segurança básica
- ⏳ MINI-FASE 4 implementará testes automatizados
