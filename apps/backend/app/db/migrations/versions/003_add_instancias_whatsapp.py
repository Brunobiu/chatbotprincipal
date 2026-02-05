"""add instancias whatsapp table

Revision ID: 003
Revises: 002
Create Date: 2026-02-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('instancias_whatsapp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('instance_id', sa.String(length=255), nullable=False),
        sa.Column('numero', sa.String(length=20), nullable=True),
        sa.Column('status', sa.Enum('PENDENTE', 'CONECTADA', 'DESCONECTADA', 'ERRO', name='instanciastatus'), nullable=False),
        sa.Column('qr_code', sa.String(length=2000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('instance_id')
    )
    op.create_index(op.f('ix_instancias_whatsapp_cliente_id'), 'instancias_whatsapp', ['cliente_id'], unique=False)
    op.create_index(op.f('ix_instancias_whatsapp_id'), 'instancias_whatsapp', ['id'], unique=False)
    op.create_index(op.f('ix_instancias_whatsapp_instance_id'), 'instancias_whatsapp', ['instance_id'], unique=True)
    op.create_index(op.f('ix_instancias_whatsapp_numero'), 'instancias_whatsapp', ['numero'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_instancias_whatsapp_numero'), table_name='instancias_whatsapp')
    op.drop_index(op.f('ix_instancias_whatsapp_instance_id'), table_name='instancias_whatsapp')
    op.drop_index(op.f('ix_instancias_whatsapp_id'), table_name='instancias_whatsapp')
    op.drop_index(op.f('ix_instancias_whatsapp_cliente_id'), table_name='instancias_whatsapp')
    op.drop_table('instancias_whatsapp')
