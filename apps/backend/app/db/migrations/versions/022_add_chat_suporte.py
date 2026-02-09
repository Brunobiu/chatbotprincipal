"""add chat suporte

Revision ID: 022
Revises: 021
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '022'
down_revision = '021'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela de mensagens do chat suporte
    op.create_table(
        'chat_suporte_mensagens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('remetente_tipo', sa.String(20), nullable=False),  # 'cliente' ou 'ia'
        sa.Column('mensagem', sa.Text(), nullable=False),
        sa.Column('confianca', sa.Float(), nullable=True),  # Confiança da resposta da IA
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chat_suporte_mensagens_cliente_id', 'chat_suporte_mensagens', ['cliente_id'])
    op.create_index('ix_chat_suporte_mensagens_created_at', 'chat_suporte_mensagens', ['created_at'])
    
    # Adicionar campos na tabela tickets para resposta automática da IA
    op.add_column('tickets', sa.Column('resposta_ia', sa.Text(), nullable=True))
    op.add_column('tickets', sa.Column('confianca_ia', sa.Float(), nullable=True))


def downgrade():
    # Remover campos da tabela tickets
    op.drop_column('tickets', 'confianca_ia')
    op.drop_column('tickets', 'resposta_ia')
    
    # Remover índices e tabela
    op.drop_index('ix_chat_suporte_mensagens_created_at', table_name='chat_suporte_mensagens')
    op.drop_index('ix_chat_suporte_mensagens_cliente_id', table_name='chat_suporte_mensagens')
    op.drop_table('chat_suporte_mensagens')
