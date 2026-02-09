"""
Script para aplicar migration 023 - FASE 1
"""
import sys
import os

# Adicionar o diretório app ao path
sys.path.insert(0, os.path.dirname(__file__))

from alembic.config import Config
from alembic import command

def apply_migration():
    """Aplica a migration 023"""
    try:
        # Configurar alembic
        alembic_cfg = Config("alembic.ini")
        
        # Aplicar migration
        print("🔄 Aplicando migration 023 - FASE 1...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migration 023 aplicada com sucesso!")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao aplicar migration: {e}")
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
