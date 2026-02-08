import chromadb
from chromadb.config import Settings

try:
    client = chromadb.HttpClient(host='chromadb', port=8000, settings=Settings(anonymized_telemetry=False))
    collection = client.get_collection(name='cliente_1_conhecimento')
    
    print('✅ Coleção encontrada!')
    print(f'📦 Total de chunks: {collection.count()}')
    
    # Buscar alguns chunks
    results = collection.get(limit=3, include=['documents', 'metadatas'])
    
    print('\n📋 Primeiros 3 chunks:\n')
    for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas'])):
        print(f'--- Chunk {i+1} ---')
        print(f'Tipo: {meta.get("tipo")}')
        print(f'Categoria: {meta.get("categoria")}')
        print(f'Texto: {doc[:100]}...')
        print()
        
except Exception as e:
    print(f'❌ Erro: {e}')
