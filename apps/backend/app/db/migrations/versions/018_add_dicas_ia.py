"""add dicas ia

Revision ID: 018
Revises: 017
Create Date: 2024-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela dicas_ia
    op.create_table(
        'dicas_ia',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('admin_id', sa.Integer(), sa.ForeignKey('admins.id', ondelete='CASCADE'), nullable=False),
        sa.Column('conteudo', JSON, nullable=False),
        sa.Column('objetivo_mensal', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    
    # Criar índice para busca por admin
    op.create_index('ix_dicas_ia_admin_id', 'dicas_ia', ['admin_id'])


def downgrade():
    op.drop_index('ix_dicas_ia_admin_id', table_name='dicas_ia')
    op.drop_table('dicas_ia')
