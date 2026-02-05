"""
Script para criar usuário de teste no banco de dados
USO: python criar_usuario_teste.py
"""
from datetime import datetime
from app.db.session import SessionLocal
from app.services.clientes.cliente_service import ClienteService
from app.db.models.cliente import ClienteStatus

def criar_usuario_teste():
    """Cria um usuário de teste no banco"""
    db = SessionLocal()
    
    try:
        # Dados do usuário de teste
        email = "teste@exemplo.com"
        nome = "Usuário Teste"
        telefone = "+5511999999999"
        senha = "senha123"  # Senha simples para teste
        
        # Verifica se já existe
        cliente_existente = ClienteService.buscar_por_email(db, email)
        if cliente_existente:
            print(f"⚠️ Usuário {email} já existe!")
            print(f"   ID: {cliente_existente.id}")
            print(f"   Nome: {cliente_existente.nome}")
            print(f"   Status: {cliente_existente.status}")
            print("\n🔄 Resetando senha para: senha123")
            
            # Resetar senha
            cliente_existente.senha_hash = ClienteService.hash_senha(senha)
            cliente_existente.updated_at = datetime.utcnow()
            db.commit()
            
            print("✅ Senha resetada com sucesso!")
            print(f"\n🔑 Use estas credenciais para fazer login:")
            print(f"   Email: {email}")
            print(f"   Senha: {senha}")
            return
        
        # Cria hash da senha
        senha_hash = ClienteService.hash_senha(senha)
        
        # Cria cliente manualmente
        from app.db.models.cliente import Cliente
        
        novo_cliente = Cliente(
            nome=nome,
            email=email,
            telefone=telefone,
            senha_hash=senha_hash,
            status=ClienteStatus.ATIVO,
            stripe_customer_id=None,
            stripe_subscription_id=None,
            stripe_status=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)
        
        print("✅ Usuário de teste criado com sucesso!")
        print(f"   ID: {novo_cliente.id}")
        print(f"   Nome: {novo_cliente.nome}")
        print(f"   Email: {novo_cliente.email}")
        print(f"   Senha: {senha}")
        print(f"   Status: {novo_cliente.status}")
        print("\n🔑 Use estas credenciais para fazer login:")
        print(f"   Email: {email}")
        print(f"   Senha: {senha}")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    criar_usuario_teste()
