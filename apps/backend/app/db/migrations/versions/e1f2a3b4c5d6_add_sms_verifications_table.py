"""add sms verifications table

Revision ID: e1f2a3b4c5d6
Revises: debdd01b9e4d
Create Date: 2026-02-09 18:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e1f2a3b4c5d6'
down_revision = 'debdd01b9e4d'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela sms_verifications
    op.create_table(
        'sms_verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telefone', sa.String(20), nullable=False),
        sa.Column('codigo', sa.String(6), nullable=False),
        sa.Column('verificado', sa.Boolean(), default=False, nullable=False),
        sa.Column('tentativas', sa.Integer(), default=0, nullable=False),
        sa.Column('expira_em', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índice para busca rápida por telefone
    op.create_index('ix_sms_verifications_telefone', 'sms_verifications', ['telefone'])


def downgrade():
    # Remover índice e tabela
    op.drop_index('ix_sms_verifications_telefone', table_name='sms_verifications')
    op.drop_table('sms_verifications')
