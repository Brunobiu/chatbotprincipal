"""
Serviço de autenticação V2 com segurança aprimorada (FASE 1)
- JWT com expiração curta (15 min)
- Refresh tokens (7 dias)
- Rate limiting
- Bloqueio de conta
- Logs de autenticação
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import secrets
import hashlib

import bcrypt
import jwt
from sqlalchemy.orm import Session
from fastapi import Request

from app.db.models.cliente import Cliente
from app.db.models.log_autenticacao import LogAutenticacao
from app.core.config import settings


class AuthServiceV2:
    """Serviço de autenticação com segurança aprimorada"""
    
    # Configurações de segurança
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Token de acesso expira em 15 minutos
    REFRESH_TOKEN_EXPIRE_DAYS = 7  # Refresh token expira em 7 dias
    MAX_LOGIN_ATTEMPTS = 5  # Máximo de tentativas de login
    LOCKOUT_DURATION_MINUTES = 15  # Duração do bloqueio em minutos
    BCRYPT_ROUNDS = 12  # Custo do bcrypt (mínimo recomendado)
    
    @staticmethod
    def hash_senha(senha: str) -> str:
        """
        Cria hash bcrypt da senha com cost factor adequado
        
        Args:
            senha: Senha em texto plano
            
        Returns:
            Hash bcrypt da senha
        """
        salt = bcrypt.gensalt(rounds=AuthServiceV2.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(senha.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
        """
        Verifica se a senha corresponde ao hash
        
        Args:
            senha_plana: Senha em texto plano
            senha_hash: Hash da senha armazenado
            
        Returns:
            True se a senha está correta, False caso contrário
        """
        try:
            return bcrypt.checkpw(senha_plana.encode('utf-8'), senha_hash.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def criar_access_token(cliente_id: int, email: str) -> str:
        """
        Cria um token JWT de acesso com expiração curta (15 min)
        
        Args:
            cliente_id: ID do cliente
            email: Email do cliente
            
        Returns:
            Token JWT de acesso
        """
        expiracao = datetime.utcnow() + timedelta(minutes=AuthServiceV2.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": str(cliente_id),
            "email": email,
            "type": "access",
            "exp": expiracao,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        
        return token
    
    @staticmethod
    def criar_refresh_token() -> str:
        """
        Cria um refresh token aleatório e seguro
        
        Returns:
            Refresh token (64 caracteres hex)
        """
        return secrets.token_hex(32)  # 64 caracteres
    
    @staticmethod
    def hash_refresh_token(token: str) -> str:
        """
        Cria hash SHA-256 do refresh token para armazenamento seguro
        
        Args:
            token: Refresh token em texto plano
            
        Returns:
            Hash SHA-256 do token
        """
        return hashlib.sha256(token.encode('utf-8')).hexdigest()
    
    @staticmethod
    def validar_access_token(token: str) -> Optional[dict]:
        """
        Valida um token JWT de acesso e retorna o payload
        
        Args:
            token: Token JWT
            
        Returns:
            Payload do token ou None se inválido
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            
            # Verificar se é um access token
            if payload.get("type") != "access":
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def verificar_conta_bloqueada(cliente: Cliente) -> Tuple[bool, Optional[str]]:
        """
        Verifica se a conta está bloqueada
        
        Args:
            cliente: Cliente a verificar
            
        Returns:
            Tupla (bloqueado, motivo)
        """
        # Verificar se conta está bloqueada temporariamente
        if cliente.bloqueado_ate and cliente.bloqueado_ate > datetime.utcnow():
            tempo_restante = (cliente.bloqueado_ate - datetime.utcnow()).seconds // 60
            return True, f"Conta bloqueada. Tente novamente em {tempo_restante} minutos"
        
        return False, None
    
    @staticmethod
    def registrar_tentativa_login(
        db: Session,
        email: str,
        ip_address: str,
        user_agent: Optional[str],
        sucesso: bool,
        motivo_falha: Optional[str] = None,
        cliente_id: Optional[int] = None
    ):
        """
        Registra tentativa de login no banco de dados
        
        Args:
            db: Sessão do banco
            email: Email da tentativa
            ip_address: IP de origem
            user_agent: User agent do navegador
            sucesso: Se o login foi bem-sucedido
            motivo_falha: Motivo da falha (se aplicável)
            cliente_id: ID do cliente (se existe)
        """
        log = LogAutenticacao(
            cliente_id=cliente_id,
            email_tentativa=email,
            ip_address=ip_address,
            user_agent=user_agent,
            sucesso=sucesso,
            motivo_falha=motivo_falha
        )
        db.add(log)
        db.commit()
    
    @staticmethod
    def processar_falha_login(db: Session, cliente: Cliente, ip_address: str):
        """
        Processa falha de login: incrementa contador e bloqueia se necessário
        
        Args:
            db: Sessão do banco
            cliente: Cliente que falhou no login
            ip_address: IP de origem
        """
        cliente.tentativas_login_falhas += 1
        cliente.ultimo_ip_falha = ip_address
        
        # Bloquear conta se atingiu o limite
        if cliente.tentativas_login_falhas >= AuthServiceV2.MAX_LOGIN_ATTEMPTS:
            cliente.bloqueado_ate = datetime.utcnow() + timedelta(
                minutes=AuthServiceV2.LOCKOUT_DURATION_MINUTES
            )
        
        db.commit()
    
    @staticmethod
    def resetar_tentativas_login(db: Session, cliente: Cliente):
        """
        Reseta contador de tentativas após login bem-sucedido
        
        Args:
            db: Sessão do banco
            cliente: Cliente que fez login com sucesso
        """
        cliente.tentativas_login_falhas = 0
        cliente.bloqueado_ate = None
        cliente.ultimo_ip_falha = None
        db.commit()
    
    @staticmethod
    def autenticar(
        db: Session,
        email: str,
        senha: str,
        request: Request
    ) -> Tuple[Optional[Cliente], Optional[str], Optional[str]]:
        """
        Autentica um cliente com email e senha
        Retorna cliente, access_token e refresh_token se bem-sucedido
        
        Args:
            db: Sessão do banco de dados
            email: Email do cliente
            senha: Senha em texto plano
            request: Request do FastAPI para extrair IP e user-agent
            
        Returns:
            Tupla (Cliente, access_token, refresh_token) ou (None, None, None) se falhou
        """
        # Extrair informações da requisição
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Buscar cliente
        cliente = db.query(Cliente).filter(Cliente.email == email).first()
        
        if not cliente:
            # Registrar tentativa com email inexistente
            AuthServiceV2.registrar_tentativa_login(
                db, email, ip_address, user_agent,
                sucesso=False, motivo_falha="email_nao_existe"
            )
            return None, None, None
        
        # Verificar se conta está bloqueada
        bloqueado, motivo = AuthServiceV2.verificar_conta_bloqueada(cliente)
        if bloqueado:
            AuthServiceV2.registrar_tentativa_login(
                db, email, ip_address, user_agent,
                sucesso=False, motivo_falha="conta_bloqueada",
                cliente_id=cliente.id
            )
            return None, None, None
        
        # Verificar senha
        if not AuthServiceV2.verificar_senha(senha, cliente.senha_hash):
            # Processar falha de login
            AuthServiceV2.processar_falha_login(db, cliente, ip_address)
            AuthServiceV2.registrar_tentativa_login(
                db, email, ip_address, user_agent,
                sucesso=False, motivo_falha="senha_incorreta",
                cliente_id=cliente.id
            )
            return None, None, None
        
        # Login bem-sucedido
        # Resetar tentativas
        AuthServiceV2.resetar_tentativas_login(db, cliente)
        
        # Atualizar último login
        cliente.ultimo_login = datetime.utcnow()
        cliente.ip_ultimo_login = ip_address
        
        # Criar tokens
        access_token = AuthServiceV2.criar_access_token(cliente.id, cliente.email)
        refresh_token = AuthServiceV2.criar_refresh_token()
        
        # Armazenar hash do refresh token
        cliente.refresh_token_hash = AuthServiceV2.hash_refresh_token(refresh_token)
        cliente.refresh_token_expira_em = datetime.utcnow() + timedelta(
            days=AuthServiceV2.REFRESH_TOKEN_EXPIRE_DAYS
        )
        
        db.commit()
        
        # Registrar login bem-sucedido
        AuthServiceV2.registrar_tentativa_login(
            db, email, ip_address, user_agent,
            sucesso=True, cliente_id=cliente.id
        )
        
        return cliente, access_token, refresh_token
    
    @staticmethod
    def refresh_access_token(
        db: Session,
        refresh_token: str,
        cliente_id: int
    ) -> Optional[str]:
        """
        Gera novo access token usando refresh token
        
        Args:
            db: Sessão do banco
            refresh_token: Refresh token fornecido
            cliente_id: ID do cliente
            
        Returns:
            Novo access token ou None se refresh token inválido
        """
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        if not cliente:
            return None
        
        # Verificar se refresh token existe e não expirou
        if not cliente.refresh_token_hash or not cliente.refresh_token_expira_em:
            return None
        
        if cliente.refresh_token_expira_em < datetime.utcnow():
            return None
        
        # Verificar se o hash do refresh token bate
        token_hash = AuthServiceV2.hash_refresh_token(refresh_token)
        if token_hash != cliente.refresh_token_hash:
            return None
        
        # Criar novo access token
        return AuthServiceV2.criar_access_token(cliente.id, cliente.email)
