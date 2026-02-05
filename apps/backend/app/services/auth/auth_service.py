"""
Serviço de autenticação (login, JWT, validação)
"""
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.db.models.cliente import Cliente
from app.core.config import settings


class AuthService:
    """Serviço para autenticação de clientes"""
    
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
        return bcrypt.checkpw(senha_plana.encode('utf-8'), senha_hash.encode('utf-8'))
    
    @staticmethod
    def criar_token_acesso(cliente_id: int, email: str) -> str:
        """
        Cria um token JWT de acesso
        
        Args:
            cliente_id: ID do cliente
            email: Email do cliente
            
        Returns:
            Token JWT
        """
        expiracao = datetime.utcnow() + timedelta(days=7)  # Token válido por 7 dias
        
        payload = {
            "sub": str(cliente_id),
            "email": email,
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
    def validar_token(token: str) -> Optional[dict]:
        """
        Valida um token JWT e retorna o payload
        
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
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def autenticar(db: Session, email: str, senha: str) -> Optional[Cliente]:
        """
        Autentica um cliente com email e senha
        
        Args:
            db: Sessão do banco de dados
            email: Email do cliente
            senha: Senha em texto plano
            
        Returns:
            Cliente autenticado ou None se credenciais inválidas
        """
        cliente = db.query(Cliente).filter(Cliente.email == email).first()
        
        if not cliente:
            return None
        
        if not AuthService.verificar_senha(senha, cliente.senha_hash):
            return None
        
        return cliente
