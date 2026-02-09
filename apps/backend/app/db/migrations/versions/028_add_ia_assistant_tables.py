"""add ia assistant tables

Revision ID: 028
Revises: 027
Create Date: 2026-02-09 15:17:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '028'
down_revision = '027'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela de mensagens da IA
    op.create_table(
        'ia_mensagens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tipo', sa.String(50), nullable=False, index=True),
        sa.Column('conteudo', sa.Text(), nullable=False),
        sa.Column('dados_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False)
    )
    
    op.create_index('idx_ia_mensagens_created_at', 'ia_mensagens', ['created_at'], postgresql_using='btree', postgresql_ops={'created_at': 'DESC'})
    
    # Tabela de objetivos do admin
    op.create_table(
        'admin_objetivos',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('meta_clientes_mes', sa.Integer(), default=10, nullable=False),
        sa.Column('meta_receita_mes', sa.DECIMAL(10, 2), default=5000.00, nullable=False),
        sa.Column('max_anuncios_percent', sa.Integer(), default=30, nullable=False),
        sa.Column('max_openai_percent', sa.Integer(), default=20, nullable=False),
        sa.Column('taxa_conversao_esperada', sa.Integer(), default=20, nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False)
    )
    
    # Inserir valores padrão
    op.execute("""
        INSERT INTO admin_objetivos (id, meta_clientes_mes, meta_receita_mes, max_anuncios_percent, max_openai_percent, taxa_conversao_esperada)
        VALUES (1, 10, 5000.00, 30, 20, 20)
    """)


def downgrade():
    op.drop_index('idx_ia_mensagens_created_at')
    op.drop_table('admin_objetivos')
    op.drop_table('ia_mensagens')
