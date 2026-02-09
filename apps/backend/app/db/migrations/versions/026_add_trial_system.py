"""add trial system

Revision ID: 026
Revises: 025
Create Date: 2026-02-09 14:54:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '026'
down_revision = '025'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campos de trial
    op.add_column('clientes', sa.Column('trial_starts_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('clientes', sa.Column('trial_ends_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('clientes', sa.Column('subscription_status', sa.String(20), server_default='trial', nullable=False))
    
    # Atualizar clientes existentes com assinatura ativa
    op.execute("""
        UPDATE clientes 
        SET subscription_status = 'active' 
        WHERE stripe_subscription_id IS NOT NULL
    """)


def downgrade():
    op.drop_column('clientes', 'subscription_status')
    op.drop_column('clientes', 'trial_ends_at')
    op.drop_column('clientes', 'trial_starts_at')
