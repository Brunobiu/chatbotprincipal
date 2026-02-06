"""
Service para processar mensagens com IA (RAG + LLM)
"""
import logging
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import settings
from app.services.rag.vectorstore import buscar_no_vectorstore
from app.services.conversations.memory import get_session_history

logger = logging.getLogger(__name__)


class AIService:
    """Service para processar mensagens com IA"""
    
    @staticmethod
    def processar_mensagem(
        cliente_id: int,
        chat_id: str,
        mensagem: str,
        tom: str = "casual"
    ) -> Dict:
        """
        Processa mensagem do usuário e gera resposta com IA
        
        Args:
            cliente_id: ID do cliente
            chat_id: ID do chat (session_id)
            mensagem: Mensagem do usuário
            tom: Tom das respostas (formal, casual, tecnico)
            
        Returns:
            Dict com 'resposta', 'contexto_usado', 'confianca'
        """
        logger.info(f"Processando mensagem para cliente {cliente_id}: '{mensagem[:50]}...'")
        
        # 1. Buscar contexto no vectorstore (RAG)
        contexto_docs = buscar_no_vectorstore(cliente_id, mensagem, k=5)
        
        if not contexto_docs:
            logger.warning(f"Nenhum contexto encontrado para cliente {cliente_id}")
            contexto_texto = "Nenhum conhecimento disponível."
            confianca = 0.0
        else:
            # Montar texto do contexto
            contexto_texto = "\n\n".join([
                f"[Trecho {i+1}]: {doc['text']}"
                for i, doc in enumerate(contexto_docs)
            ])
            
            # Calcular confiança média baseada nos scores
            scores = [doc['score'] for doc in contexto_docs]
            confianca = 1.0 - (sum(scores) / len(scores))  # Inverter score (menor = melhor)
            
            logger.info(f"Contexto encontrado: {len(contexto_docs)} chunks, confiança: {confianca:.2f}")
        
        # 2. Buscar histórico da conversa (últimas 10 mensagens)
        session_history = get_session_history(chat_id)
        historico_mensagens = session_history.messages[-10:] if session_history.messages else []
        
        logger.info(f"Histórico: {len(historico_mensagens)} mensagens")
        
        # 3. Montar prompt baseado no tom
        system_prompt = AIService._get_system_prompt(tom, contexto_texto)
        
        # 4. Montar mensagens para o LLM
        messages = [SystemMessage(content=system_prompt)]
        
        # Adicionar histórico
        for msg in historico_mensagens:
            messages.append(msg)
        
        # Adicionar mensagem atual
        messages.append(HumanMessage(content=mensagem))
        
        # 5. Chamar OpenAI
        try:
            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL_NAME,
                temperature=float(settings.OPENAI_MODEL_TEMPERATURE)
            )
            
            response = llm.invoke(messages)
            resposta = response.content
            
            logger.info(f"Resposta gerada: '{resposta[:50]}...'")
            
            # 6. Salvar no histórico
            session_history.add_user_message(mensagem)
            session_history.add_ai_message(resposta)
            
            return {
                "resposta": resposta,
                "contexto_usado": len(contexto_docs),
                "confianca": confianca
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            raise
    
    @staticmethod
    def _get_system_prompt(tom: str, contexto: str) -> str:
        """
        Gera system prompt baseado no tom e contexto
        """
        tom_instrucoes = {
            "formal": "Você deve ser profissional, respeitoso e usar linguagem formal.",
            "casual": "Você deve ser amigável, descontraído e usar linguagem casual.",
            "tecnico": "Você deve ser preciso, técnico e usar terminologia especializada."
        }
        
        instrucao_tom = tom_instrucoes.get(tom, tom_instrucoes["casual"])
        
        return f"""Você é um assistente virtual inteligente. {instrucao_tom}

IMPORTANTE:
- Responda APENAS com base no conhecimento fornecido abaixo
- Se a informação não estiver no conhecimento, diga que não sabe
- Seja conciso e direto
- Não invente informações

CONHECIMENTO DISPONÍVEL:
{contexto}

Responda à pergunta do usuário usando apenas as informações acima."""
