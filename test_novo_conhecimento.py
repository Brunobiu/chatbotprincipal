import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(
    host='chromadb',
    port=8000,
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_collection(name='cliente_1_conhecimento')
count = collection.count()

print(f'🔢 Total de chunks: {count}\n')

# Pegar todos os chunks
results = collection.get(include=['documents', 'metadatas'])

# Agrupar por tipo
tipos = {}
for doc, meta in zip(results['documents'], results['metadatas']):
    tipo = meta.get('tipo', 'desconhecido')
    if tipo not in tipos:
        tipos[tipo] = []
    tipos[tipo].append({
        'doc': doc,
        'meta': meta
    })

print('📊 Chunks por tipo:')
print('=' * 80)

for tipo, chunks in sorted(tipos.items()):
    print(f'\n{tipo.upper()}: {len(chunks)} chunks')
    
    for i, chunk in enumerate(chunks[:3]):  # Mostrar até 3 de cada tipo
        meta = chunk['meta']
        doc = chunk['doc']
        
        print(f'\n  Chunk {i+1}:')
        if meta.get('categoria'):
            print(f'    Categoria: {meta["categoria"]}')
        if meta.get('nome'):
            print(f'    Nome: {meta["nome"]}')
        if meta.get('preco'):
            print(f'    Preço: R$ {meta["preco"]:.2f}')
        
        texto = doc[:150] if len(doc) > 150 else doc
        print(f'    Texto: {texto}...')
    
    if len(chunks) > 3:
        print(f'    ... e mais {len(chunks) - 3} chunks')

print('\n' + '=' * 80)
print(f'\n✅ Total: {count} chunks estruturados')
