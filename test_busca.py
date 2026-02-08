import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings

try:
    client = chromadb.HttpClient(host='chromadb', port=8000, settings=Settings(anonymized_telemetry=False))
    collection = client.get_collection(name='cliente_1_conhecimento')
    
    # Gerar embedding da query
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
    
    queries = [
        "quanto custa lavar um carro pequeno?",
        "qual o horário de funcionamento?",
        "vocês buscam em casa?"
    ]
    
    for query in queries:
        print(f'\n🔍 Busca: "{query}"')
        print('-' * 60)
        
        query_embedding = embeddings_model.embed_query(query)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=2,
            include=['documents', 'metadatas', 'distances']
        )
        
        for i, (doc, meta, dist) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
            print(f'\nResultado {i+1}:')
            print(f'  Tipo: {meta.get("tipo")}')
            print(f'  Categoria: {meta.get("categoria")}')
            print(f'  Distância: {dist:.4f}')
            print(f'  Texto: {doc[:120]}...')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
