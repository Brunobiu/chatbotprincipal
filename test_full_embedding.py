"""
Teste completo de geração de embeddings
"""
import sys
sys.path.insert(0, '/app')

import logging
logging.basicConfig(level=logging.INFO)

from app.db.session import SessionLocal
from app.services.conhecimento import ConhecimentoService

print("=" * 60)
print("TESTE COMPLETO DE EMBEDDINGS")
print("=" * 60)

db = SessionLocal()

try:
    # Buscar conhecimento
    print("\n1️⃣ Buscando conhecimento do cliente 1...")
    conhecimento = ConhecimentoService.buscar_ou_criar(db, 1)
    print(f"   ✅ Tamanho: {len(conhecimento.conteudo_texto)} chars")
    
    # Gerar chunks
    print("\n2️⃣ Gerando chunks...")
    chunks = ConhecimentoService.gerar_chunks(conhecimento.conteudo_texto)
    print(f"   ✅ {len(chunks)} chunks gerados")
    
    # Gerar embeddings
    print("\n3️⃣ Gerando embeddings no ChromaDB...")
    from app.services.rag.vectorstore import criar_vectorstore_de_chunks
    
    vectorstore = criar_vectorstore_de_chunks(1, chunks)
    print(f"   ✅ Vectorstore criado!")
    
    # Verificar se foram salvos
    print("\n4️⃣ Verificando ChromaDB...")
    from app.services.rag.vectorstore import get_chroma_client, get_collection_name
    
    client = get_chroma_client()
    collection = client.get_collection(get_collection_name(1))
    count = collection.count()
    print(f"   ✅ Documentos na coleção: {count}")
    
    if count > 0:
        print("\n5️⃣ Testando busca...")
        from app.services.rag.vectorstore import buscar_no_vectorstore
        
        results = buscar_no_vectorstore(1, "pizza", k=3)
        print(f"   ✅ {len(results)} resultados encontrados")
        
        if results:
            print(f"\n   Primeiro resultado:")
            print(f"   - Score: {results[0]['score']:.4f}")
            print(f"   - Texto: {results[0]['text'][:100]}...")
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
