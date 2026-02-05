"""add stripe fields to clientes

Revision ID: 002
Revises: 001
Create Date: 2026-02-04 16:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('clientes', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
    op.create_unique_constraint(op.f('uq_clientes_stripe_customer_id'), 'clientes', ['stripe_customer_id'])
    op.add_column('clientes', sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_clientes_stripe_subscription_id'), 'clientes', ['stripe_subscription_id'], unique=False)
    op.add_column('clientes', sa.Column('stripe_status', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('clientes', 'stripe_status')
    op.drop_index(op.f('ix_clientes_stripe_subscription_id'), table_name='clientes')
    op.drop_column('clientes', 'stripe_subscription_id')
    op.drop_constraint(op.f('uq_clientes_stripe_customer_id'), 'clientes', type_='unique')
    op.drop_column('clientes', 'stripe_customer_id')

