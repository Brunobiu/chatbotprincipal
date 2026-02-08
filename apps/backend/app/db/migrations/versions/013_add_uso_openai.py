"""add uso openai tracking

Revision ID: 013
Revises: 012
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela de uso OpenAI
    op.create_table(
        'uso_openai',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('tokens_prompt', sa.Integer(), default=0, nullable=False),
        sa.Column('tokens_completion', sa.Integer(), default=0, nullable=False),
        sa.Column('tokens_total', sa.Integer(), default=0, nullable=False),
        sa.Column('custo_estimado', sa.Float(), default=0.0, nullable=False),
        sa.Column('mensagens_processadas', sa.Integer(), default=0, nullable=False),
        sa.Column('modelo', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Índices para performance
    op.create_index('ix_uso_openai_cliente_id', 'uso_openai', ['cliente_id'])
    op.create_index('ix_uso_openai_data', 'uso_openai', ['data'])
    op.create_index('ix_uso_openai_cliente_data', 'uso_openai', ['cliente_id', 'data'], unique=True)
    
    # Foreign key
    op.create_foreign_key(
        'fk_uso_openai_cliente',
        'uso_openai', 'clientes',
        ['cliente_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_constraint('fk_uso_openai_cliente', 'uso_openai', type_='foreignkey')
    op.drop_index('ix_uso_openai_cliente_data', table_name='uso_openai')
    op.drop_index('ix_uso_openai_data', table_name='uso_openai')
    op.drop_index('ix_uso_openai_cliente_id', table_name='uso_openai')
    op.drop_table('uso_openai')
