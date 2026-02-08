"""
Serviço de Vectorstore com suporte a multi-tenant
Cada cliente tem sua própria coleção isolada no ChromaDB
"""
import logging
import time
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_chroma_client():
    """
    Retorna cliente ChromaDB configurado
    """
    return chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
        settings=Settings(anonymized_telemetry=False)
    )


def get_collection_name(cliente_id: int) -> str:
    """
    Retorna o nome da coleção para um cliente específico
    
    Args:
        cliente_id: ID do cliente
        
    Returns:
        Nome da coleção no formato tenant_{cliente_id}
    """
    return f"tenant_{cliente_id}"


def criar_vectorstore_de_chunks(cliente_id: int, chunks: List[Dict]) -> Chroma:
    """
    Cria vectorstore a partir de chunks de texto
    Apaga coleção antiga e cria nova
    Processa em lotes para evitar problemas de memória
    
    Args:
        cliente_id: ID do cliente
        chunks: Lista de dicts com 'text', 'start', 'end', 'index'
        
    Returns:
        Instância do Chroma vectorstore
    """
    collection_name = get_collection_name(cliente_id)
    logger.info(f"Criando vectorstore para cliente {cliente_id} com {len(chunks)} chunks")
    
    # Deletar coleção antiga se existir
    try:
        deletar_vectorstore_cliente(cliente_id)
    except Exception as e:
        logger.warning(f"Erro ao deletar coleção antiga: {e}")
    
    if not chunks:
        logger.warning(f"Nenhum chunk fornecido para cliente {cliente_id}")
        return None
    
    # Criar documentos a partir dos chunks
    documents = []
    for chunk in chunks:
        doc = Document(
            page_content=chunk['text'],
            metadata={
                'cliente_id': cliente_id,
                'chunk_index': chunk['index'],
                'start': chunk['start'],
                'end': chunk['end']
            }
        )
        documents.append(doc)
    
    # Criar vectorstore com ChromaDB via HTTP
    client = get_chroma_client()
    
    # Processar em lotes de 5 documentos para evitar problemas de memória
    batch_size = 5
    vectorstore = None
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        logger.info(f"Processando lote {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1} ({len(batch)} docs)")
        
        if vectorstore is None:
            # Primeiro lote - criar vectorstore
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=OpenAIEmbeddings(),
                client=client,
                collection_name=collection_name,
            )
        else:
            # Lotes seguintes - adicionar à coleção existente
            vectorstore.add_documents(batch)
        
        # Pequeno delay entre lotes para evitar sobrecarga
        if i + batch_size < len(documents):
            time.sleep(0.5)
    
    logger.info(f"Vectorstore criado com sucesso para cliente {cliente_id}")
    return vectorstore


def buscar_no_vectorstore(cliente_id: int, query: str, k: int = 5) -> List[Dict]:
    """
    Busca documentos relevantes no vectorstore do cliente
    
    Args:
        cliente_id: ID do cliente
        query: Texto da busca
        k: Número de resultados
        
    Returns:
        Lista de dicts com 'text', 'score', 'metadata'
    """
    collection_name = get_collection_name(cliente_id)
    logger.info(f"Buscando no vectorstore do cliente {cliente_id}: '{query}'")
    
    try:
        client = get_chroma_client()
        
        vectorstore = Chroma(
            embedding_function=OpenAIEmbeddings(),
            client=client,
            collection_name=collection_name,
        )
        
        # Buscar com scores
        results = vectorstore.similarity_search_with_score(query, k=k)
        
        # Formatar resultados
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'text': doc.page_content,
                'score': float(score),
                'metadata': doc.metadata
            })
        
        logger.info(f"Encontrados {len(formatted_results)} resultados")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Erro ao buscar no vectorstore: {e}")
        return []


def deletar_vectorstore_cliente(cliente_id: int):
    """
    Deleta vectorstore de um cliente específico
    
    Args:
        cliente_id: ID do cliente
    """
    collection_name = get_collection_name(cliente_id)
    logger.info(f"Deletando vectorstore do cliente {cliente_id}")
    
    try:
        client = get_chroma_client()
        client.delete_collection(name=collection_name)
        logger.info(f"Vectorstore do cliente {cliente_id} deletado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao deletar vectorstore do cliente {cliente_id}: {str(e)}")
