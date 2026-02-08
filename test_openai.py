"""
Teste simples de conexão com OpenAI
"""
import os
print(f"OPENAI_API_KEY definida: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"Primeiros 20 chars: {os.getenv('OPENAI_API_KEY', '')[:20]}...")

try:
    from langchain_openai import OpenAIEmbeddings
    print("\n✅ OpenAIEmbeddings importado com sucesso")
    
    embeddings = OpenAIEmbeddings()
    print("✅ OpenAIEmbeddings instanciado")
    
    # Testar embedding simples
    print("\n🔄 Testando embedding de texto simples...")
    result = embeddings.embed_query("teste")
    print(f"✅ Embedding gerado! Dimensão: {len(result)}")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
