"""add configuracoes_bot table

Revision ID: 004
Revises: 003
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela configuracoes_bot
    op.create_table(
        'configuracoes_bot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('tom', sa.Enum('formal', 'casual', 'tecnico', name='tomenum'), nullable=False, server_default='casual'),
        sa.Column('mensagem_saudacao', sa.Text(), nullable=True),
        sa.Column('mensagem_fallback', sa.Text(), nullable=True),
        sa.Column('mensagem_espera', sa.Text(), nullable=True),
        sa.Column('mensagem_retorno_24h', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('cliente_id')
    )
    op.create_index(op.f('ix_configuracoes_bot_id'), 'configuracoes_bot', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_configuracoes_bot_id'), table_name='configuracoes_bot')
    op.drop_table('configuracoes_bot')
    op.execute('DROP TYPE tomenum')
