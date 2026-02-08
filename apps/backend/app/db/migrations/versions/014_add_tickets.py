"""add tickets system

Revision ID: 014
Revises: 013
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade():
    # Tabela de categorias de tickets
    op.create_table(
        'ticket_categorias',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de tickets
    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('categoria_id', sa.Integer(), nullable=True),
        sa.Column('assunto', sa.String(200), nullable=False),
        sa.Column('status', sa.String(50), default='aberto', nullable=False),  # aberto, em_andamento, aguardando_cliente, resolvido, fechado
        sa.Column('prioridade', sa.String(20), default='normal', nullable=False),  # baixa, normal, alta, urgente
        sa.Column('atribuido_admin_id', sa.Integer(), nullable=True),
        sa.Column('ia_respondeu', sa.Boolean(), default=False, nullable=False),
        sa.Column('confianca_ia', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('resolvido_em', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['categoria_id'], ['ticket_categorias.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['atribuido_admin_id'], ['admins.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de mensagens dos tickets
    op.create_table(
        'ticket_mensagens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('remetente_tipo', sa.String(20), nullable=False),  # cliente, admin, ia
        sa.Column('remetente_id', sa.Integer(), nullable=True),
        sa.Column('mensagem', sa.Text(), nullable=False),
        sa.Column('anexos', JSONB, nullable=True),  # [{nome, url, tipo, tamanho}]
        sa.Column('lida', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Índices para performance
    op.create_index('idx_tickets_cliente_id', 'tickets', ['cliente_id'])
    op.create_index('idx_tickets_status', 'tickets', ['status'])
    op.create_index('idx_tickets_created_at', 'tickets', ['created_at'])
    op.create_index('idx_ticket_mensagens_ticket_id', 'ticket_mensagens', ['ticket_id'])
    
    # Inserir categorias padrão
    op.execute("""
        INSERT INTO ticket_categorias (nome, descricao, ativo) VALUES
        ('Financeiro', 'Dúvidas sobre pagamento, faturas e cobranças', true),
        ('Técnico', 'Problemas técnicos, bugs e erros', true),
        ('Dúvida', 'Dúvidas gerais sobre o uso da plataforma', true),
        ('WhatsApp', 'Problemas com conexão e mensagens do WhatsApp', true),
        ('Conhecimento', 'Dúvidas sobre base de conhecimento e IA', true),
        ('Outro', 'Outros assuntos', true)
    """)


def downgrade():
    op.drop_index('idx_ticket_mensagens_ticket_id', 'ticket_mensagens')
    op.drop_index('idx_tickets_created_at', 'tickets')
    op.drop_index('idx_tickets_status', 'tickets')
    op.drop_index('idx_tickets_cliente_id', 'tickets')
    op.drop_table('ticket_mensagens')
    op.drop_table('tickets')
    op.drop_table('ticket_categorias')
