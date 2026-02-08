"""add tutoriais system

Revision ID: 015
Revises: 014
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela de tutoriais
    op.create_table(
        'tutoriais',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(200), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('video_url', sa.String(500), nullable=False),
        sa.Column('thumbnail_url', sa.String(500), nullable=True),
        sa.Column('ordem', sa.Integer(), default=0, nullable=False),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de visualizações
    op.create_table(
        'tutorial_visualizacoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tutorial_id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('visualizado_em', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['tutorial_id'], ['tutoriais.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tutorial_id', 'cliente_id', name='uq_tutorial_cliente')
    )
    
    # Tabela de comentários
    op.create_table(
        'tutorial_comentarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tutorial_id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('comentario', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['tutorial_id'], ['tutoriais.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Índices
    op.create_index('idx_tutoriais_ordem', 'tutoriais', ['ordem'])
    op.create_index('idx_tutoriais_ativo', 'tutoriais', ['ativo'])
    op.create_index('idx_tutorial_visualizacoes_cliente', 'tutorial_visualizacoes', ['cliente_id'])
    op.create_index('idx_tutorial_comentarios_tutorial', 'tutorial_comentarios', ['tutorial_id'])


def downgrade():
    op.drop_index('idx_tutorial_comentarios_tutorial', 'tutorial_comentarios')
    op.drop_index('idx_tutorial_visualizacoes_cliente', 'tutorial_visualizacoes')
    op.drop_index('idx_tutoriais_ativo', 'tutoriais')
    op.drop_index('idx_tutoriais_ordem', 'tutoriais')
    op.drop_table('tutorial_comentarios')
    op.drop_table('tutorial_visualizacoes')
    op.drop_table('tutoriais')
