"""
Testes unitários para ConfiancaService
"""
import pytest
from langchain_core.documents import Document
from app.services.confianca import ConfiancaService


class TestCalcularConfianca:
    """Testes para cálculo de confiança"""
    
    def test_calcular_confianca_alta(self):
        """Teste com alta confiança - documentos relevantes e resposta completa"""
        query = "qual o horário de funcionamento"
        documentos = [
            Document(
                page_content="Horário de funcionamento: Segunda a Sexta, 9h às 18h",
                metadata={'score': 0.9}
            ),
            Document(
                page_content="Estamos abertos de 9h às 18h nos dias úteis",
                metadata={'score': 0.85}
            )
        ]
        resposta = "Nosso horário de funcionamento é de segunda a sexta, das 9h às 18h."
        
        score = ConfiancaService.calcular_confianca(query, documentos, resposta)
        
        assert score >= 0.7, f"Score deveria ser >= 0.7, mas foi {score}"
        assert score <= 1.0, f"Score deveria ser <= 1.0, mas foi {score}"
    
    def test_calcular_confianca_baixa_sem_documentos(self):
        """Teste com baixa confiança - sem documentos"""
        query = "qual o horário de funcionamento"
        documentos = []
        resposta = "Não sei informar"
        
        score = ConfiancaService.calcular_confianca(query, documentos, resposta)
        
        assert score < 0.5, f"Score deveria ser < 0.5, mas foi {score}"
    
    def test_calcular_confianca_baixa_resposta_curta(self):
        """Teste com baixa confiança - resposta muito curta"""
        query = "qual o horário de funcionamento"
        documentos = [
            Document(page_content="Horário: 9h-18h", metadata={'score': 0.8})
        ]
        resposta = "Não sei"
        
        score = ConfiancaService.calcular_confianca(query, documentos, resposta)
        
        assert score < 0.6, f"Score deveria ser < 0.6, mas foi {score}"
    
    def test_calcular_confianca_media(self):
        """Teste com confiança média"""
        query = "como funciona o sistema"
        documentos = [
            Document(page_content="O sistema funciona assim...", metadata={'score': 0.6})
        ]
        resposta = "O sistema é bem simples de usar e funciona de forma automática."
        
        score = ConfiancaService.calcular_confianca(query, documentos, resposta)
        
        assert 0.4 <= score <= 0.8, f"Score deveria estar entre 0.4 e 0.8, mas foi {score}"
    
    def test_calcular_confianca_resposta_muito_longa(self):
        """Teste com resposta muito longa - penaliza score"""
        query = "qual o horário"
        documentos = [
            Document(page_content="Horário: 9h-18h", metadata={'score': 0.9})
        ]
        resposta = "A" * 1000  # Resposta muito longa
        
        score = ConfiancaService.calcular_confianca(query, documentos, resposta)
        
        # Score deve ser penalizado pelo tamanho
        assert score < 0.9, f"Score deveria ser penalizado, mas foi {score}"


class TestDeveAcionarFallback:
    """Testes para decisão de fallback"""
    
    def test_deve_acionar_fallback_score_baixo(self):
        """Deve acionar fallback quando score < threshold"""
        score = 0.5
        threshold = 0.6
        
        resultado = ConfiancaService.deve_acionar_fallback(score, threshold)
        
        assert resultado is True
    
    def test_nao_deve_acionar_fallback_score_alto(self):
        """Não deve acionar fallback quando score >= threshold"""
        score = 0.7
        threshold = 0.6
        
        resultado = ConfiancaService.deve_acionar_fallback(score, threshold)
        
        assert resultado is False
    
    def test_deve_acionar_fallback_score_igual_threshold(self):
        """Não deve acionar fallback quando score == threshold"""
        score = 0.6
        threshold = 0.6
        
        resultado = ConfiancaService.deve_acionar_fallback(score, threshold)
        
        assert resultado is False
    
    def test_threshold_customizado(self):
        """Testa com threshold customizado"""
        score = 0.5
        threshold = 0.4
        
        resultado = ConfiancaService.deve_acionar_fallback(score, threshold)
        
        assert resultado is False  # Score acima do threshold customizado


class TestDetectarSolicitacaoHumano:
    """Testes para detecção de solicitação de humano"""
    
    def test_detectar_falar_com_humano(self):
        """Detecta 'falar com humano'"""
        mensagem = "Quero falar com humano"
        
        resultado = ConfiancaService.detectar_solicitacao_humano(mensagem)
        
        assert resultado is True
    
    def test_detectar_falar_com_atendente(self):
        """Detecta 'falar com atendente'"""
        mensagem = "Preciso falar com um atendente"
        
        resultado = ConfiancaService.detectar_solicitacao_humano(mensagem)
        
        assert resultado is True
    
    def test_detectar_pessoa_real(self):
        """Detecta 'pessoa real'"""
        mensagem = "Quero falar com uma pessoa real"
        
        resultado = ConfiancaService.detectar_solicitacao_humano(mensagem)
        
        assert resultado is True
    
    def test_detectar_nao_quero_robo(self):
        """Detecta 'não quero robô'"""
        mensagem = "Não quero robô, quero pessoa"
        
        resultado = ConfiancaService.detectar_solicitacao_humano(mensagem)
        
        assert resultado is True
    
    def test_nao_detectar_mensagem_normal(self):
        """Não detecta em mensagem normal"""
        mensagem = "Qual o horário de funcionamento?"
        
        resultado = ConfiancaService.detectar_solicitacao_humano(mensagem)
        
        assert resultado is False
    
    def test_nao_detectar_mensagem_com_palavra_similar(self):
        """Não detecta falso positivo"""
        mensagem = "Gostaria de saber sobre o atendimento online"
        
        resultado = ConfiancaService.detectar_solicitacao_humano(mensagem)
        
        assert resultado is False
    
    def test_detectar_case_insensitive(self):
        """Detecta independente de maiúsculas/minúsculas"""
        mensagem = "QUERO FALAR COM HUMANO"
        
        resultado = ConfiancaService.detectar_solicitacao_humano(mensagem)
        
        assert resultado is True
    
    def test_detectar_no_meio_da_frase(self):
        """Detecta palavra-chave no meio da frase"""
        mensagem = "Olá, eu gostaria de falar com um atendente humano por favor"
        
        resultado = ConfiancaService.detectar_solicitacao_humano(mensagem)
        
        assert resultado is True
