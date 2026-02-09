"""add_whatsapp_number_and_trial_history

Revision ID: 034_add_whatsapp_trial
Revises: 033_add_device_fingerprint
Create Date: 2026-02-09 18:12:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '034_add_whatsapp_trial'
down_revision = '033_add_device_fingerprint'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campo whatsapp_number na tabela clientes
    op.add_column('clientes', sa.Column('whatsapp_number', sa.String(20), nullable=True))
    
    # Criar tabela trial_history
    op.create_table(
        'trial_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('whatsapp_number', sa.String(20), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('ip_cadastro', sa.String(45), nullable=True),
        sa.Column('device_fingerprint', sa.String(255), nullable=True),
        sa.Column('used_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('whatsapp_number')
    )
    
    # Criar índice para busca rápida
    op.create_index('idx_trial_history_whatsapp', 'trial_history', ['whatsapp_number'])


def downgrade():
    # Remover índice e tabela
    op.drop_index('idx_trial_history_whatsapp', table_name='trial_history')
    op.drop_table('trial_history')
    
    # Remover campo whatsapp_number
    op.drop_column('clientes', 'whatsapp_number')
