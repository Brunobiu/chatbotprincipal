"""add payment logs table

Revision ID: 025
Revises: 024
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '025'
down_revision = '024'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela de logs de pagamento (FASE 6)
    op.create_table(
        'payment_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
        sa.Column('stripe_invoice_id', sa.String(255), nullable=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(3), default='brl', nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('plan_id', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('webhook_received', sa.Boolean(), default=False, nullable=False),
        sa.Column('webhook_received_at', sa.DateTime(), nullable=True),
        sa.Column('webhook_event_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Índices
    op.create_index('ix_payment_logs_id', 'payment_logs', ['id'])
    op.create_index('ix_payment_logs_cliente_id', 'payment_logs', ['cliente_id'])
    op.create_index('ix_payment_logs_stripe_payment_intent_id', 'payment_logs', ['stripe_payment_intent_id'], unique=True)
    op.create_index('ix_payment_logs_stripe_subscription_id', 'payment_logs', ['stripe_subscription_id'])
    op.create_index('ix_payment_logs_stripe_invoice_id', 'payment_logs', ['stripe_invoice_id'])
    op.create_index('ix_payment_logs_stripe_customer_id', 'payment_logs', ['stripe_customer_id'])
    op.create_index('ix_payment_logs_status', 'payment_logs', ['status'])
    op.create_index('ix_payment_logs_webhook_event_id', 'payment_logs', ['webhook_event_id'], unique=True)


def downgrade():
    op.drop_index('ix_payment_logs_webhook_event_id', table_name='payment_logs')
    op.drop_index('ix_payment_logs_status', table_name='payment_logs')
    op.drop_index('ix_payment_logs_stripe_customer_id', table_name='payment_logs')
    op.drop_index('ix_payment_logs_stripe_invoice_id', table_name='payment_logs')
    op.drop_index('ix_payment_logs_stripe_subscription_id', table_name='payment_logs')
    op.drop_index('ix_payment_logs_stripe_payment_intent_id', table_name='payment_logs')
    op.drop_index('ix_payment_logs_cliente_id', table_name='payment_logs')
    op.drop_index('ix_payment_logs_id', table_name='payment_logs')
    op.drop_table('payment_logs')
