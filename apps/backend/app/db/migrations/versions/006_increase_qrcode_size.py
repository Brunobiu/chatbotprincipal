"""increase qr_code field size

Revision ID: 006
Revises: 005
Create Date: 2026-02-07 18:58:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Aumentar tamanho do campo qr_code de 2000 para 20000 caracteres
    op.alter_column('instancias_whatsapp', 'qr_code',
                    existing_type=sa.String(length=2000),
                    type_=sa.Text(),
                    existing_nullable=True)


def downgrade() -> None:
    op.alter_column('instancias_whatsapp', 'qr_code',
                    existing_type=sa.Text(),
                    type_=sa.String(length=2000),
                    existing_nullable=True)
