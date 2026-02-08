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
    # Verificar quais colunas já existem
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    
    existing_columns = [col['name'] for col in inspector.get_columns('mensagens')]
    
    # Adicionar novos campos na tabela mensagens apenas se não existirem
    if 'confidence_score' not in existing_columns:
        op.add_column('mensagens', sa.Column('confidence_score', sa.Float(), nullable=True))
    
    if 'fallback_triggered' not in existing_columns:
        op.add_column('mensagens', sa.Column('fallback_triggered', sa.Boolean(), nullable=False, server_default='false'))
    
    if 'conversa_id' not in existing_columns:
        op.add_column('mensagens', sa.Column('conversa_id', sa.Integer(), nullable=True))
    
    # Verificar se a foreign key já existe
    existing_fks = [fk['name'] for fk in inspector.get_foreign_keys('mensagens')]
    if 'fk_mensagens_conversa_id' not in existing_fks:
        op.create_foreign_key('fk_mensagens_conversa_id', 'mensagens', 'conversas', ['conversa_id'], ['id'])
    
    # Verificar se o índice já existe
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('mensagens')]
    if 'ix_mensagens_conversa_id' not in existing_indexes:
        op.create_index(op.f('ix_mensagens_conversa_id'), 'mensagens', ['conversa_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_mensagens_conversa_id'), table_name='mensagens')
    op.drop_constraint('fk_mensagens_conversa_id', 'mensagens', type_='foreignkey')
    op.drop_column('mensagens', 'conversa_id')
    op.drop_column('mensagens', 'fallback_triggered')
    op.drop_column('mensagens', 'confidence_score')
