"""
Fixtures globais para testes
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import get_db
from app.main import app


# Database de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Cria uma sessão de banco de dados de teste
    Cada teste tem sua própria sessão isolada
    """
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    # Criar sessão
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Limpar tabelas após o teste
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Cliente de teste do FastAPI
    Usa banco de dados de teste
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_cliente_data():
    """
    Dados de exemplo para criar cliente
    """
    return {
        "email": "teste@exemplo.com",
        "nome": "Cliente Teste",
        "stripe_customer_id": "cus_test_123",
        "stripe_subscription_id": "sub_test_123",
        "stripe_status": "active",
        "telefone": "+5511999999999"
    }


@pytest.fixture
def sample_stripe_checkout_event():
    """
    Evento de exemplo do Stripe: checkout.session.completed
    """
    return {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "customer": "cus_test_123",
                "customer_email": "teste@exemplo.com",
                "customer_details": {
                    "name": "Cliente Teste",
                    "phone": "+5511999999999"
                },
                "subscription": "sub_test_123",
                "payment_status": "paid"
            }
        }
    }


@pytest.fixture
def sample_stripe_invoice_event():
    """
    Evento de exemplo do Stripe: invoice.payment_succeeded
    """
    return {
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "id": "in_test_123",
                "subscription": "sub_test_123",
                "amount_paid": 9900,
                "status": "paid"
            }
        }
    }
