import chromadb
from chromadb.config import Settings

# Conectar ao ChromaDB (usando hostname do Docker)
client = chromadb.HttpClient(
    host="chromadb",
    port=8000,
    settings=Settings(anonymized_telemetry=False)
)

# Listar todas as coleções
collections = client.list_collections()
print(f"Total de coleções: {len(collections)}")
print()

for col in collections:
    print(f"Coleção: {col.name}")
    print(f"  - Count: {col.count()}")
    
    # Se for a coleção do cliente 1, mostrar alguns documentos
    if col.name == "tenant_1":
        print(f"  - Metadata: {col.metadata}")
        
        # Pegar alguns documentos
        if col.count() > 0:
            results = col.get(limit=3)
            print(f"  - Primeiros documentos:")
            for i, doc in enumerate(results['documents']):
                print(f"    {i+1}. {doc[:100]}...")
    print()
