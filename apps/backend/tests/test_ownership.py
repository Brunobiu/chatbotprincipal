"""
Testes de Ownership (FASE 2)
Garante que usuários só acessem seus próprios recursos
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.ownership import (
    OwnershipValidator,
    verify_conversa_ownership,
    verify_instancia_ownership,
    verify_ticket_ownership
)
from app.db.models.cliente import Cliente
from app.db.models.conversa import Conversa
from app.db.models.instancia_whatsapp import InstanciaWhatsApp
from app.db.models.ticket import Ticket


class TestOwnershipValidator:
    """Testes do OwnershipValidator"""
    
    def test_verify_conversa_ownership_success(self, db: Session):
        """Testa que cliente pode acessar sua própria conversa"""
        # Criar cliente e conversa
        cliente = Cliente(
            nome="Test",
            email="test@test.com",
            senha_hash="hash"
        )
        db.add(cliente)
        db.commit()
        
        conversa = Conversa(
            cliente_id=cliente.id,
            chat_id="123456",
            nome_contato="Contato"
        )
        db.add(conversa)
        db.commit()
        
        # Verificar ownership
        result = verify_conversa_ownership(db, conversa.id, cliente)
        
        assert result.id == conversa.id
        assert result.cliente_id == cliente.id
    
    def test_verify_conversa_ownership_fail(self, db: Session):
        """Testa que cliente NÃO pode acessar conversa de outro"""
        # Criar dois clientes
        cliente_a = Cliente(
            nome="Cliente A",
            email="a@test.com",
            senha_hash="hash"
        )
        cliente_b = Cliente(
            nome="Cliente B",
            email="b@test.com",
            senha_hash="hash"
        )
        db.add_all([cliente_a, cliente_b])
        db.commit()
        
        # Cliente A cria conversa
        conversa = Conversa(
            cliente_id=cliente_a.id,
            chat_id="123456",
            nome_contato="Contato"
        )
        db.add(conversa)
        db.commit()
        
        # Cliente B tenta acessar
        with pytest.raises(Exception) as exc_info:
            verify_conversa_ownership(db, conversa.id, cliente_b)
        
        assert exc_info.value.status_code == 404
        assert "não encontrada" in str(exc_info.value.detail).lower()
    
    def test_get_cliente_conversas_only_own(self, db: Session):
        """Testa que listagem retorna apenas conversas do cliente"""
        # Criar dois clientes
        cliente_a = Cliente(
            nome="Cliente A",
            email="a@test.com",
            senha_hash="hash"
        )
        cliente_b = Cliente(
            nome="Cliente B",
            email="b@test.com",
            senha_hash="hash"
        )
        db.add_all([cliente_a, cliente_b])
        db.commit()
        
        # Criar conversas para cada cliente
        conversa_a1 = Conversa(
            cliente_id=cliente_a.id,
            chat_id="111",
            nome_contato="A1"
        )
        conversa_a2 = Conversa(
            cliente_id=cliente_a.id,
            chat_id="222",
            nome_contato="A2"
        )
        conversa_b1 = Conversa(
            cliente_id=cliente_b.id,
            chat_id="333",
            nome_contato="B1"
        )
        db.add_all([conversa_a1, conversa_a2, conversa_b1])
        db.commit()
        
        # Cliente A lista suas conversas
        conversas_a = OwnershipValidator.get_cliente_conversas(db, cliente_a)
        
        # Deve retornar apenas 2 conversas (do cliente A)
        assert len(conversas_a) == 2
        assert all(c.cliente_id == cliente_a.id for c in conversas_a)
        
        # Cliente B lista suas conversas
        conversas_b = OwnershipValidator.get_cliente_conversas(db, cliente_b)
        
        # Deve retornar apenas 1 conversa (do cliente B)
        assert len(conversas_b) == 1
        assert conversas_b[0].cliente_id == cliente_b.id
    
    def test_verify_instancia_ownership_success(self, db: Session):
        """Testa que cliente pode acessar sua própria instância"""
        cliente = Cliente(
            nome="Test",
            email="test@test.com",
            senha_hash="hash"
        )
        db.add(cliente)
        db.commit()
        
        instancia = InstanciaWhatsApp(
            cliente_id=cliente.id,
            instance_id="inst_123",
            numero="5511999999999"
        )
        db.add(instancia)
        db.commit()
        
        result = verify_instancia_ownership(db, instancia.id, cliente)
        
        assert result.id == instancia.id
        assert result.cliente_id == cliente.id
    
    def test_verify_instancia_ownership_fail(self, db: Session):
        """Testa que cliente NÃO pode acessar instância de outro"""
        cliente_a = Cliente(
            nome="Cliente A",
            email="a@test.com",
            senha_hash="hash"
        )
        cliente_b = Cliente(
            nome="Cliente B",
            email="b@test.com",
            senha_hash="hash"
        )
        db.add_all([cliente_a, cliente_b])
        db.commit()
        
        instancia = InstanciaWhatsApp(
            cliente_id=cliente_a.id,
            instance_id="inst_123",
            numero="5511999999999"
        )
        db.add(instancia)
        db.commit()
        
        with pytest.raises(Exception) as exc_info:
            verify_instancia_ownership(db, instancia.id, cliente_b)
        
        assert exc_info.value.status_code == 404
    
    def test_verify_ticket_ownership_success(self, db: Session):
        """Testa que cliente pode acessar seu próprio ticket"""
        cliente = Cliente(
            nome="Test",
            email="test@test.com",
            senha_hash="hash"
        )
        db.add(cliente)
        db.commit()
        
        ticket = Ticket(
            cliente_id=cliente.id,
            titulo="Problema",
            descricao="Descrição"
        )
        db.add(ticket)
        db.commit()
        
        result = verify_ticket_ownership(db, ticket.id, cliente)
        
        assert result.id == ticket.id
        assert result.cliente_id == cliente.id
    
    def test_verify_ticket_ownership_fail(self, db: Session):
        """Testa que cliente NÃO pode acessar ticket de outro"""
        cliente_a = Cliente(
            nome="Cliente A",
            email="a@test.com",
            senha_hash="hash"
        )
        cliente_b = Cliente(
            nome="Cliente B",
            email="b@test.com",
            senha_hash="hash"
        )
        db.add_all([cliente_a, cliente_b])
        db.commit()
        
        ticket = Ticket(
            cliente_id=cliente_a.id,
            titulo="Problema",
            descricao="Descrição"
        )
        db.add(ticket)
        db.commit()
        
        with pytest.raises(Exception) as exc_info:
            verify_ticket_ownership(db, ticket.id, cliente_b)
        
        assert exc_info.value.status_code == 404


class TestOwnershipIntegration:
    """Testes de integração com API"""
    
    def test_cannot_access_other_user_conversa_via_api(
        self,
        client: TestClient,
        db: Session
    ):
        """Testa que não é possível acessar conversa de outro usuário via API"""
        # TODO: Implementar após atualizar rotas com ownership
        pass
    
    def test_list_conversas_returns_only_own(
        self,
        client: TestClient,
        db: Session
    ):
        """Testa que listagem retorna apenas conversas próprias"""
        # TODO: Implementar após atualizar rotas com ownership
        pass


# Fixtures
@pytest.fixture
def db():
    """Fixture de banco de dados para testes"""
    # TODO: Implementar fixture de DB
    pass


@pytest.fixture
def client():
    """Fixture de cliente HTTP para testes"""
    # TODO: Implementar fixture de client
    pass
