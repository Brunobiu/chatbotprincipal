"""add_ip_cadastro_to_clientes

Revision ID: 032_add_ip_cadastro
Revises: 031_add_training_fields
Create Date: 2026-02-09 18:06:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '032_add_ip_cadastro'
down_revision = '031_add_training_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campo ip_cadastro na tabela clientes
    op.add_column('clientes', sa.Column('ip_cadastro', sa.String(45), nullable=True))


def downgrade():
    # Remover campo ip_cadastro
    op.drop_column('clientes', 'ip_cadastro')
