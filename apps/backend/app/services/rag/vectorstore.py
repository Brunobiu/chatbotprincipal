"""
Serviço de Vectorstore com suporte a multi-tenant
Cada cliente tem sua própria coleção isolada no ChromaDB
"""
import os
import shutil
import logging
from typing import Optional

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.core.config import RAG_FILES_DIR, VECTOR_STORE_PATH

logger = logging.getLogger(__name__)


def get_collection_name(cliente_id: int) -> str:
    """
    Retorna o nome da coleção para um cliente específico
    
    Args:
        cliente_id: ID do cliente
        
    Returns:
        Nome da coleção no formato tenant_{cliente_id}
    """
    return f"tenant_{cliente_id}"


def load_documents(cliente_id: Optional[int] = None):
    """
    Carrega documentos da pasta RAG_FILES_DIR
    Se cliente_id for fornecido, procura em RAG_FILES_DIR/cliente_{id}/
    
    Args:
        cliente_id: ID do cliente (opcional)
        
    Returns:
        Lista de documentos carregados
    """
    docs = []
    
    # Determinar diretório base
    if cliente_id:
        base_dir = os.path.join(RAG_FILES_DIR, f'cliente_{cliente_id}')
    else:
        base_dir = RAG_FILES_DIR
    
    if not os.path.exists(base_dir):
        logger.warning(f"Diretório não encontrado: {base_dir}")
        return docs
    
    processed_dir = os.path.join(base_dir, 'processed')
    os.makedirs(processed_dir, exist_ok=True)

    files = [
        os.path.join(base_dir, f)
        for f in os.listdir(base_dir)
        if f.endswith('.pdf') or f.endswith('.txt')
    ]

    for file in files:
        try:
            loader = PyPDFLoader(file) if file.endswith('.pdf') else TextLoader(file)
            docs.extend(loader.load())
            dest_path = os.path.join(processed_dir, os.path.basename(file))
            shutil.move(file, dest_path)
            logger.info(f"Documento processado: {os.path.basename(file)}")
        except Exception as e:
            logger.error(f"Erro ao processar {file}: {str(e)}")

    return docs


def get_vectorstore(cliente_id: Optional[int] = None):
    """
    Retorna vectorstore para um cliente específico
    Se cliente_id não for fornecido, usa coleção padrão (legado)
    
    Args:
        cliente_id: ID do cliente
        
    Returns:
        Instância do Chroma vectorstore
    """
    # Determinar nome da coleção
    if cliente_id:
        collection_name = get_collection_name(cliente_id)
        logger.info(f"Usando coleção: {collection_name}")
    else:
        collection_name = "default"
        logger.warning("Usando coleção padrão (não recomendado para multi-tenant)")
    
    # Carregar documentos (se houver novos)
    docs = load_documents(cliente_id)
    
    if docs:
        logger.info(f"Processando {len(docs)} documentos para cliente {cliente_id}")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Reduzido de 1000 para melhor precisão
            chunk_overlap=160,  # 20% de overlap
        )
        splits = text_splitter.split_documents(docs)
        logger.info(f"Criados {len(splits)} chunks")
        
        return Chroma.from_documents(
            documents=splits,
            embedding=OpenAIEmbeddings(),
            persist_directory=VECTOR_STORE_PATH,
            collection_name=collection_name,
        )
    
    # Retornar vectorstore existente
    return Chroma(
        embedding_function=OpenAIEmbeddings(),
        persist_directory=VECTOR_STORE_PATH,
        collection_name=collection_name,
    )


def criar_vectorstore_cliente(cliente_id: int, documentos: list) -> Chroma:
    """
    Cria ou atualiza vectorstore para um cliente específico
    
    Args:
        cliente_id: ID do cliente
        documentos: Lista de documentos (strings ou Documents)
        
    Returns:
        Instância do Chroma vectorstore
    """
    collection_name = get_collection_name(cliente_id)
    logger.info(f"Criando/atualizando vectorstore para cliente {cliente_id}")
    
    # Processar documentos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=160,
    )
    
    if isinstance(documentos[0], str):
        # Se são strings, criar Documents
        from langchain_core.documents import Document
        docs = [Document(page_content=doc) for doc in documentos]
    else:
        docs = documentos
    
    splits = text_splitter.split_documents(docs)
    logger.info(f"Criados {len(splits)} chunks para cliente {cliente_id}")
    
    # Criar vectorstore
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings(),
        persist_directory=VECTOR_STORE_PATH,
        collection_name=collection_name,
    )
    
    return vectorstore


def deletar_vectorstore_cliente(cliente_id: int):
    """
    Deleta vectorstore de um cliente específico
    
    Args:
        cliente_id: ID do cliente
    """
    collection_name = get_collection_name(cliente_id)
    logger.info(f"Deletando vectorstore do cliente {cliente_id}")
    
    try:
        # Criar instância temporária para deletar
        vectorstore = Chroma(
            embedding_function=OpenAIEmbeddings(),
            persist_directory=VECTOR_STORE_PATH,
            collection_name=collection_name,
        )
        vectorstore.delete_collection()
        logger.info(f"Vectorstore do cliente {cliente_id} deletado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao deletar vectorstore do cliente {cliente_id}: {str(e)}")
