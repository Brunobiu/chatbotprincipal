"""
Script para testar geração de embeddings manualmente
"""
import sys
import os
sys.path.insert(0, '/app')

from app.db.session import SessionLocal
from app.services.conhecimento import ConhecimentoService

print("=" * 60)
print("TESTE DE GERAÇÃO DE EMBEDDINGS")
print("=" * 60)

db = SessionLocal()

try:
    # Buscar conhecimento do cliente 1
    conhecimento = ConhecimentoService.buscar_ou_criar(db, 1)
    print(f"\n✅ Conhecimento encontrado:")
    print(f"   - Cliente ID: {conhecimento.cliente_id}")
    print(f"   - Tamanho: {len(conhecimento.conteudo_texto)} chars")
    print(f"   - Preview: {conhecimento.conteudo_texto[:100]}...")
    
    # Gerar chunks
    print(f"\n📦 Gerando chunks...")
    chunks = ConhecimentoService.gerar_chunks(conhecimento.conteudo_texto)
    print(f"   - Total de chunks: {len(chunks)}")
    
    if chunks:
        print(f"   - Primeiro chunk: {chunks[0]['text'][:100]}...")
    
    # Tentar gerar embeddings
    print(f"\n🔄 Gerando embeddings no ChromaDB...")
    from app.services.rag.vectorstore import criar_vectorstore_de_chunks
    
    vectorstore = criar_vectorstore_de_chunks(1, chunks)
    
    if vectorstore:
        print(f"   ✅ Embeddings gerados com sucesso!")
        
        # Verificar se foram salvos
        from app.services.rag.vectorstore import get_chroma_client, get_collection_name
        client = get_chroma_client()
        collection = client.get_collection(get_collection_name(1))
        count = collection.count()
        print(f"   - Documentos na coleção: {count}")
    else:
        print(f"   ❌ Falha ao gerar embeddings")
        
except Exception as e:
    print(f"\n❌ ERRO: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 60)
