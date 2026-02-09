"""
Testes de Segurança - FASE 5
Valida bloqueio de IPs e detecção de anomalias
"""
import pytest
from datetime import datetime, timedelta
from app.services.security.ip_blocker import IPBlocker
from app.services.security.anomaly_detector import AnomalyDetector
from app.db.models.blocked_ip import BlockedIP
import redis
import json


class TestIPBlocker:
    """Testes do bloqueador de IPs"""
    
    def test_block_ip_temporary(self, db):
        """Testa bloqueio temporário de IP"""
        ip = "192.168.1.100"
        
        # Bloquear por 15 minutos
        blocked = IPBlocker.block_ip(db, ip, "Teste", duration_minutes=15)
        
        assert blocked.ip_address == ip
        assert blocked.reason == "Teste"
        assert blocked.is_permanent == False
        assert blocked.blocked_until is not None
    
    def test_block_ip_permanent(self, db):
        """Testa bloqueio permanente de IP"""
        ip = "192.168.1.101"
        
        # Bloquear permanentemente
        blocked = IPBlocker.block_ip(db, ip, "Ataque grave", duration_minutes=None)
        
        assert blocked.ip_address == ip
        assert blocked.is_permanent == True
        assert blocked.blocked_until is None
    
    def test_is_blocked_returns_true(self, db):
        """Testa que IP bloqueado retorna True"""
        ip = "192.168.1.102"
        
        # Bloquear
        IPBlocker.block_ip(db, ip, "Teste", duration_minutes=15)
        
        # Verificar
        is_blocked, reason = IPBlocker.is_blocked(db, ip)
        
        assert is_blocked == True
        assert reason == "Teste"
    
    def test_is_blocked_returns_false(self, db):
        """Testa que IP não bloqueado retorna False"""
        ip = "192.168.1.103"
        
        # Verificar (sem bloquear)
        is_blocked, reason = IPBlocker.is_blocked(db, ip)
        
        assert is_blocked == False
        assert reason == ""
    
    def test_progressive_blocking(self, db):
        """Testa bloqueio progressivo"""
        ip = "192.168.1.104"
        
        # Primeira tentativa
        blocked = IPBlocker.block_ip(db, ip, "Tentativa 1", duration_minutes=15)
        assert blocked.attempts_count == 1
        assert blocked.is_permanent == False
        
        # Segunda tentativa
        blocked = IPBlocker.block_ip(db, ip, "Tentativa 2", duration_minutes=15)
        assert blocked.attempts_count == 2
        assert blocked.is_permanent == False
        
        # Terceira, quarta, quinta tentativas
        for i in range(3, 6):
            blocked = IPBlocker.block_ip(db, ip, f"Tentativa {i}", duration_minutes=15)
        
        # Após 5 tentativas, deve ser permanente
        assert blocked.attempts_count == 5
        assert blocked.is_permanent == True
    
    def test_unblock_ip(self, db):
        """Testa desbloqueio de IP"""
        ip = "192.168.1.105"
        
        # Bloquear
        IPBlocker.block_ip(db, ip, "Teste", duration_minutes=15)
        
        # Verificar que está bloqueado
        is_blocked, _ = IPBlocker.is_blocked(db, ip)
        assert is_blocked == True
        
        # Desbloquear
        result = IPBlocker.unblock_ip(db, ip)
        assert result == True
        
        # Verificar que não está mais bloqueado
        is_blocked, _ = IPBlocker.is_blocked(db, ip)
        assert is_blocked == False
    
    def test_expired_block_is_removed(self, db):
        """Testa que bloqueio expirado é removido automaticamente"""
        ip = "192.168.1.106"
        
        # Criar bloqueio já expirado
        blocked = BlockedIP(
            ip_address=ip,
            reason="Teste",
            blocked_at=datetime.utcnow() - timedelta(hours=2),
            blocked_until=datetime.utcnow() - timedelta(hours=1),
            is_permanent=False
        )
        db.add(blocked)
        db.commit()
        
        # Verificar - deve remover automaticamente
        is_blocked, _ = IPBlocker.is_blocked(db, ip)
        assert is_blocked == False
        
        # Verificar que foi removido do banco
        blocked = db.query(BlockedIP).filter(BlockedIP.ip_address == ip).first()
        assert blocked is None


