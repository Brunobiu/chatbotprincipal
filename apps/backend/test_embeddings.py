import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(host='chromadb', port=8000, settings=Settings(anonymized_telemetry=False))
collection = client.get_collection(name='cliente_1_conhecimento')

print(f'📦 Total de chunks: {collection.count()}')
print('\n📋 Primeiros 5 chunks:\n')

results = collection.get(limit=5, include=['documents', 'metadatas'])

for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas'])):
    print(f'--- Chunk {i+1} ---')
    print(f'Tipo: {meta.get("tipo")}')
    print(f'Categoria: {meta.get("categoria")}')
    print(f'Texto: {doc[:120]}...\n')
