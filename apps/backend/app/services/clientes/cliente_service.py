"""
Serviço para gerenciar clientes (CRUD e lógica de negócio)
"""
import secrets
import string
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from bcrypt import hashpw, gensalt

from app.db.models.cliente import Cliente, ClienteStatus


class ClienteService:
    """Serviço para operações com clientes"""
    
    @staticmethod
    def gerar_senha_aleatoria(tamanho: int = 12) -> str:
        """
        Gera uma senha aleatória segura
        
        Args:
            tamanho: Tamanho da senha (padrão: 12)
            
        Returns:
            Senha aleatória
        """
        caracteres = string.ascii_letters + string.digits + "!@#$%&*"
        return ''.join(secrets.choice(caracteres) for _ in range(tamanho))
    
    @staticmethod
    def hash_senha(senha: str) -> str:
        """
        Cria hash bcrypt da senha
        
        Args:
            senha: Senha em texto plano
            
        Returns:
            Hash da senha
        """
        return hashpw(senha.encode('utf-8'), gensalt()).decode('utf-8')
    
    @staticmethod
    def criar_cliente_from_stripe(
        db: Session,
        email: str,
        nome: str,
        stripe_customer_id: str,
        stripe_subscription_id: str,
        stripe_status: str,
        telefone: Optional[str] = None
    ) -> tuple[Cliente, str]:
        """
        Cria um novo cliente a partir de dados do Stripe
        
        Args:
            db: Sessão do banco de dados
            email: Email do cliente
            nome: Nome do cliente
            stripe_customer_id: ID do customer no Stripe
            stripe_subscription_id: ID da subscription no Stripe
            stripe_status: Status da subscription no Stripe
            telefone: Telefone do cliente (opcional)
            
        Returns:
            Tupla (cliente, senha_plana)
        """
        # Verifica se cliente já existe
        cliente_existente = db.query(Cliente).filter(Cliente.email == email).first()
        if cliente_existente:
            # Atualiza dados do Stripe
            cliente_existente.stripe_customer_id = stripe_customer_id
            cliente_existente.stripe_subscription_id = stripe_subscription_id
            cliente_existente.stripe_status = stripe_status
            cliente_existente.status = ClienteStatus.ATIVO
            cliente_existente.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(cliente_existente)
            return cliente_existente, None  # Não retorna senha para cliente existente
        
        # Gera senha aleatória
        senha_plana = ClienteService.gerar_senha_aleatoria()
        senha_hash = ClienteService.hash_senha(senha_plana)
        
        # Cria novo cliente
        novo_cliente = Cliente(
            nome=nome,
            email=email,
            telefone=telefone,
            senha_hash=senha_hash,
            status=ClienteStatus.ATIVO,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            stripe_status=stripe_status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)
        
        return novo_cliente, senha_plana
    
    @staticmethod
    def atualizar_status_subscription(
        db: Session,
        stripe_subscription_id: str,
        novo_status: str
    ) -> Optional[Cliente]:
        """
        Atualiza o status da subscription de um cliente
        
        Args:
            db: Sessão do banco de dados
            stripe_subscription_id: ID da subscription no Stripe
            novo_status: Novo status da subscription
            
        Returns:
            Cliente atualizado ou None se não encontrado
        """
        cliente = db.query(Cliente).filter(
            Cliente.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if not cliente:
            return None
        
        cliente.stripe_status = novo_status
        
        # Atualiza status do cliente baseado no status da subscription
        if novo_status in ['active', 'trialing']:
            cliente.status = ClienteStatus.ATIVO
        elif novo_status in ['canceled', 'unpaid']:
            cliente.status = ClienteStatus.SUSPENSO
        elif novo_status == 'incomplete':
            cliente.status = ClienteStatus.PENDENTE
        
        cliente.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(cliente)
        
        return cliente
    
    @staticmethod
    def buscar_por_email(db: Session, email: str) -> Optional[Cliente]:
        """
        Busca cliente por email
        
        Args:
            db: Sessão do banco de dados
            email: Email do cliente
            
        Returns:
            Cliente ou None se não encontrado
        """
        return db.query(Cliente).filter(Cliente.email == email).first()
    
    @staticmethod
    def buscar_por_id(db: Session, cliente_id: int) -> Optional[Cliente]:
        """
        Busca cliente por ID
        
        Args:
            db: Sessão do banco de dados
            cliente_id: ID do cliente
            
        Returns:
            Cliente ou None se não encontrado
        """
        return db.query(Cliente).filter(Cliente.id == cliente_id).first()
