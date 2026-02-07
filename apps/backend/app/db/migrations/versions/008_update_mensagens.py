"""update mensagens table with confidence fields

Revision ID: 008
Revises: 007
Create Date: 2026-02-07 19:36:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar novos campos na tabela mensagens
    op.add_column('mensagens', sa.Column('confidence_score', sa.Float(), nullable=True))
    op.add_column('mensagens', sa.Column('fallback_triggered', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('mensagens', sa.Column('conversa_id', sa.Integer(), nullable=True))
    
    # Adicionar foreign key para conversas
    op.create_foreign_key('fk_mensagens_conversa_id', 'mensagens', 'conversas', ['conversa_id'], ['id'])
    
    # Criar índice para conversa_id
    op.create_index(op.f('ix_mensagens_conversa_id'), 'mensagens', ['conversa_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_mensagens_conversa_id'), table_name='mensagens')
    op.drop_constraint('fk_mensagens_conversa_id', 'mensagens', type_='foreignkey')
    op.drop_column('mensagens', 'conversa_id')
    op.drop_column('mensagens', 'fallback_triggered')
    op.drop_column('mensagens', 'confidence_score')
