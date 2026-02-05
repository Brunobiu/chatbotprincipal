"""
Script para testar manualmente o webhook de pagamento
Execute: python apps/backend/test_webhook_manual.py
"""
import sys
import os

# Adicionar o diretório do backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models.cliente import Cliente
from app.services.clientes.cliente_service import ClienteService
from app.core.config import DATABASE_URL

# Criar engine e sessão
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def testar_criacao_cliente():
    """Testa a criação de um cliente via serviço"""
    db = SessionLocal()
    
    try:
        print("🧪 Testando criação de cliente...")
        
        # Dados de teste
        email_teste = "teste@exemplo.com"
        nome_teste = "Cliente Teste"
        stripe_customer_id = "cus_test_123"
        stripe_subscription_id = "sub_test_123"
        stripe_status = "active"
        
        # Criar cliente
        cliente, senha = ClienteService.criar_cliente_from_stripe(
            db=db,
            email=email_teste,
            nome=nome_teste,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            stripe_status=stripe_status,
            telefone="+5511999999999"
        )
        
        print(f"✅ Cliente criado com sucesso!")
        print(f"   ID: {cliente.id}")
        print(f"   Nome: {cliente.nome}")
        print(f"   Email: {cliente.email}")
        print(f"   Status: {cliente.status}")
        print(f"   Stripe Customer ID: {cliente.stripe_customer_id}")
        print(f"   Stripe Subscription ID: {cliente.stripe_subscription_id}")
        
        if senha:
            print(f"   🔑 Senha gerada: {senha}")
        
        # Verificar se cliente foi salvo no banco
        cliente_db = db.query(Cliente).filter(Cliente.email == email_teste).first()
        if cliente_db:
            print(f"✅ Cliente encontrado no banco de dados!")
        else:
            print(f"❌ Cliente NÃO encontrado no banco de dados!")
        
        # Limpar teste (opcional - comente se quiser manter)
        # db.delete(cliente)
        # db.commit()
        # print(f"🧹 Cliente de teste removido")
        
    except Exception as e:
        print(f"❌ Erro ao testar: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE MANUAL - WEBHOOK DE PAGAMENTO")
    print("=" * 60)
    testar_criacao_cliente()
    print("=" * 60)
