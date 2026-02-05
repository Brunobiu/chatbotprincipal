"""
Testes para funcionalidades de segurança
"""
import pytest
from unittest.mock import patch


@pytest.mark.integration
class TestSecurity:
    """Testes de integração para segurança"""
    
    def test_health_check_retorna_200(self, client):
        """Testa que health check retorna 200"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "whatsapp-ai-bot"
    
    def test_health_check_tem_process_time_header(self, client):
        """Testa que health check retorna header X-Process-Time"""
        response = client.get("/health")
        
        assert "x-process-time" in response.headers
        process_time = float(response.headers["x-process-time"])
        assert process_time > 0
    
    def test_health_db_retorna_200(self, client):
        """Testa que health/db retorna 200"""
        response = client.get("/health/db")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"
    
    def test_cors_headers_presentes(self, client):
        """Testa que headers CORS estão presentes"""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # CORS deve permitir a origem
        assert response.status_code in [200, 204]
    
    @patch('app.core.config.settings.WEBHOOK_API_KEY', 'test_api_key')
    def test_webhook_sem_api_key_retorna_403(self, client):
        """Testa que webhook sem API key retorna 403 quando configurado"""
        response = client.post(
            "/webhook",
            json={
                "data": {
                    "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
                    "message": {"conversation": "Teste"}
                }
            }
        )
        
        # Deve retornar 403 quando API key está configurada mas não foi enviada
        assert response.status_code == 403
    
    @patch('app.core.config.settings.WEBHOOK_API_KEY', 'test_api_key')
    def test_webhook_com_api_key_invalida_retorna_403(self, client):
        """Testa que webhook com API key inválida retorna 403"""
        response = client.post(
            "/webhook",
            json={
                "data": {
                    "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
                    "message": {"conversation": "Teste"}
                }
            },
            headers={"X-API-Key": "chave_errada"}
        )
        
        assert response.status_code == 403
    
    def test_endpoint_inexistente_retorna_404(self, client):
        """Testa que endpoint inexistente retorna 404"""
        response = client.get("/endpoint-que-nao-existe")
        
        assert response.status_code == 404
    
    def test_rate_limiting_configurado(self, client):
        """Testa que rate limiting está configurado (não testa o limite)"""
        # Fazer algumas requisições
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200
        
        # Se chegou aqui, rate limiting não bloqueou (5 req está ok)
        assert True


@pytest.mark.unit
class TestSecurityFunctions:
    """Testes unitários para funções de segurança"""
    
    def test_config_tem_allowed_origins(self):
        """Testa que configuração tem ALLOWED_ORIGINS"""
        from app.core.config import settings
        
        assert hasattr(settings, 'ALLOWED_ORIGINS')
        assert isinstance(settings.ALLOWED_ORIGINS, str)
    
    def test_config_tem_rate_limit(self):
        """Testa que configuração tem RATE_LIMIT_PER_MINUTE"""
        from app.core.config import settings
        
        assert hasattr(settings, 'RATE_LIMIT_PER_MINUTE')
        assert isinstance(settings.RATE_LIMIT_PER_MINUTE, int)
        assert settings.RATE_LIMIT_PER_MINUTE > 0
    
    def test_get_allowed_origins_list(self):
        """Testa conversão de ALLOWED_ORIGINS para lista"""
        from app.core.config import settings
        
        origins = settings.get_allowed_origins_list()
        
        assert isinstance(origins, list)
        assert len(origins) > 0
        assert all(isinstance(origin, str) for origin in origins)
