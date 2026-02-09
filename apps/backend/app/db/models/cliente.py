import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, DECIMAL
from sqlalchemy.orm import relationship

from app.db.base import Base


class ClienteStatus(str, enum.Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    PENDENTE = "pendente"
    SUSPENSO = "suspenso"


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    nome_empresa = Column(String(255), nullable=True)  # Nome da empresa do cliente
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=True)
    senha_hash = Column(String(255), nullable=False)
    status = Column(SQLEnum(ClienteStatus), default=ClienteStatus.PENDENTE, nullable=False)
    # Stripe fields
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True, index=True)
    stripe_status = Column(String(50), nullable=True)
    # Trial fields (FASE A)
    trial_starts_at = Column(DateTime, nullable=True)
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_status = Column(String(20), default='trial', nullable=False)
    # Billing fields (FASE E)
    plano = Column(String(20), nullable=True)  # 'mensal', 'trimestral', 'semestral'
    plano_preco = Column(DECIMAL(10, 2), nullable=True)  # Preço mensal
    plano_valor_total = Column(DECIMAL(10, 2), nullable=True)  # Valor total por período
    proxima_cobranca = Column(DateTime, nullable=True)
    plano_pendente = Column(String(20), nullable=True)  # Mudança de plano agendada
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Tracking fields (FASE 16.3)
    ultimo_login = Column(DateTime, nullable=True, index=True)
    ip_ultimo_login = Column(String(45), nullable=True)  # IPv6 pode ter até 45 chars
    total_mensagens_enviadas = Column(Integer, default=0, nullable=False)
    
    # Anti-abuse fields (Proteção Trial)
    ip_cadastro = Column(String(45), nullable=True)  # IP usado no cadastro
    device_fingerprint = Column(String(255), nullable=True)  # Fingerprint do navegador
    whatsapp_number = Column(String(20), nullable=True)  # Número WhatsApp conectado
    telefone_cadastro = Column(String(20), nullable=True)  # Telefone usado no cadastro
    telefone_verificado = Column(Integer, default=0, nullable=False)  # 0 = não verificado, 1 = verificado
    
    # Admin usando ferramenta (Task 12.1)
    eh_cliente_admin = Column(Integer, default=0, nullable=False)  # 0 = cliente normal, 1 = admin usando ferramenta
    admin_vinculado_id = Column(Integer, nullable=True, index=True)  # ID do admin que criou este cliente
    
    # Campos de segurança (FASE 1)
    tentativas_login_falhas = Column(Integer, default=0, nullable=False)
    bloqueado_ate = Column(DateTime, nullable=True, index=True)
    ultimo_ip_falha = Column(String(45), nullable=True)
    refresh_token_hash = Column(String(255), nullable=True)
    refresh_token_expira_em = Column(DateTime, nullable=True)

    # Relacionamentos
    conversas = relationship("Conversa", back_populates="cliente", cascade="all, delete-orphan")
    configuracao_bot = relationship("ConfiguracaoBot", back_populates="cliente", uselist=False, cascade="all, delete-orphan")
    conhecimento = relationship("Conhecimento", back_populates="cliente", uselist=False, cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="cliente", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome}', email='{self.email}', status='{self.status}')>"
