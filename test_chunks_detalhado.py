import chromadb
from chromadb.config import Settings

try:
    client = chromadb.HttpClient(host='chromadb', port=8000, settings=Settings(anonymized_telemetry=False))
    collection = client.get_collection(name='cliente_1_conhecimento')
    
    print(f'📦 Total de chunks: {collection.count()}\n')
    
    # Buscar todos os chunks
    results = collection.get(include=['documents', 'metadatas'])
    
    # Agrupar por tipo
    chunks_por_tipo = {}
    for doc, meta in zip(results['documents'], results['metadatas']):
        tipo = meta.get('tipo', 'desconhecido')
        if tipo not in chunks_por_tipo:
            chunks_por_tipo[tipo] = []
        chunks_por_tipo[tipo].append({
            'categoria': meta.get('categoria'),
            'nome': meta.get('nome'),
            'texto': doc[:80]
        })
    
    # Mostrar resumo
    print('📊 RESUMO POR TIPO:\n')
    for tipo, chunks in sorted(chunks_por_tipo.items()):
        print(f'{tipo}: {len(chunks)} chunks')
        for chunk in chunks[:3]:  # Mostrar até 3 exemplos
            if chunk['nome']:
                print(f'  - {chunk["nome"]} ({chunk["categoria"]})')
            else:
                print(f'  - {chunk["categoria"]}')
        if len(chunks) > 3:
            print(f'  ... e mais {len(chunks) - 3}')
        print()
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
