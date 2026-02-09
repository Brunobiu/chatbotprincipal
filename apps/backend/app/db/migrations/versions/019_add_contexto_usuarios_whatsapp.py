"""add contexto usuarios whatsapp

Revision ID: 019
Revises: 018
Create Date: 2024-02-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '019'
down_revision = '018'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela contexto_usuarios_whatsapp
    op.create_table(
        'contexto_usuarios_whatsapp',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('cliente_id', sa.Integer(), sa.ForeignKey('clientes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('numero_usuario', sa.String(50), nullable=False),
        sa.Column('nome', sa.String(200), nullable=True),
        sa.Column('primeira_interacao', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('ultima_interacao', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Criar índice único para cliente_id + numero_usuario
    op.create_index(
        'ix_contexto_usuarios_cliente_numero',
        'contexto_usuarios_whatsapp',
        ['cliente_id', 'numero_usuario'],
        unique=True
    )


def downgrade():
    op.drop_index('ix_contexto_usuarios_cliente_numero', table_name='contexto_usuarios_whatsapp')
    op.drop_table('contexto_usuarios_whatsapp')
