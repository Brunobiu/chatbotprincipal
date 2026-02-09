"""add analytics table

Revision ID: 030
Revises: 029
Create Date: 2026-02-09 15:41:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '030'
down_revision = '029'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela de métricas diárias
    op.create_table(
        'metricas_diarias',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('data', sa.Date(), nullable=False, unique=True, index=True),
        sa.Column('total_clientes', sa.Integer(), default=0, nullable=False),
        sa.Column('clientes_ativos', sa.Integer(), default=0, nullable=False),
        sa.Column('clientes_trial', sa.Integer(), default=0, nullable=False),
        sa.Column('clientes_cancelados', sa.Integer(), default=0, nullable=False),
        sa.Column('novos_clientes', sa.Integer(), default=0, nullable=False),
        sa.Column('conversoes', sa.Integer(), default=0, nullable=False),
        sa.Column('cancelamentos', sa.Integer(), default=0, nullable=False),
        sa.Column('total_conversas', sa.Integer(), default=0, nullable=False),
        sa.Column('total_mensagens', sa.Integer(), default=0, nullable=False),
        sa.Column('receita_dia', sa.DECIMAL(10, 2), default=0, nullable=False),
        sa.Column('custo_openai_dia', sa.DECIMAL(10, 2), default=0, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False)
    )


def downgrade():
    op.drop_table('metricas_diarias')
