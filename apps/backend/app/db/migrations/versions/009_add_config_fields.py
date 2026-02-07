"""add threshold_confianca and notificar_email to configuracoes_bot

Revision ID: 009
Revises: 008
Create Date: 2026-02-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campos threshold_confianca e notificar_email
    op.add_column('configuracoes_bot', sa.Column('threshold_confianca', sa.Float(), nullable=False, server_default='0.6'))
    op.add_column('configuracoes_bot', sa.Column('notificar_email', sa.String(255), nullable=True))


def downgrade():
    # Remover campos
    op.drop_column('configuracoes_bot', 'notificar_email')
    op.drop_column('configuracoes_bot', 'threshold_confianca')
