"""add security fields

Revision ID: 023
Revises: 022
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '023'
down_revision = '022'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campos de segurança na tabela clientes
    op.add_column('clientes', sa.Column('tentativas_login_falhas', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('clientes', sa.Column('bloqueado_ate', sa.DateTime(), nullable=True))
    op.add_column('clientes', sa.Column('ultimo_ip_falha', sa.String(45), nullable=True))
    op.add_column('clientes', sa.Column('refresh_token_hash', sa.String(255), nullable=True))
    op.add_column('clientes', sa.Column('refresh_token_expira_em', sa.DateTime(), nullable=True))
    
    # Criar índices para performance
    op.create_index('ix_clientes_bloqueado_ate', 'clientes', ['bloqueado_ate'])
    
    # Criar tabela de logs de autenticação
    op.create_table(
        'logs_autenticacao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('email_tentativa', sa.String(255), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('sucesso', sa.Boolean(), nullable=False),
        sa.Column('motivo_falha', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_logs_autenticacao_cliente_id', 'logs_autenticacao', ['cliente_id'])
    op.create_index('ix_logs_autenticacao_email_tentativa', 'logs_autenticacao', ['email_tentativa'])
    op.create_index('ix_logs_autenticacao_ip_address', 'logs_autenticacao', ['ip_address'])
    op.create_index('ix_logs_autenticacao_created_at', 'logs_autenticacao', ['created_at'])
    op.create_index('ix_logs_autenticacao_sucesso', 'logs_autenticacao', ['sucesso'])


def downgrade():
    # Remover tabela de logs
    op.drop_index('ix_logs_autenticacao_sucesso', table_name='logs_autenticacao')
    op.drop_index('ix_logs_autenticacao_created_at', table_name='logs_autenticacao')
    op.drop_index('ix_logs_autenticacao_ip_address', table_name='logs_autenticacao')
    op.drop_index('ix_logs_autenticacao_email_tentativa', table_name='logs_autenticacao')
    op.drop_index('ix_logs_autenticacao_cliente_id', table_name='logs_autenticacao')
    op.drop_table('logs_autenticacao')
    
    # Remover índices e campos da tabela clientes
    op.drop_index('ix_clientes_bloqueado_ate', table_name='clientes')
    op.drop_column('clientes', 'refresh_token_expira_em')
    op.drop_column('clientes', 'refresh_token_hash')
    op.drop_column('clientes', 'ultimo_ip_falha')
    op.drop_column('clientes', 'bloqueado_ate')
    op.drop_column('clientes', 'tentativas_login_falhas')
