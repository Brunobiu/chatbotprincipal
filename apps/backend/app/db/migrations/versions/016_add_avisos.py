"""add avisos system

Revision ID: 016
Revises: 015
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela de avisos
    op.create_table(
        'avisos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(20), nullable=False),  # info, warning, error, success
        sa.Column('titulo', sa.String(200), nullable=False),
        sa.Column('mensagem', sa.Text(), nullable=False),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),
        sa.Column('dismissivel', sa.Boolean(), default=True, nullable=False),  # Pode fechar?
        sa.Column('data_inicio', sa.DateTime(), nullable=True),
        sa.Column('data_fim', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Índices
    op.create_index('idx_avisos_ativo', 'avisos', ['ativo'])
    op.create_index('idx_avisos_data_inicio', 'avisos', ['data_inicio'])
    op.create_index('idx_avisos_data_fim', 'avisos', ['data_fim'])


def downgrade():
    op.drop_index('idx_avisos_data_fim', 'avisos')
    op.drop_index('idx_avisos_data_inicio', 'avisos')
    op.drop_index('idx_avisos_ativo', 'avisos')
    op.drop_table('avisos')
