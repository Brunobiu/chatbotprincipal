"""add training fields

Revision ID: 031
Revises: 030
Create Date: 2026-02-09 15:44:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '031'
down_revision = '030'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campos de avaliação nas conversas
    op.add_column('conversas', sa.Column('avaliacao', sa.String(10), nullable=True))
    op.add_column('conversas', sa.Column('avaliado_em', sa.TIMESTAMP(), nullable=True))
    op.add_column('conversas', sa.Column('avaliado_por', sa.String(50), default='admin', nullable=True))
    
    op.create_index('idx_conversas_avaliacao', 'conversas', ['avaliacao'])


def downgrade():
    op.drop_index('idx_conversas_avaliacao')
    op.drop_column('conversas', 'avaliado_por')
    op.drop_column('conversas', 'avaliado_em')
    op.drop_column('conversas', 'avaliacao')
