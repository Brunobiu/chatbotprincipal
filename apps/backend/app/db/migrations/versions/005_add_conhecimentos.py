"""add conhecimentos table

Revision ID: 005
Revises: 004
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela conhecimentos
    op.create_table(
        'conhecimentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('conteudo_texto', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('cliente_id')
    )
    op.create_index(op.f('ix_conhecimentos_id'), 'conhecimentos', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_conhecimentos_id'), table_name='conhecimentos')
    op.drop_table('conhecimentos')
