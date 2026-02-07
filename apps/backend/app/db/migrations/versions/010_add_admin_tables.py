"""add admin tables

Revision ID: 010
Revises: 009
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela admins
    op.create_table(
        'admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('senha_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='admin'),
        sa.Column('tema', sa.String(length=20), nullable=False, server_default='light'),
        sa.Column('cliente_especial_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.ForeignKeyConstraint(['cliente_especial_id'], ['clientes.id'], ondelete='SET NULL')
    )
    op.create_index('idx_admins_email', 'admins', ['email'])

    # Tabela login_attempts
    op.create_table(
        'login_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('ip', sa.String(length=45), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_login_attempts_ip', 'login_attempts', ['ip', 'created_at'])
    op.create_index('idx_login_attempts_email', 'login_attempts', ['email', 'created_at'])

    # Tabela ips_bloqueados
    op.create_table(
        'ips_bloqueados',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ip', sa.String(length=45), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('blocked_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ip')
    )
    op.create_index('idx_ips_bloqueados_ip', 'ips_bloqueados', ['ip'])
    op.create_index('idx_ips_bloqueados_expires', 'ips_bloqueados', ['expires_at'])

    # Tabela audit_log
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('old_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ondelete='SET NULL')
    )
    op.create_index('idx_audit_log_admin', 'audit_log', ['admin_id', 'created_at'])
    op.create_index('idx_audit_log_entity', 'audit_log', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_log_action', 'audit_log', ['action', 'created_at'])


def downgrade():
    op.drop_index('idx_audit_log_action', table_name='audit_log')
    op.drop_index('idx_audit_log_entity', table_name='audit_log')
    op.drop_index('idx_audit_log_admin', table_name='audit_log')
    op.drop_table('audit_log')
    
    op.drop_index('idx_ips_bloqueados_expires', table_name='ips_bloqueados')
    op.drop_index('idx_ips_bloqueados_ip', table_name='ips_bloqueados')
    op.drop_table('ips_bloqueados')
    
    op.drop_index('idx_login_attempts_email', table_name='login_attempts')
    op.drop_index('idx_login_attempts_ip', table_name='login_attempts')
    op.drop_table('login_attempts')
    
    op.drop_index('idx_admins_email', table_name='admins')
    op.drop_table('admins')
