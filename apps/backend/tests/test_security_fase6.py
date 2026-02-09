"""
Testes de Segurança - FASE 6
Valida segurança de pagamentos
"""
import pytest
from app.services.billing.payment_auditor import PaymentAuditor
from app.db.models.payment_log import PaymentLog


class TestPaymentAuditor:
    """Testes do auditor de pagamentos"""
    
    def test_log_payment(self, db, cliente_fixture):
        """Testa logging de pagamento"""
        log = PaymentAuditor.log_payment(
            db=db,
            cliente_id=cliente_fixture.id,
            amount=99.90,
            status="pending",
            stripe_payment_intent_id="pi_test123",
            plan_id="basic"
        )
        
        assert log.id is not None
        assert log.cliente_id == cliente_fixture.id
        assert log.amount == 99.90
        assert log.status == "pending"
        assert log.stripe_payment_intent_id == "pi_test123"
    
    def test_update_payment_status(self, db, cliente_fixture):
        """Testa atualização de status"""
        # Criar log
        log = PaymentAuditor.log_payment(
            db=db,
            cliente_id=cliente_fixture.id,
            amount=99.90,
            status="pending",
            stripe_payment_intent_id="pi_test456"
        )
        
        # Atualizar status
        updated = PaymentAuditor.update_payment_status(
            db=db,
            stripe_payment_intent_id="pi_test456",
            new_status="succeeded",
            webhook_event_id="evt_test123"
        )
        
        assert updated.status == "succeeded"
        assert updated.webhook_received == True
        assert updated.webhook_event_id == "evt_test123"
    
    def test_replay_attack_detection(self, db, cliente_fixture):
        """Testa detecção de replay attack"""
        webhook_event_id = "evt_replay_test"
        
        # Primeira vez: não é replay
        is_replay = PaymentAuditor.check_replay_attack(db, webhook_event_id)
        assert is_replay == False
        
        # Criar log com este webhook_event_id
        PaymentAuditor.log_payment(
            db=db,
            cliente_id=cliente_fixture.id,
            amount=99.90,
            status="succeeded",
            webhook_event_id=webhook_event_id
        )
        
        # Segunda vez: É REPLAY!
        is_replay = PaymentAuditor.check_replay_attack(db, webhook_event_id)
        assert is_replay == True
    
    def test_get_cliente_payments(self, db, cliente_fixture):
        """Testa listagem de pagamentos do cliente"""
        # Criar 3 pagamentos
        for i in range(3):
            PaymentAuditor.log_payment(
                db=db,
                cliente_id=cliente_fixture.id,
                amount=99.90 + i,
                status="succeeded",
                stripe_payment_intent_id=f"pi_test{i}"
            )
        
        # Listar
        payments = PaymentAuditor.get_cliente_payments(db, cliente_fixture.id)
        
        assert len(payments) == 3
        # Deve estar ordenado por data (mais recente primeiro)
        assert payments[0].amount == 101.90  # Último criado
    
    def test_get_failed_payments(self, db, cliente_fixture):
        """Testa listagem de pagamentos falhados"""
        # Criar pagamentos (2 falhados, 1 sucesso)
        PaymentAuditor.log_payment(
            db=db,
            cliente_id=cliente_fixture.id,
            amount=99.90,
            status="failed",
            stripe_payment_intent_id="pi_fail1"
        )
        
        PaymentAuditor.log_payment(
            db=db,
            cliente_id=cliente_fixture.id,
            amount=99.90,
            status="succeeded",
            stripe_payment_intent_id="pi_success1"
        )
        
        PaymentAuditor.log_payment(
            db=db,
            cliente_id=cliente_fixture.id,
            amount=99.90,
            status="failed",
            stripe_payment_intent_id="pi_fail2"
        )
        
        # Listar apenas falhados
        failed = PaymentAuditor.get_failed_payments(db, days=7)
        
        assert len(failed) == 2
        assert all(p.status == "failed" for p in failed)


class TestPaymentSecurity:
    """Testes de segurança de pagamentos"""
    
    def test_payment_log_prevents_duplicate_webhook(self, db, cliente_fixture):
        """Testa que webhook duplicado não é processado duas vezes"""
        webhook_event_id = "evt_duplicate_test"
        
        # Primeiro webhook
        log1 = PaymentAuditor.log_payment(
            db=db,
            cliente_id=cliente_fixture.id,
            amount=99.90,
            status="pending",
            stripe_payment_intent_id="pi_dup_test",
            webhook_event_id=webhook_event_id
        )
        
        # Tentar processar mesmo webhook novamente
        updated = PaymentAuditor.update_payment_status(
            db=db,
            stripe_payment_intent_id="pi_dup_test",
            new_status="succeeded",
            webhook_event_id=webhook_event_id  # Mesmo ID!
        )
        
        # Deve retornar o log existente sem atualizar
        assert updated.webhook_event_id == webhook_event_id
        # Status não deve mudar (ainda pending)
        assert updated.status == "pending"
    
    def test_payment_log_unique_constraints(self, db, cliente_fixture):
        """Testa constraints únicos"""
        # Criar primeiro log
        PaymentAuditor.log_payment(
            db=db,
            cliente_id=cliente_fixture.id,
            amount=99.90,
            status="pending",
            stripe_payment_intent_id="pi_unique_test"
        )
        
        # Tentar criar outro com mesmo payment_intent_id
        with pytest.raises(Exception):  # Deve falhar por constraint unique
            PaymentAuditor.log_payment(
                db=db,
                cliente_id=cliente_fixture.id,
                amount=99.90,
                status="pending",
                stripe_payment_intent_id="pi_unique_test"  # Duplicado!
            )


# Fixtures
@pytest.fixture
def db():
    """Fixture de banco de dados"""
    from app.db.session import SessionLocal
    db = SessionLocal()
    yield db
    # Limpar após teste
    db.query(PaymentLog).delete()
    db.commit()
    db.close()


@pytest.fixture
def cliente_fixture(db):
    """Fixture de cliente para testes"""
    from app.db.models.cliente import Cliente, ClienteStatus
    
    cliente = Cliente(
        nome="Cliente Teste",
        email="teste_payment@test.com",
        senha_hash="hash",
        status=ClienteStatus.ATIVO
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    
    yield cliente
    
    # Limpar
    db.delete(cliente)
    db.commit()


# Para rodar os testes:
# pytest apps/backend/tests/test_security_fase6.py -v
