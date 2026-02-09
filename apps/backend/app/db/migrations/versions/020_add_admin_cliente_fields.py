"""add admin cliente fields

Revision ID: 020
Revises: 019
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '020'
down_revision = '019'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campos para admin usar ferramenta
    op.add_column('clientes', sa.Column('eh_cliente_admin', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('clientes', sa.Column('admin_vinculado_id', sa.Integer(), nullable=True))
    
    # Criar índice para admin_vinculado_id
    op.create_index('ix_clientes_admin_vinculado_id', 'clientes', ['admin_vinculado_id'])


def downgrade():
    # Remover índice
    op.drop_index('ix_clientes_admin_vinculado_id', table_name='clientes')
    
    # Remover colunas
    op.drop_column('clientes', 'admin_vinculado_id')
    op.drop_column('clientes', 'eh_cliente_admin')
