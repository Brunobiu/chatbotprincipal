"""add billing fields

Revision ID: 027
Revises: 026
Create Date: 2026-02-09 15:08:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '027'
down_revision = '026'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campos de billing
    op.add_column('clientes', sa.Column('plano', sa.String(20), nullable=True))
    op.add_column('clientes', sa.Column('plano_preco', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('clientes', sa.Column('plano_valor_total', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('clientes', sa.Column('proxima_cobranca', sa.TIMESTAMP(), nullable=True))
    op.add_column('clientes', sa.Column('plano_pendente', sa.String(20), nullable=True))
    
    # Criar tabela de pagamentos
    op.create_table(
        'pagamentos',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('cliente_id', sa.Integer(), sa.ForeignKey('clientes.id'), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
        sa.Column('plano', sa.String(20), nullable=False),
        sa.Column('valor', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('data_pagamento', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False)
    )
    
    op.create_index('idx_pagamentos_cliente', 'pagamentos', ['cliente_id'])
    op.create_index('idx_pagamentos_status', 'pagamentos', ['status'])


def downgrade():
    op.drop_index('idx_pagamentos_status')
    op.drop_index('idx_pagamentos_cliente')
    op.drop_table('pagamentos')
    
    op.drop_column('clientes', 'plano_pendente')
    op.drop_column('clientes', 'proxima_cobranca')
    op.drop_column('clientes', 'plano_valor_total')
    op.drop_column('clientes', 'plano_preco')
    op.drop_column('clientes', 'plano')