class TestAnomalyDetector:
    """Testes do detector de anomalias"""
    
    @pytest.fixture
    def redis_client(self):
        """Fixture de cliente Redis para testes"""
        client = redis.from_url("redis://localhost:6379/1")  # DB 1 para testes
        yield client
        # Limpar após teste
        client.flushdb()
    
    @pytest.fixture
    def detector(self, redis_client):
        """Fixture do detector"""
        return AnomalyDetector(redis_client)
    
    def test_track_request(self, detector):
        """Testa rastreamento de requisição"""
        ip = "192.168.1.200"
        
        # Rastrear requisição
        detector.track_request(ip, "/api/test", 200)
        
        # Verificar que foi rastreada
        recent = detector.get_recent_requests(ip, minutes=5)
        assert len(recent) == 1
        assert recent[0]['endpoint'] == "/api/test"
        assert recent[0]['status'] == 200
    
    def test_detects_too_many_requests(self, detector):
        """Testa detecção de muitas requisições"""
        ip = "192.168.1.201"
        
        # Simular 101 requisições
        for i in range(101):
            detector.track_request(ip, f"/api/endpoint{i % 10}", 200)
        
        # Verificar que detecta como suspeito
        is_suspicious, reason = detector.is_suspicious(ip)
        assert is_suspicious == True
        assert "Muitas requisições" in reason
    
    def test_detects_endpoint_scanning(self, detector):
        """Testa detecção de scanning de endpoints"""
        ip = "192.168.1.202"
        
        # Simular acesso a 31 endpoints diferentes
        for i in range(31):
            detector.track_request(ip, f"/api/endpoint{i}", 200)
        
        # Verificar que detecta como suspeito
        is_suspicious, reason = detector.is_suspicious(ip)
        assert is_suspicious == True
        assert "Scanning" in reason
    
    def test_detects_404_attacks(self, detector):
        """Testa detecção de muitos 404 (path traversal)"""
        ip = "192.168.1.203"
        
        # Simular 21 erros 404
        for i in range(21):
            detector.track_request(ip, f"/../../etc/passwd{i}", 404)
        
        # Verificar que detecta como suspeito
        is_suspicious, reason = detector.is_suspicious(ip)
        assert is_suspicious == True
        assert "404" in reason
    
    def test_detects_auth_failures(self, detector):
        """Testa detecção de falhas de autenticação"""
        ip = "192.168.1.204"
        
        # Simular 11 falhas de autenticação
        for i in range(11):
            detector.track_request(ip, "/api/auth/login", 401)
        
        # Verificar que detecta como suspeito
        is_suspicious, reason = detector.is_suspicious(ip)
        assert is_suspicious == True
        assert "autenticação" in reason
    
    def test_normal_behavior_not_suspicious(self, detector):
        """Testa que comportamento normal não é suspeito"""
        ip = "192.168.1.205"
        
        # Simular comportamento normal (10 requisições)
        for i in range(10):
            detector.track_request(ip, "/api/users", 200)
        
        # Verificar que NÃO é suspeito
        is_suspicious, reason = detector.is_suspicious(ip)
        assert is_suspicious == False
    
    def test_progressive_block_duration(self, detector):
        """Testa duração progressiva de bloqueio"""
        ip = "192.168.1.206"
        
        # Primeira vez: 15 minutos
        duration1 = detector.get_block_duration(ip)
        assert duration1 == 15
        
        # Segunda vez: 30 minutos
        duration2 = detector.get_block_duration(ip)
        assert duration2 == 30
        
        # Terceira vez: 60 minutos
        duration3 = detector.get_block_duration(ip)
        assert duration3 == 60
        
        # Quarta vez: 120 minutos
        duration4 = detector.get_block_duration(ip)
        assert duration4 == 120
        
        # Quinta vez: 240 minutos
        duration5 = detector.get_block_duration(ip)
        assert duration5 == 240
        
        # Sexta vez: permanente (None)
        duration6 = detector.get_block_duration(ip)
        assert duration6 is None


# Fixtures
@pytest.fixture
def db():
    """Fixture de banco de dados para testes"""
    from app.db.session import SessionLocal
    db = SessionLocal()
    yield db
    # Limpar após teste
    db.query(BlockedIP).delete()
    db.commit()
    db.close()


# Para rodar os testes:
# pytest apps/backend/tests/test_security_fase5.py -v
