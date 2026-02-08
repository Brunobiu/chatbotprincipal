"""add conhecimento estruturado

Revision ID: 011
Revises: 010
Create Date: 2026-02-08 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna conteudo_estruturado (JSONB)
    op.add_column('conhecimentos', sa.Column('conteudo_estruturado', JSONB, nullable=True))
    
    # Adicionar índice GIN para busca eficiente no JSON
    op.create_index(
        'ix_conhecimentos_conteudo_estruturado',
        'conhecimentos',
        ['conteudo_estruturado'],
        postgresql_using='gin'
    )


def downgrade():
    op.drop_index('ix_conhecimentos_conteudo_estruturado', table_name='conhecimentos')
    op.drop_column('conhecimentos', 'conteudo_estruturado')
