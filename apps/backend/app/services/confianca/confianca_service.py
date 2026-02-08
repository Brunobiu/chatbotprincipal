"""
Service para calcular confiança nas respostas da IA e detectar necessidade de fallback
"""
import logging
from typing import List, Optional
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class ConfiancaService:
    """Service para gerenciar confiança e fallback"""
    
    # Palavras-chave para detectar solicitação de atendimento humano
    PALAVRAS_CHAVE_HUMANO = [
        "falar com humano",
        "falar com atendente",
        "falar com um atendente",
        "falar com pessoa",
        "atendente humano",
        "pessoa real",
        "quero falar com alguém",
        "preciso de ajuda humana",
        "transferir para humano",
        "não quero robô",
        "quero pessoa",
        "atendimento humano",
        "falar com gente",
        "preciso de uma pessoa",
        "quero um humano",
        "falar com alguém",
        "atendente real"
    ]
    
    @staticmethod
    def calcular_confianca(
        query: str,
        documentos: List[Document],
        resposta: str
    ) -> float:
        """
        Calcula score de confiança baseado em múltiplos fatores
        
        Args:
            query: Pergunta do usuário
            documentos: Documentos recuperados do RAG
            resposta: Resposta gerada pela IA
            
        Returns:
            float: Score entre 0.0 e 1.0
        """
        # DETECÇÃO DE RESPOSTAS DE DESCONHECIMENTO
        # Se o bot responde que não sabe, score = 0.0 (aciona fallback)
        respostas_desconhecimento = [
            "não sei",
            "nao sei",
            "não tenho",
            "nao tenho",
            "não possuo",
            "nao possuo",
            "desconheço",
            "não conheço",
            "nao conheco",
            "não tenho essa informação",
            "nao tenho essa informacao",
            "não tenho certeza",
            "nao tenho certeza",
            "não tenho informação",
            "nao tenho informacao"
        ]
        
        resposta_lower = resposta.lower().strip()
        for frase in respostas_desconhecimento:
            if frase in resposta_lower:
                logger.warning(f"⚠️ Resposta de desconhecimento detectada: '{frase}' na resposta '{resposta[:50]}' - Score = 0.0")
                return 0.0
        
        # DETECÇÃO DE SAUDAÇÕES E MENSAGENS GERAIS
        # Saudações devem ter score alto (0.9) pois são conversas naturais
        saudacoes = [
            "olá", "ola", "oi", "bom dia", "boa tarde", "boa noite",
            "hey", "e aí", "e ai", "tudo bem", "como vai", "opa"
        ]
        
        query_lower = query.lower().strip()
        eh_saudacao = any(saudacao in query_lower for saudacao in saudacoes)
        
        if eh_saudacao and len(resposta) > 20:
            logger.info(f"✅ Saudação detectada - Score alto: 0.9")
            return 0.9
        
        scores = []
        
        # 1. Similaridade média dos documentos (peso: 0.4 se tem docs, 0.0 se não tem)
        if documentos:
            similarity_scores = [
                doc.metadata.get('score', 0.5) 
                for doc in documentos
            ]
            avg_similarity = sum(similarity_scores) / len(similarity_scores)
            scores.append(('similarity', avg_similarity, 0.4))
            logger.debug(f"Similaridade média: {avg_similarity:.2f}")
        else:
            # Sem documentos, não penalizar - usar score neutro
            scores.append(('similarity', 0.6, 0.4))
            logger.debug("Nenhum documento encontrado - usando score neutro: 0.6")
        
        # 2. Presença de palavras-chave da query na resposta (peso: 0.2)
        query_words = set(query.lower().split())
        resposta_words = set(resposta.lower().split())
        
        # Remover palavras comuns (stopwords básicas)
        stopwords = {'o', 'a', 'de', 'da', 'do', 'em', 'para', 'com', 'por', 'e', 'ou'}
        query_words = query_words - stopwords
        
        if query_words:
            keyword_overlap = len(query_words & resposta_words) / len(query_words)
            scores.append(('keywords', keyword_overlap, 0.2))
            logger.debug(f"Overlap de palavras-chave: {keyword_overlap:.2f}")
        else:
            scores.append(('keywords', 0.5, 0.2))
        
        # 3. Tamanho e qualidade da resposta (peso: 0.4)
        # Respostas muito curtas (<20 chars) ou muito longas (>500 chars) têm score menor
        resposta_len = len(resposta)
        if 30 <= resposta_len <= 500:
            length_score = 1.0
        elif resposta_len < 30:
            length_score = resposta_len / 30
        else:
            length_score = max(0.6, 1.0 - (resposta_len - 500) / 1000)
        
        scores.append(('length', length_score, 0.4))
        logger.debug(f"Score de tamanho ({resposta_len} chars): {length_score:.2f}")
        
        # Calcular score final ponderado
        final_score = sum(score * weight for _, score, weight in scores)
        final_score = round(final_score, 2)
        
        logger.info(f"Score de confiança calculado: {final_score}")
        logger.debug(f"Detalhes: {scores}")
        
        return final_score
    
    @staticmethod
    def deve_acionar_fallback(score: float, threshold: float = 0.6) -> bool:
        """
        Verifica se deve acionar fallback baseado no score de confiança
        
        Args:
            score: Score de confiança (0.0 - 1.0)
            threshold: Threshold mínimo (padrão: 0.6)
            
        Returns:
            bool: True se deve acionar fallback
        """
        deve_acionar = score < threshold
        
        if deve_acionar:
            logger.warning(f"Score {score} abaixo do threshold {threshold} - acionando fallback")
        else:
            logger.info(f"Score {score} acima do threshold {threshold} - resposta confiável")
        
        return deve_acionar
    
    @staticmethod
    def detectar_solicitacao_humano(mensagem: str) -> bool:
        """
        Detecta se cliente está solicitando atendimento humano
        
        Args:
            mensagem: Mensagem do cliente
            
        Returns:
            bool: True se detectou solicitação de humano
        """
        mensagem_lower = mensagem.lower()
        
        for palavra_chave in ConfiancaService.PALAVRAS_CHAVE_HUMANO:
            if palavra_chave in mensagem_lower:
                logger.info(f"Solicitação de humano detectada: '{palavra_chave}'")
                return True
        
        return False
