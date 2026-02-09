"""add_device_fingerprint_to_clientes

Revision ID: 033_add_device_fingerprint
Revises: 032_add_ip_cadastro
Create Date: 2026-02-09 18:09:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '033_add_device_fingerprint'
down_revision = '032_add_ip_cadastro'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campo device_fingerprint na tabela clientes
    op.add_column('clientes', sa.Column('device_fingerprint', sa.String(255), nullable=True))


def downgrade():
    # Remover campo device_fingerprint
    op.drop_column('clientes', 'device_fingerprint')
