"""add blocked ips table

Revision ID: 024
Revises: 023
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '024'
down_revision = '023'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela de IPs bloqueados (FASE 5)
    op.create_table(
        'blocked_ips',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('reason', sa.String(500), nullable=False),
        sa.Column('blocked_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('blocked_until', sa.DateTime(), nullable=True),
        sa.Column('is_permanent', sa.Boolean(), default=False, nullable=False),
        sa.Column('attempts_count', sa.Integer(), default=1, nullable=False),
        sa.Column('last_attempt', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Índices
    op.create_index('ix_blocked_ips_id', 'blocked_ips', ['id'])
    op.create_index('ix_blocked_ips_ip_address', 'blocked_ips', ['ip_address'], unique=True)
    op.create_index('ix_blocked_ips_blocked_until', 'blocked_ips', ['blocked_until'])


def downgrade():
    op.drop_index('ix_blocked_ips_blocked_until', table_name='blocked_ips')
    op.drop_index('ix_blocked_ips_ip_address', table_name='blocked_ips')
    op.drop_index('ix_blocked_ips_id', table_name='blocked_ips')
    op.drop_table('blocked_ips')
