"""
Testes para Webhook do WhatsApp
"""
import pytest
from unittest.mock import patch, AsyncMock

from app.db.models.cliente import Cliente, ClienteStatus
from app.db.models.instancia_whatsapp import InstanciaWhatsApp, InstanciaStatus
from app.services.clientes.cliente_service import ClienteService


@pytest.mark.integration
class TestWebhookWhatsApp:
    """Testes de integração para webhook do WhatsApp"""
    
    def test_webhook_sem_dados(self, client):
        """Testa webhook sem chat_id ou message"""
        response = client.post(
            "/webhook",
            json={"data": {}}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"
        assert data["reason"] == "missing_data"
    
    def test_webhook_mensagem_grupo(self, client):
        """Testa que mensagens de grupo são ignoradas"""
        response = client.post(
            "/webhook",
            json={
                "data": {
                    "key": {"remoteJid": "5511999999999@g.us"},
                    "message": {"conversation": "Olá grupo"}
                },
                "instance": "test_instance"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"
        assert data["reason"] == "group_message"
    
    def test_webhook_cliente_nao_encontrado(self, client, db_session):
        """Testa webhook quando cliente não é encontrado"""
        response = client.post(
            "/webhook",
            json={
                "data": {
                    "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
                    "message": {"conversation": "Olá"}
                },
                "instance": "instance_inexistente"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"
        assert data["reason"] == "client_not_found"
    
    def test_webhook_cliente_inativo(self, client, db_session, sample_cliente_data):
        """Testa que clientes inativos não processam mensagens"""
        # Criar cliente inativo
        cliente, _ = ClienteService.criar_cliente_from_stripe(
            db=db_session,
            **sample_cliente_data
        )
        cliente.status = ClienteStatus.SUSPENSO
        db_session.commit()
        
        # Criar instância WhatsApp
        instancia = InstanciaWhatsApp(
            cliente_id=cliente.id,
            instance_id="test_instance",
            numero="5511999999999",
            status=InstanciaStatus.CONECTADA
        )
        db_session.add(instancia)
        db_session.commit()
        
        # Enviar mensagem
        response = client.post(
            "/webhook",
            json={
                "data": {
                    "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
                    "message": {"conversation": "Olá"}
                },
                "instance": "test_instance"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"
        assert data["reason"] == "inactive_subscription"
    
    @patch('app.main.buffer_message', new_callable=AsyncMock)
    def test_webhook_cliente_ativo_processa_mensagem(
        self, mock_buffer, client, db_session, sample_cliente_data
    ):
        """Testa que cliente ativo processa mensagem corretamente"""
        # Criar cliente ativo
        cliente, _ = ClienteService.criar_cliente_from_stripe(
            db=db_session,
            **sample_cliente_data
        )
        
        # Criar instância WhatsApp
        instancia = InstanciaWhatsApp(
            cliente_id=cliente.id,
            instance_id="test_instance",
            numero="5511999999999",
            status=InstanciaStatus.CONECTADA
        )
        db_session.add(instancia)
        db_session.commit()
        
        # Enviar mensagem
        response = client.post(
            "/webhook",
            json={
                "data": {
                    "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
                    "message": {"conversation": "Olá, preciso de ajuda"}
                },
                "instance": "test_instance"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
        # Verificar que buffer_message foi chamado com cliente_id correto
        mock_buffer.assert_called_once()
        call_kwargs = mock_buffer.call_args[1]
        assert call_kwargs["cliente_id"] == cliente.id
        assert call_kwargs["chat_id"] == "5511999999999@s.whatsapp.net"
        assert call_kwargs["message"] == "Olá, preciso de ajuda"
    
    @patch('app.main.buffer_message', new_callable=AsyncMock)
    def test_webhook_lookup_por_numero(
        self, mock_buffer, client, db_session, sample_cliente_data
    ):
        """Testa lookup de cliente por número quando instance_id não encontrado"""
        # Criar cliente
        cliente, _ = ClienteService.criar_cliente_from_stripe(
            db=db_session,
            **sample_cliente_data
        )
        
        # Criar instância com instance_id diferente (para testar fallback por número)
        instancia = InstanciaWhatsApp(
            cliente_id=cliente.id,
            instance_id="instance_diferente",
            numero="5511999999999",
            status=InstanciaStatus.CONECTADA
        )
        db_session.add(instancia)
        db_session.commit()
        
        # Enviar mensagem sem instance (vai buscar por número)
        response = client.post(
            "/webhook",
            json={
                "data": {
                    "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
                    "message": {"conversation": "Teste"}
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
        # Verificar que encontrou cliente pelo número
        mock_buffer.assert_called_once()
        call_kwargs = mock_buffer.call_args[1]
        assert call_kwargs["cliente_id"] == cliente.id
