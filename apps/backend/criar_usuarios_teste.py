"""
Script para criar 5 usuários de teste no sistema
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db.session import SessionLocal
from app.db.models.cliente import Cliente
from app.services.clientes.cliente_service import ClienteService

def criar_usuarios_teste():
    """Cria 5 usuários de teste"""
    db = SessionLocal()
    
    usuarios = [
        {
            "nome": "Teste 1",
            "email": "teste1@teste.com",
            "telefone": "11999999991",
            "senha": "123456"
        },
        {
            "nome": "Teste 2",
            "email": "teste2@teste.com",
            "telefone": "11999999992",
            "senha": "123456"
        },
        {
            "nome": "Teste 3",
            "email": "teste3@teste.com",
            "telefone": "11999999993",
            "senha": "123456"
        },
        {
            "nome": "Teste 4",
            "email": "teste4@teste.com",
            "telefone": "11999999994",
            "senha": "123456"
        },
        {
            "nome": "Teste 5",
            "email": "teste5@teste.com",
            "telefone": "11999999995",
            "senha": "123456"
        }
    ]
    
    criados = 0
    
    for user_data in usuarios:
        # Verificar se já existe
        existe = db.query(Cliente).filter(Cliente.email == user_data["email"]).first()
        
        if existe:
            print(f"⚠️  {user_data['email']} já existe - pulando")
            continue
        
        # Criar cliente
        cliente = Cliente(
            nome=user_data["nome"],
            email=user_data["email"],
            telefone=user_data["telefone"],
            senha_hash=ClienteService.hash_senha(user_data["senha"]),
            status="ativo"
        )
        
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        
        print(f"✅ Criado: {user_data['email']} (ID: {cliente.id})")
        criados += 1
    
    db.close()
    
    print(f"\n🎉 Total criados: {criados}/5")
    print("\n📋 Credenciais:")
    print("Email: teste1@teste.com até teste5@teste.com")
    print("Senha: 123456")

if __name__ == "__main__":
    criar_usuarios_teste()
