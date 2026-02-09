"""add ia config table

Revision ID: 029
Revises: 028
Create Date: 2026-02-09 15:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '029'
down_revision = '028'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela de configurações de IA
    op.create_table(
        'ia_configuracoes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('provedor', sa.String(20), nullable=False, unique=True),
        sa.Column('api_key_encrypted', sa.Text(), nullable=True),
        sa.Column('modelo', sa.String(50), nullable=False),
        sa.Column('ativo', sa.Boolean(), default=False, nullable=False),
        sa.Column('configurado', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False)
    )
    
    # Inserir configurações padrão
    op.execute("""
        INSERT INTO ia_configuracoes (provedor, modelo, ativo, configurado)
        VALUES 
            ('openai', 'gpt-4-turbo', TRUE, FALSE),
            ('anthropic', 'claude-3-opus', FALSE, FALSE),
            ('google', 'gemini-pro', FALSE, FALSE),
            ('xai', 'grok-beta', FALSE, FALSE),
            ('ollama', 'llama2', FALSE, FALSE)
    """)
    
    # Garantir apenas 1 ativo
    op.create_index('idx_ia_config_ativo', 'ia_configuracoes', ['ativo'], unique=True, postgresql_where=sa.text('ativo = TRUE'))


def downgrade():
    op.drop_index('idx_ia_config_ativo')
    op.drop_table('ia_configuracoes')
