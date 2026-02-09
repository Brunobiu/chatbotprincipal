"""add agendamentos

Revision ID: 021
Revises: 020
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '021'
down_revision = '020'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela de configurações de horários
    op.create_table(
        'configuracoes_horarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('horarios_disponiveis', JSON, nullable=False),  # {"segunda": [{"inicio": "09:00", "fim": "18:00"}], ...}
        sa.Column('duracao_slot_minutos', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('tipos_servico', JSON, nullable=True),  # ["consulta", "banho", "corte", ...]
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_configuracoes_horarios_cliente_id', 'configuracoes_horarios', ['cliente_id'])
    
    # Tabela de agendamentos
    op.create_table(
        'agendamentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('numero_usuario', sa.String(20), nullable=False),  # Número WhatsApp do usuário
        sa.Column('nome_usuario', sa.String(255), nullable=True),
        sa.Column('data_hora', sa.DateTime(), nullable=False),
        sa.Column('tipo_servico', sa.String(100), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pendente'),  # pendente, aprovado, recusado, cancelado
        sa.Column('mensagem_original', sa.Text(), nullable=True),  # Mensagem original do usuário
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agendamentos_cliente_id', 'agendamentos', ['cliente_id'])
    op.create_index('ix_agendamentos_status', 'agendamentos', ['status'])
    op.create_index('ix_agendamentos_data_hora', 'agendamentos', ['data_hora'])
    op.create_index('ix_agendamentos_numero_usuario', 'agendamentos', ['numero_usuario'])


def downgrade():
    op.drop_index('ix_agendamentos_numero_usuario', table_name='agendamentos')
    op.drop_index('ix_agendamentos_data_hora', table_name='agendamentos')
    op.drop_index('ix_agendamentos_status', table_name='agendamentos')
    op.drop_index('ix_agendamentos_cliente_id', table_name='agendamentos')
    op.drop_table('agendamentos')
    
    op.drop_index('ix_configuracoes_horarios_cliente_id', table_name='configuracoes_horarios')
    op.drop_table('configuracoes_horarios')
