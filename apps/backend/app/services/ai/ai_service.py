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
from app.db.models.ia_configuracao import IAConfiguracao

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
        primeira_mensagem: bool = False,
        nome_usuario: str = None
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
            nome_usuario: Nome do usuário (se conhecido)
            
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
        system_prompt = AIService._get_system_prompt(tom, contexto_texto, nome_empresa, nome_usuario)
        
        # 4. Montar mensagens para o LLM
        messages = [SystemMessage(content=system_prompt)]
        
        # Adicionar histórico
        for msg in historico_mensagens:
            messages.append(msg)
        
        # Adicionar mensagem atual
        messages.append(HumanMessage(content=mensagem))
        
        # 5. Chamar IA com fallback automático
        try:
            from app.db.session import SessionLocal
            from app.services.ia_config_service import IAConfigService
            
            # Buscar TODOS os provedores configurados (ordenados por prioridade)
            db_config = SessionLocal()
            try:
                # Buscar provedor ativo
                config_ativa = IAConfigService.get_api_key_ativa(db_config)
                
                # Buscar todos configurados como backup
                todos_configs = db_config.query(IAConfiguracao).filter_by(configurado=True).all()
                
                # Ordenar: ativo primeiro, depois os outros
                configs_ordenadas = []
                if config_ativa:
                    configs_ordenadas.append(config_ativa)
                
                for cfg in todos_configs:
                    provedor_cfg = (cfg.provedor, cfg.modelo, IAConfigService.decrypt_key(cfg.api_key_encrypted))
                    if config_ativa and cfg.provedor == config_ativa[0]:
                        continue  # Já adicionou
                    configs_ordenadas.append(provedor_cfg)
                
            finally:
                db_config.close()
            
            # Tentar cada provedor até funcionar
            ultima_exception = None
            
            for idx, config in enumerate(configs_ordenadas):
                provedor, modelo, api_key = config
                
                try:
                    if idx == 0:
                        logger.info(f"🤖 Tentando {provedor} ({modelo}) - Provedor ativo")
                    else:
                        logger.warning(f"🔄 Fallback: Tentando {provedor} ({modelo})")
                    
                    # Usar provedor
                    if provedor == 'openai':
                        llm = ChatOpenAI(
                            model=modelo,
                            temperature=float(settings.OPENAI_MODEL_TEMPERATURE),
                            openai_api_key=api_key
                        )
                    else:
                        # Outros provedores ainda não implementados
                        continue
                    
                    # Tentar gerar resposta
                    response = llm.invoke(messages)
                    resposta = response.content
                    
                    # ✅ Sucesso! Sair do loop
                    if idx > 0:
                        logger.info(f"✅ Fallback bem-sucedido! Usando {provedor}")
                    break
                    
                except Exception as e:
                    ultima_exception = e
                    error_msg = str(e).lower()
                    
                    # Detectar erros de limite/quota
                    if any(x in error_msg for x in ['rate limit', 'quota', 'insufficient', 'exceeded']):
                        logger.error(f"❌ {provedor} atingiu limite: {e}")
                        # Tentar próximo
                        continue
                    else:
                        # Outro tipo de erro, tentar próximo também
                        logger.error(f"❌ Erro em {provedor}: {e}")
                        continue
            
            # Se nenhum funcionou, tentar .env como último recurso
            if 'resposta' not in locals():
                logger.warning(f"⚠️ Todos os provedores falharam, tentando .env como último recurso")
                try:
                    llm = ChatOpenAI(
                        model=settings.OPENAI_MODEL_NAME,
                        temperature=float(settings.OPENAI_MODEL_TEMPERATURE)
                    )
                    response = llm.invoke(messages)
                    resposta = response.content
                    logger.info(f"✅ Fallback .env bem-sucedido!")
                except Exception as e:
                    logger.error(f"❌ Até o .env falhou: {e}")
                    raise ultima_exception or e
            
            # 📊 REGISTRAR USO DA OPENAI (FASE 16.4)
            try:
                from app.db.session import SessionLocal
                from app.services.uso import UsoOpenAIService
                
                # Extrair tokens da resposta
                tokens_prompt = response.response_metadata.get('token_usage', {}).get('prompt_tokens', 0)
                tokens_completion = response.response_metadata.get('token_usage', {}).get('completion_tokens', 0)
                
                if tokens_prompt > 0 or tokens_completion > 0:
                    db = SessionLocal()
                    try:
                        UsoOpenAIService.registrar_uso(
                            db=db,
                            cliente_id=cliente_id,
                            modelo=settings.OPENAI_MODEL_NAME,
                            tokens_prompt=tokens_prompt,
                            tokens_completion=tokens_completion
                        )
                    finally:
                        db.close()
            except Exception as e:
                logger.error(f"Erro ao registrar uso OpenAI: {e}")
                # Não falhar a requisição por erro no registro
            
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
    def _get_system_prompt(tom: str, contexto: str, nome_empresa: str = None, nome_usuario: str = None) -> str:
        """
        Gera system prompt baseado no tom e contexto
        """
        tom_instrucoes = {
            "formal": "Você deve ser profissional, respeitoso e usar linguagem formal.",
            "casual": "Você deve ser amigável, descontraído e usar linguagem casual.",
            "tecnico": "Você deve ser preciso, técnico e usar terminologia especializada."
        }
        
        instrucao_tom = tom_instrucoes.get(tom, tom_instrucoes["casual"])
        
        # Adicionar instrução sobre uso do nome
        instrucao_nome = ""
        if nome_usuario:
            instrucao_nome = f"\n\nIMPORTANTE: O nome do usuário é {nome_usuario}. Use o nome dele nas respostas de forma natural e amigável."
        
        return f"""Você é um assistente virtual de atendimento. {instrucao_tom}{instrucao_nome}

REGRAS IMPORTANTES:

1. TOLERÂNCIA COM ERROS:
   - Seja tolerante com erros de digitação (ex: "queor" = "quero", "cachoro" = "cachorro")
   - Tente entender a INTENÇÃO da mensagem, não apenas as palavras exatas
   - Se entender a intenção, responda normalmente

2. SAUDAÇÕES E MENSAGENS GERAIS:
   - Se a pessoa apenas cumprimentar (oi, olá, bom dia, boa tarde, e aí, etc), responda de forma amigável e pergunte como pode ajudar
   - Exemplo: "Olá{', ' + nome_usuario if nome_usuario else ''}! Como posso ajudar você hoje?"
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

    @staticmethod
    def melhorar_conhecimento(texto: str) -> str:
        """
        Usa IA para estruturar e melhorar texto do conhecimento
        
        Args:
            texto: Texto bruto do conhecimento
            
        Returns:
            Texto estruturado e melhorado
        """
        logger.info(f"🤖 Melhorando conhecimento com IA: {len(texto)} chars")
        
        try:
            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0.3,  # Baixa temperatura para respostas mais consistentes
                api_key=settings.OPENAI_API_KEY
            )
            
            system_prompt = """Você é um assistente especializado em estruturar e melhorar textos de conhecimento para chatbots.

Sua tarefa é:
1. Organizar o texto em tópicos claros e bem estruturados
2. Corrigir erros de português
3. Melhorar a clareza e objetividade
4. Adicionar formatação com marcadores e subtítulos quando apropriado
5. Manter TODAS as informações importantes do texto original
6. NÃO inventar informações que não estão no texto original

Formato de saída:
- Use títulos em MAIÚSCULAS para seções principais
- Use marcadores (•) para listas
- Seja conciso mas completo
- Mantenha um tom profissional mas acessível

Exemplo de estrutura:

SOBRE A EMPRESA
• Informação 1
• Informação 2

PRODUTOS E SERVIÇOS
• Produto 1: descrição
• Produto 2: descrição

HORÁRIOS E CONTATO
• Horário: informação
• Telefone: informação
• Email: informação

POLÍTICAS
• Política 1
• Política 2"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Melhore e estruture este texto:\n\n{texto}")
            ]
            
            response = llm.invoke(messages)
            texto_melhorado = response.content
            
            logger.info(f"✅ Texto melhorado: {len(texto_melhorado)} chars")
            
            return texto_melhorado
            
        except Exception as e:
            logger.error(f"❌ Erro ao melhorar conhecimento: {str(e)}", exc_info=True)
            raise
