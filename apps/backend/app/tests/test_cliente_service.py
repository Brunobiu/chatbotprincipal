"""
Testes para ClienteService
"""
import pytest
from bcrypt import checkpw

from app.services.clientes.cliente_service import ClienteService
from app.db.models.cliente import Cliente, ClienteStatus


@pytest.mark.unit
class TestClienteService:
    """Testes unitários para ClienteService"""
    
    def test_gerar_senha_aleatoria(self):
        """Testa geração de senha aleatória"""
        senha = ClienteService.gerar_senha_aleatoria()
        
        assert len(senha) == 12
        assert isinstance(senha, str)
        
        # Testar tamanho customizado
        senha_custom = ClienteService.gerar_senha_aleatoria(tamanho=20)
        assert len(senha_custom) == 20
    
    def test_hash_senha(self):
        """Testa hash de senha com bcrypt"""
        senha = "senha_teste_123"
        hash_senha = ClienteService.hash_senha(senha)
        
        assert isinstance(hash_senha, str)
        assert len(hash_senha) > 0
        assert hash_senha != senha
        
        # Verificar que o hash é válido
        assert checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))
    
    def test_criar_cliente_from_stripe(self, db_session, sample_cliente_data):
        """Testa criação de cliente a partir de dados do Stripe"""
        cliente, senha = ClienteService.criar_cliente_from_stripe(
            db=db_session,
            **sample_cliente_data
        )
        
        # Verificar cliente criado
        assert cliente.id is not None
        assert cliente.email == sample_cliente_data["email"]
        assert cliente.nome == sample_cliente_data["nome"]
        assert cliente.stripe_customer_id == sample_cliente_data["stripe_customer_id"]
        assert cliente.stripe_subscription_id == sample_cliente_data["stripe_subscription_id"]
        assert cliente.status == ClienteStatus.ATIVO
        
        # Verificar senha
        assert senha is not None
        assert len(senha) == 12
        assert checkpw(senha.encode('utf-8'), cliente.senha_hash.encode('utf-8'))
    
    def test_criar_cliente_duplicado(self, db_session, sample_cliente_data):
        """Testa que cliente duplicado atualiza ao invés de criar novo"""
        # Criar primeiro cliente
        cliente1, senha1 = ClienteService.criar_cliente_from_stripe(
            db=db_session,
            **sample_cliente_data
        )
        
        # Tentar criar novamente com mesmo email
        cliente2, senha2 = ClienteService.criar_cliente_from_stripe(
            db=db_session,
            **sample_cliente_data
        )
        
        # Deve ser o mesmo cliente
        assert cliente1.id == cliente2.id
        assert senha2 is None  # Não gera nova senha para cliente existente
    
    def test_atualizar_status_subscription_ativo(self, db_session, sample_cliente_data):
        """Testa atualização de status para ativo"""
        # Criar cliente
        cliente, _ = ClienteService.criar_cliente_from_stripe(
            db=db_session,
            **sample_cliente_data
        )
        
        # Atualizar status
        cliente_atualizado = ClienteService.atualizar_status_subscription(
            db=db_session,
            stripe_subscription_id=sample_cliente_data["stripe_subscription_id"],
            novo_status="active"
        )
        
        assert cliente_atualizado is not None
        assert cliente_atualizado.id == cliente.id
        assert cliente_atualizado.stripe_status == "active"
        assert cliente_atualizado.status == ClienteStatus.ATIVO
    
    def test_atualizar_status_subscription_cancelado(self, db_session, sample_cliente_data):
        """Testa atualização de status para cancelado"""
        # Criar cliente
        cliente, _ = ClienteService.criar_cliente_from_stripe(
            db=db_session,
            **sample_cliente_data
        )
        
        # Cancelar subscription
        cliente_atualizado = ClienteService.atualizar_status_subscription(
            db=db_session,
            stripe_subscription_id=sample_cliente_data["stripe_subscription_id"],
            novo_status="canceled"
        )
        
        assert cliente_atualizado is not None
        assert cliente_atualizado.stripe_status == "canceled"
        assert cliente_atualizado.status == ClienteStatus.SUSPENSO
    
    def test_atualizar_status_subscription_inexistente(self, db_session):
        """Testa atualização de subscription que não existe"""
        cliente = ClienteService.atualizar_status_subscription(
            db=db_session,
            stripe_subscription_id="sub_inexistente",
            novo_status="active"
        )
        
        assert cliente is None
    
    def test_buscar_por_email(self, db_session, sample_cliente_data):
        """Testa busca de cliente por email"""
        # Criar cliente
        cliente_criado, _ = ClienteService.criar_cliente_from_stripe(
            db=db_session,
            **sample_cliente_data
        )
        
        # Buscar por email
        cliente_encontrado = ClienteService.buscar_por_email(
            db=db_session,
            email=sample_cliente_data["email"]
        )
        
        assert cliente_encontrado is not None
        assert cliente_encontrado.id == cliente_criado.id
        assert cliente_encontrado.email == sample_cliente_data["email"]
    
    def test_buscar_por_email_inexistente(self, db_session):
        """Testa busca de cliente que não existe"""
        cliente = ClienteService.buscar_por_email(
            db=db_session,
            email="inexistente@exemplo.com"
        )
        
        assert cliente is None
    
    def test_buscar_por_id(self, db_session, sample_cliente_data):
        """Testa busca de cliente por ID"""
        # Criar cliente
        cliente_criado, _ = ClienteService.criar_cliente_from_stripe(
            db=db_session,
            **sample_cliente_data
        )
        
        # Buscar por ID
        cliente_encontrado = ClienteService.buscar_por_id(
            db=db_session,
            cliente_id=cliente_criado.id
        )
        
        assert cliente_encontrado is not None
        assert cliente_encontrado.id == cliente_criado.id
    
    def test_buscar_por_id_inexistente(self, db_session):
        """Testa busca de cliente com ID que não existe"""
        cliente = ClienteService.buscar_por_id(
            db=db_session,
            cliente_id=99999
        )
        
        assert cliente is None
