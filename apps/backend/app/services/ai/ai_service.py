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
        tom: str = "casual",
        nome_empresa: str = None,
        primeira_mensagem: bool = False
    ) -> Dict:
        """
        Processa mensagem do usuário e gera resposta com IA
        
        Args:
            cliente_id: ID do cliente
            chat_id: ID do chat (session_id)
            mensagem: Mensagem do usuário
            tom: Tom das respostas (formal, casual, tecnico)
            nome_empresa: Nome da empresa para saudação
            primeira_mensagem: Se é a primeira mensagem da conversa
            
        Returns:
            Dict com 'resposta', 'contexto_usado', 'confianca'
        """
        logger.info(f"Processando mensagem para cliente {cliente_id}: '{mensagem[:50]}...'")
        
        # 1. Buscar contexto no vectorstore (RAG)
        contexto_docs = buscar_no_vectorstore(cliente_id, mensagem, k=5)
        
        if not contexto_docs or len(contexto_docs) == 0:
            logger.warning(f"Nenhum embedding encontrado para cliente {cliente_id} - usando conhecimento estruturado")
            
            # Fallback: buscar conhecimento direto do banco
            from app.db.session import SessionLocal
            from app.services.conhecimento import ConhecimentoService
            from app.services.conhecimento.estruturador_service import EstruturadorService
            
            db = SessionLocal()
            try:
                conhecimento = ConhecimentoService.buscar_ou_criar(db, cliente_id)
                
                # Priorizar JSON estruturado se existir
                if conhecimento.conteudo_estruturado:
                    logger.info(f"✅ Usando conhecimento estruturado (JSON)")
                    contexto_texto = EstruturadorService.json_para_texto_busca(conhecimento.conteudo_estruturado)
                    confianca = 0.7  # Confiança alta quando usa JSON estruturado
                elif conhecimento.conteudo_texto and len(conhecimento.conteudo_texto.strip()) > 0:
                    logger.info(f"⚠️ Usando texto direto (JSON não disponível)")
                    contexto_texto = conhecimento.conteudo_texto
                    confianca = 0.5  # Confiança média quando usa texto direto
                else:
                    contexto_texto = "Nenhum conhecimento disponível."
                    confianca = 0.0
                    
                logger.info(f"Usando conhecimento: {len(contexto_texto)} chars, confiança: {confianca}")
            finally:
                db.close()
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
        system_prompt = AIService._get_system_prompt(tom, contexto_texto, nome_empresa)
        
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
            
            # 6. Adicionar saudação se for primeira mensagem
            if primeira_mensagem:
                from datetime import datetime
                hora = datetime.now().hour
                
                if 5 <= hora < 12:
                    saudacao = "Bom dia"
                elif 12 <= hora < 18:
                    saudacao = "Boa tarde"
                else:
                    saudacao = "Boa noite"
                
                # Saudação simples sem nome da empresa
                resposta = f"{saudacao}! Como posso ajudar você?\n\n{resposta}"
            
            logger.info(f"Resposta gerada: '{resposta[:50]}...'")
            
            # 7. Salvar no histórico
            session_history.add_user_message(mensagem)
            session_history.add_ai_message(resposta)
            
            return {
                "resposta": resposta,
                "contexto_usado": len(contexto_docs),
                "confianca": confianca,
                "documentos": contexto_docs  # Adicionar documentos para cálculo de confiança
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            raise
    
    @staticmethod
    def _get_system_prompt(tom: str, contexto: str, nome_empresa: str = None) -> str:
        """
        Gera system prompt baseado no tom e contexto
        """
        tom_instrucoes = {
            "formal": "Você deve ser profissional, respeitoso e usar linguagem formal.",
            "casual": "Você deve ser amigável, descontraído e usar linguagem casual.",
            "tecnico": "Você deve ser preciso, técnico e usar terminologia especializada."
        }
        
        instrucao_tom = tom_instrucoes.get(tom, tom_instrucoes["casual"])
        
        return f"""Você é um assistente virtual de atendimento. {instrucao_tom}

REGRAS IMPORTANTES:

1. TOLERÂNCIA COM ERROS:
   - Seja tolerante com erros de digitação (ex: "queor" = "quero", "cachoro" = "cachorro")
   - Tente entender a INTENÇÃO da mensagem, não apenas as palavras exatas
   - Se entender a intenção, responda normalmente

2. SAUDAÇÕES E MENSAGENS GERAIS:
   - Se a pessoa apenas cumprimentar (oi, olá, bom dia, boa tarde, e aí, etc), responda de forma amigável e pergunte como pode ajudar
   - Exemplo: "Olá! Como posso ajudar você hoje?"
   - Seja natural e receptivo

3. PERGUNTAS ESPECÍFICAS:
   - Para perguntas sobre produtos/serviços, responda APENAS com base no conhecimento abaixo
   - Se você REALMENTE não souber ou a informação não estiver no conhecimento, responda EXATAMENTE: "Não tenho essa informação no momento."
   - IMPORTANTE: Use essa frase exata para que possamos transferir para um atendente humano
   
4. PERGUNTAS FORA DO ESCOPO:
   - Para perguntas não relacionadas ao negócio (hora, tempo, notícias, etc), responda: "Desculpe, só posso ajudar com informações sobre nossos serviços."

5. ESTILO:
   - Seja conciso (máximo 3 frases)
   - Seja amigável e prestativo
   - Não invente informações

CONHECIMENTO DISPONÍVEL:
{contexto}

Responda de forma natural e útil."""
