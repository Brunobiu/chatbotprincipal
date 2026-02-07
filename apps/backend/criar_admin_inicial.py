"""
Script para criar o administrador inicial do sistema.
Credenciais: brunobiuu / santana7996@
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.db.session import SessionLocal
from app.db.models.admin import Admin
from app.core.security import hash_senha
from datetime import datetime


def criar_admin_inicial():
    """Cria o administrador inicial do sistema"""
    db = SessionLocal()
    
    try:
        # Verificar se já existe algum admin
        admin_existente = db.query(Admin).filter(Admin.email == "brunobiuu").first()
        
        if admin_existente:
            print("❌ Admin já existe no sistema!")
            print(f"   Email: {admin_existente.email}")
            print(f"   Nome: {admin_existente.nome}")
            return
        
        # Criar admin inicial
        senha_hash = hash_senha("santana7996@")
        
        admin = Admin(
            nome="Bruno Biuu",
            email="brunobiuu",
            senha_hash=senha_hash,
            role="admin",
            tema="light",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ Admin inicial criado com sucesso!")
        print(f"   ID: {admin.id}")
        print(f"   Nome: {admin.nome}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role}")
        print(f"   Senha: santana7996@")
        print("\n🔐 Use estas credenciais para fazer login no painel admin")
        
    except Exception as e:
        print(f"❌ Erro ao criar admin: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Criando administrador inicial...")
    print("=" * 50)
    criar_admin_inicial()
    print("=" * 50)
