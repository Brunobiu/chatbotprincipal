"""
Chains do LangChain com suporte a multi-tenant
"""
import logging
from typing import Optional

from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from app.core.config import (
    OPENAI_MODEL_NAME,
    OPENAI_MODEL_TEMPERATURE,
)
from app.services.conversations.memory import get_session_history
from app.services.rag.vectorstore import get_vectorstore
from app.services.llm.prompts import contextualize_prompt, qa_prompt

logger = logging.getLogger(__name__)


def get_rag_chain(cliente_id: Optional[int] = None):
    """
    Cria RAG chain para um cliente específico
    
    Args:
        cliente_id: ID do cliente (para isolamento multi-tenant)
        
    Returns:
        RAG chain configurada
    """
    llm = ChatOpenAI(
        model=OPENAI_MODEL_NAME,
        temperature=OPENAI_MODEL_TEMPERATURE,
    )
    
    # Obter vectorstore do cliente específico
    vectorstore = get_vectorstore(cliente_id)
    retriever = vectorstore.as_retriever()
    
    if cliente_id:
        logger.info(f"RAG chain criada para cliente {cliente_id}")
    
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_prompt)
    question_answer_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=qa_prompt,
    )
    return create_retrieval_chain(history_aware_retriever, question_answer_chain)


def get_conversational_rag_chain(cliente_id: Optional[int] = None):
    """
    Cria conversational RAG chain para um cliente específico
    
    Args:
        cliente_id: ID do cliente (para isolamento multi-tenant)
        
    Returns:
        Conversational RAG chain configurada
    """
    rag_chain = get_rag_chain(cliente_id)
    return RunnableWithMessageHistory(
        runnable=rag_chain,
        get_session_history=get_session_history,
        input_messages_key='input',
        history_messages_key='chat_history',
        output_messages_key='answer',
    )
