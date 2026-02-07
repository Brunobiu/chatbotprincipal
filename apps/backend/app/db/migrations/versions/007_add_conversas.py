"""add conversas table

Revision ID: 007
Revises: 006
Create Date: 2026-02-07 19:35:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar enum para status da conversa
    op.execute("CREATE TYPE statusconversa AS ENUM ('ativa', 'aguardando_humano', 'finalizada')")
    
    # Criar enum para motivo do fallback
    op.execute("CREATE TYPE motivofallback AS ENUM ('baixa_confianca', 'solicitacao_manual')")
    
    # Criar tabela conversas
    op.create_table('conversas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('numero_whatsapp', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='ativa'),
        sa.Column('motivo_fallback', sa.String(length=20), nullable=True),
        sa.Column('ultima_mensagem_em', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('assumida_por', sa.String(length=100), nullable=True),
        sa.Column('assumida_em', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversas_id'), 'conversas', ['id'], unique=False)
    op.create_index(op.f('ix_conversas_cliente_id'), 'conversas', ['cliente_id'], unique=False)
    op.create_index(op.f('ix_conversas_numero_whatsapp'), 'conversas', ['numero_whatsapp'], unique=False)
    op.create_index(op.f('ix_conversas_status'), 'conversas', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_conversas_status'), table_name='conversas')
    op.drop_index(op.f('ix_conversas_numero_whatsapp'), table_name='conversas')
    op.drop_index(op.f('ix_conversas_cliente_id'), table_name='conversas')
    op.drop_index(op.f('ix_conversas_id'), table_name='conversas')
    op.drop_table('conversas')
    op.execute('DROP TYPE motivofallback')
    op.execute('DROP TYPE statusconversa')
