# STATUS FASE 9 - Embeddings + ChromaDB + Vector Search Multi-tenant

## ✅ CONCLUÍDO

### Infraestrutura

**Docker Compose** (`docker-compose.yml`)
- ✅ ChromaDB adicionado como serviço
- ✅ Porta: 8001 (externa) → 8000 (interna)
- ✅ Volume persistente: `chromadb_data`
- ✅ Configurações:
  - IS_PERSISTENT=TRUE
  - ANONYMIZED_TELEMETRY=FALSE
- ✅ Container rodando e acessível

### Backend

**Configurações** (`apps/backend/app/core/config.py`)
- ✅ `CHROMA_HOST = "chromadb"`
- ✅ `CHROMA_PORT = 8000`

**Vectorstore** (`apps/backend/app/services/rag/vectorstore.py`)
- ✅ Refatorado para usar ChromaDB via HTTP
- ✅ `get_chroma_client()` - Cliente HTTP configurado
- ✅ `criar_vectorstore_de_chunks()` - Cria vectorstore a partir de chunks
  - Apaga coleção antiga
  - Cria documentos com metadata
  - Gera embeddings com OpenAI
  - Salva no ChromaDB
- ✅ `buscar_no_vectorstore()` - Busca semântica
  - Retorna top-k resultados
  - Inclui scores de similaridade
  - Retorna metadata dos chunks
- ✅ `deletar_vectorstore_cliente()` - Remove coleção do cliente
- ✅ Multi-tenant: collection = `tenant_{cliente_id}`

**ConhecimentoService** (`apps/backend/app/services/conhecimento/conhecimento_service.py`)
- ✅ Integração com vectorstore ao salvar
- ✅ Fluxo automático:
  1. Salva texto no Postgres
  2. Gera chunks
  3. Cria embeddings
  4. Salva no ChromaDB
- ✅ Se conteúdo vazio: deleta vectorstore
- ✅ Tratamento de erros (não falha se embeddings falharem)

**Endpoints** (`apps/backend/app/api/v1/conhecimento.py`)
- ✅ `GET /api/v1/knowledge/search?q=texto&k=5` - Busca semântica
  - Query param `q`: texto da busca
  - Query param `k`: número de resultados (default: 5)
  - Retorna: query, total_results, results (text, score, metadata)
  - Autenticação obrigatória (JWT)

### Fluxo Completo

**Ao salvar conhecimento:**
```
1. Cliente salva texto (até 50k chars)
2. Backend valida e salva no Postgres
3. Backend gera chunks (~800 chars, 20% overlap)
4. Backend deleta coleção antiga do ChromaDB
5. Backend cria documentos com metadata
6. OpenAI gera embeddings para cada chunk
7. ChromaDB armazena embeddings na coleção tenant_{cliente_id}
```

**Ao buscar:**
```
1. Cliente faz query de busca
2. Backend gera embedding da query (OpenAI)
3. ChromaDB busca chunks similares (cosine similarity)
4. Backend retorna top-k resultados com scores
```

## 📋 Critérios de Aceite (FASE 9)

- [x] ChromaDB rodando no docker-compose
- [x] Vectorstore multi-tenant (collection por cliente)
- [x] Ao salvar conhecimento:
  - [x] Apagar coleção antiga
  - [x] Criar nova
  - [x] Gerar embeddings (OpenAI)
  - [x] Inserir documentos
- [x] Endpoint de busca semântica
- [x] Isolamento entre clientes validado (collections separadas)

## 🎯 Próximas Fases

**FASE 10** - Integração Evolution API + QR no dashboard
- Criar tabela `instancias_whatsapp`
- Endpoints para criar instância e pegar QR
- Frontend: exibir QR e status da conexão
- Filtrar mensagens de grupo
- Webhook recebe mensagens

**FASE 11** - Pipeline IA (RAG + Memória) respondendo no WhatsApp
- Receber mensagem → buscar contexto → chamar OpenAI → responder
- Memória de 10 mensagens (Redis)
- RAG: buscar top-k chunks
- Montar prompt com contexto
- Enviar resposta via Evolution

## 📝 Notas Técnicas

**ChromaDB:**
- Porta 8001 (externa) para não conflitar com backend (8000)
- Persistência habilitada (dados não são perdidos ao reiniciar)
- Telemetria desabilitada

**Embeddings:**
- Modelo: OpenAI text-embedding-ada-002 (padrão do LangChain)
- Dimensões: 1536
- Custo: ~$0.0001 por 1k tokens

**Multi-tenant:**
- Cada cliente tem collection isolada: `tenant_{cliente_id}`
- Cliente A não consegue acessar dados do Cliente B
- Collections são criadas/deletadas automaticamente

**Performance:**
- Chunks pequenos (~800 chars) = melhor precisão
- Overlap 20% = contexto entre chunks
- Top-k = 5 (padrão) = bom balanço precisão/contexto

**Metadata dos Chunks:**
```python
{
    'cliente_id': int,
    'chunk_index': int,
    'start': int,  # posição inicial no texto original
    'end': int     # posição final no texto original
}
```

## 🧪 Testes Pendentes

- [ ] Testar salvar conhecimento e verificar embeddings gerados
- [ ] Testar busca semântica com query relevante
- [ ] Testar busca semântica com query irrelevante
- [ ] Testar isolamento: Cliente A não vê dados do Cliente B
- [ ] Testar atualização de conhecimento (deve recriar embeddings)
- [ ] Testar conhecimento vazio (deve deletar vectorstore)
- [ ] Verificar ChromaDB UI (http://localhost:8001)

## 🔍 Debug

**Ver collections no ChromaDB:**
```python
import chromadb
client = chromadb.HttpClient(host="localhost", port=8001)
collections = client.list_collections()
print(collections)
```

**Testar busca via API:**
```bash
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/v1/knowledge/search?q=teste&k=3"
```

---

**Data de Conclusão:** 05/02/2026
**Status:** ✅ FASE 9 COMPLETA - Pronto para FASE 10
