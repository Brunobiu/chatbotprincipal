"""add notificacoes admin

Revision ID: 017
Revises: 016
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela notificacoes_admin
    op.create_table(
        'notificacoes_admin',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('mensagem', sa.Text(), nullable=False),
        sa.Column('prioridade', sa.String(length=20), nullable=False, server_default='normal'),
        sa.Column('lida', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ondelete='CASCADE')
    )
    op.create_index('idx_notificacoes_admin_admin', 'notificacoes_admin', ['admin_id', 'created_at'])
    op.create_index('idx_notificacoes_admin_lida', 'notificacoes_admin', ['admin_id', 'lida'])


def downgrade():
    op.drop_index('idx_notificacoes_admin_lida', table_name='notificacoes_admin')
    op.drop_index('idx_notificacoes_admin_admin', table_name='notificacoes_admin')
    op.drop_table('notificacoes_admin')
