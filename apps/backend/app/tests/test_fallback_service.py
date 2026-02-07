"""
Testes para FallbackService
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.services.fallback import FallbackService
from app.db.models.conversa import Conversa, MotivoFallback
from app.db.models.cliente import Cliente


class TestFallbackService:
    """Testes unitários para FallbackService"""
    
    def test_acionar_fallback_baixa_confianca(self, db_session):
        """Testa acionamento de fallback por baixa confiança"""
        # Criar cliente
        cliente = Cliente(
            nome="Cliente Teste",
            email="teste@teste.com",
            senha_hash="hash",
            status="ativo"
        )
        db_session.add(cliente)
        db_session.commit()
        
        # Acionar fallback
        with patch('app.services.fallback.fallback_service.send_whatsapp_message') as mock_send:
            FallbackService.acionar_fallback(
                db=db_session,
                numero_whatsapp="5511999999999",
                cliente_id=cliente.id,
                motivo=MotivoFallback.BAIXA_CONFIANCA,
                mensagem_fallback="Aguarde atendimento humano"
            )
        
        # Verificar conversa criada
        conversa = db_session.query(Conversa).filter(
            Conversa.cliente_id == cliente.id
        ).first()
        
        assert conversa is not None
        assert conversa.status == "aguardando_humano"
        assert conversa.motivo_fallback == "baixa_confianca"
        assert conversa.numero_whatsapp == "5511999999999"
        
        # Verificar mensagem enviada
        mock_send.assert_called_once_with(
            number="5511999999999",
            text="Aguarde atendimento humano"
        )
    
    def test_acionar_fallback_solicitacao_manual(self, db_session):
        """Testa acionamento de fallback por solicitação manual"""
        # Criar cliente
        cliente = Cliente(
            nome="Cliente Teste",
            email="teste@teste.com",
            senha_hash="hash",
            status="ativo"
        )
        db_session.add(cliente)
        db_session.commit()
        
        # Acionar fallback
        with patch('app.services.fallback.fallback_service.send_whatsapp_message') as mock_send:
            FallbackService.acionar_fallback(
                db=db_session,
                numero_whatsapp="5511999999999",
                cliente_id=cliente.id,
                motivo=MotivoFallback.SOLICITACAO_MANUAL,
                mensagem_fallback="Um humano irá atendê-lo"
            )
        
        # Verificar conversa criada
        conversa = db_session.query(Conversa).filter(
            Conversa.cliente_id == cliente.id
        ).first()
        
        assert conversa is not None
        assert conversa.status == "aguardando_humano"
        assert conversa.motivo_fallback == "solicitacao_manual"
        
        # Verificar mensagem enviada
        mock_send.assert_called_once()
    
    def test_assumir_conversa(self, db_session):
        """Testa assumir conversa por atendente"""
        # Criar cliente e conversa
        cliente = Cliente(
            nome="Cliente Teste",
            email="teste@teste.com",
            senha_hash="hash",
            status="ativo"
        )
        db_session.add(cliente)
        db_session.commit()
        
        conversa = Conversa(
            cliente_id=cliente.id,
            numero_whatsapp="5511999999999",
            status="aguardando_humano",
            motivo_fallback="baixa_confianca"
        )
        db_session.add(conversa)
        db_session.commit()
        
        # Assumir conversa
        with patch('app.services.fallback.fallback_service.send_whatsapp_message') as mock_send:
            FallbackService.assumir_conversa(
                db=db_session,
                conversa_id=conversa.id,
                atendente_email="atendente@teste.com"
            )
        
        # Verificar status atualizado
        db_session.refresh(conversa)
        assert conversa.status == "em_atendimento"
        assert conversa.atendente_email == "atendente@teste.com"
        
        # Verificar mensagem enviada
        mock_send.assert_called_once()
    
    def test_verificar_timeout_24h(self, db_session):
        """Testa verificação de timeout de 24h"""
        # Criar cliente
        cliente = Cliente(
            nome="Cliente Teste",
            email="teste@teste.com",
            senha_hash="hash",
            status="ativo"
        )
        db_session.add(cliente)
        db_session.commit()
        
        # Criar conversa antiga (mais de 24h)
        conversa_antiga = Conversa(
            cliente_id=cliente.id,
            numero_whatsapp="5511999999999",
            status="aguardando_humano",
            motivo_fallback="baixa_confianca",
            created_at=datetime.utcnow() - timedelta(hours=25)
        )
        db_session.add(conversa_antiga)
        
        # Criar conversa recente (menos de 24h)
        conversa_recente = Conversa(
            cliente_id=cliente.id,
            numero_whatsapp="5511888888888",
            status="aguardando_humano",
            motivo_fallback="solicitacao_manual",
            created_at=datetime.utcnow() - timedelta(hours=12)
        )
        db_session.add(conversa_recente)
        db_session.commit()
        
        # Verificar timeout
        with patch('app.services.fallback.fallback_service.send_whatsapp_message') as mock_send:
            conversas_retornadas = FallbackService.verificar_timeout_24h(db_session)
        
        # Verificar que apenas conversa antiga foi retornada
        assert len(conversas_retornadas) == 1
        assert conversas_retornadas[0].id == conversa_antiga.id
        
        # Verificar status atualizado
        db_session.refresh(conversa_antiga)
        db_session.refresh(conversa_recente)
        assert conversa_antiga.status == "ativa"
        assert conversa_recente.status == "aguardando_humano"
        
        # Verificar mensagem enviada apenas para conversa antiga
        assert mock_send.call_count == 1
    
    def test_notificar_humano(self, db_session):
        """Testa notificação de humano via email"""
        # Criar cliente com email de notificação
        cliente = Cliente(
            nome="Cliente Teste",
            email="teste@teste.com",
            senha_hash="hash",
            status="ativo"
        )
        db_session.add(cliente)
        db_session.commit()
        
        # Criar configuração com email
        from app.db.models.configuracao_bot import ConfiguracaoBot
        config = ConfiguracaoBot(
            cliente_id=cliente.id,
            tom="casual",
            notificar_email="atendente@teste.com"
        )
        db_session.add(config)
        db_session.commit()
        
        # Criar conversa
        conversa = Conversa(
            cliente_id=cliente.id,
            numero_whatsapp="5511999999999",
            status="aguardando_humano"
        )
        db_session.add(conversa)
        db_session.commit()
        
        # Notificar humano
        with patch('app.services.fallback.fallback_service.EmailService.enviar_email') as mock_email:
            FallbackService.notificar_humano(
                db=db_session,
                conversa_id=conversa.id,
                cliente_nome="Cliente Teste",
                ultima_mensagem="Preciso de ajuda"
            )
        
        # Verificar email enviado
        mock_email.assert_called_once()
        call_args = mock_email.call_args[1]
        assert call_args['destinatario'] == "atendente@teste.com"
        assert "Cliente Teste" in call_args['assunto']
