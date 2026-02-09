"""add_phone_verification

Revision ID: 035_add_phone_verification
Revises: 034_add_whatsapp_trial
Create Date: 2026-02-09 18:16:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '035_add_phone_verification'
down_revision = '034_add_whatsapp_trial'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campos de telefone na tabela clientes
    op.add_column('clientes', sa.Column('telefone_cadastro', sa.String(20), nullable=True))
    op.add_column('clientes', sa.Column('telefone_verificado', sa.Boolean(), default=False, nullable=False))
    
    # Criar tabela sms_verification
    op.create_table(
        'sms_verification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telefone', sa.String(20), nullable=False),
        sa.Column('codigo', sa.String(6), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('verificado', sa.Boolean(), default=False, nullable=False),
        sa.Column('tentativas', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índice para busca rápida
    op.create_index('idx_sms_verification_telefone', 'sms_verification', ['telefone'])


def downgrade():
    # Remover índice e tabela
    op.drop_index('idx_sms_verification_telefone', table_name='sms_verification')
    op.drop_table('sms_verification')
    
    # Remover campos de telefone
    op.drop_column('clientes', 'telefone_verificado')
    op.drop_column('clientes', 'telefone_cadastro')
