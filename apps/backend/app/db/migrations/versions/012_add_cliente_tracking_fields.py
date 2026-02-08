"""add cliente tracking fields

Revision ID: 012
Revises: 011
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campos de tracking ao cliente
    op.add_column('clientes', sa.Column('ultimo_login', sa.DateTime(), nullable=True))
    op.add_column('clientes', sa.Column('ip_ultimo_login', sa.String(45), nullable=True))
    op.add_column('clientes', sa.Column('total_mensagens_enviadas', sa.Integer(), default=0, nullable=False, server_default='0'))
    
    # Criar índice para busca por último login
    op.create_index('ix_clientes_ultimo_login', 'clientes', ['ultimo_login'])


def downgrade():
    op.drop_index('ix_clientes_ultimo_login', table_name='clientes')
    op.drop_column('clientes', 'total_mensagens_enviadas')
    op.drop_column('clientes', 'ip_ultimo_login')
    op.drop_column('clientes', 'ultimo_login')
