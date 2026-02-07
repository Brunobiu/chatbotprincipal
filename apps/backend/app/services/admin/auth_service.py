"""
Serviço de autenticação e autorização de administradores.
"""
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from redis import Redis
import jwt

from app.db.models.admin import Admin, LoginAttempt, IPBloqueado
from app.core.security import verify_senha, hash_senha
from app.core.config import settings


class AdminAuthService:
    """Serviço para autenticação e autorização de administradores"""
    
    def __init__(self, db: Session, redis_client: Optional[Redis] = None):
        self.db = db
        self.redis = redis_client
        self.max_attempts = 5
        self.block_duration_minutes = 60
        self.attempt_window_minutes = 15
    
    def authenticate(self, email: str, password: str, ip: str, user_agent: Optional[str] = None) -> Optional[Admin]:
        """
        Autentica admin e retorna objeto ou None.
        
        Args:
            email: Email do admin
            password: Senha em texto plano
            ip: Endereço IP da requisição
            user_agent: User agent do navegador
            
        Returns:
            Admin object se autenticado, None caso contrário
        """
        # Verificar se IP está bloqueado
        if self.check_ip_blocked(ip):
            self.record_login_attempt(email, ip, False, user_agent)
            return None
        
        # Buscar admin por email
        admin = self.db.query(Admin).filter(Admin.email == email).first()
        
        if not admin:
            self.record_login_attempt(email, ip, False, user_agent)
            self._check_and_block_ip(ip)
            return None
        
        # Verificar senha
        if not verify_senha(password, admin.senha_hash):
            self.record_login_attempt(email, ip, False, user_agent)
            self._check_and_block_ip(ip)
            return None
        
        # Autenticação bem-sucedida
        self.record_login_attempt(email, ip, True, user_agent)
        return admin
    
    def generate_token(self, admin: Admin) -> str:
        """
        Gera JWT com role=admin.
        
        Args:
            admin: Objeto Admin
            
        Returns:
            JWT token string
        """
        payload = {
            "sub": str(admin.id),
            "email": admin.email,
            "role": "admin",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        # Cachear sessão no Redis se disponível
        if self.redis:
            self.redis.setex(
                f"admin_session:{admin.id}",
                86400,  # 24 horas
                token
            )
        
        return token
    
    def verify_token(self, token: str) -> Optional[Admin]:
        """
        Valida JWT e retorna admin.
        
        Args:
            token: JWT token
            
        Returns:
            Admin object se válido, None caso contrário
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            
            # Verificar se tem role admin
            if payload.get("role") != "admin":
                return None
            
            admin_id = int(payload.get("sub"))
            admin = self.db.query(Admin).filter(Admin.id == admin_id).first()
            
            return admin
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
    
    def check_ip_blocked(self, ip: str) -> bool:
        """
        Verifica se IP está bloqueado.
        
        Args:
            ip: Endereço IP
            
        Returns:
            True se bloqueado, False caso contrário
        """
        blocked = self.db.query(IPBloqueado).filter(
            IPBloqueado.ip == ip,
            IPBloqueado.expires_at > datetime.utcnow()
        ).first()
        
        return blocked is not None
    
    def record_login_attempt(self, email: str, ip: str, success: bool, user_agent: Optional[str] = None):
        """
        Registra tentativa de login.
        
        Args:
            email: Email tentado
            ip: Endereço IP
            success: Se foi bem-sucedido
            user_agent: User agent do navegador
        """
        attempt = LoginAttempt(
            email=email,
            ip=ip,
            success=success,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        
        self.db.add(attempt)
        self.db.commit()
    
    def block_ip(self, ip: str, duration_minutes: int = 60, reason: Optional[str] = None):
        """
        Bloqueia IP por período.
        
        Args:
            ip: Endereço IP
            duration_minutes: Duração do bloqueio em minutos
            reason: Motivo do bloqueio
        """
        # Verificar se já está bloqueado
        existing = self.db.query(IPBloqueado).filter(IPBloqueado.ip == ip).first()
        
        if existing:
            # Atualizar expiração
            existing.expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
            if reason:
                existing.reason = reason
        else:
            # Criar novo bloqueio
            blocked = IPBloqueado(
                ip=ip,
                reason=reason or "Múltiplas tentativas de login falhadas",
                blocked_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=duration_minutes)
            )
            self.db.add(blocked)
        
        self.db.commit()
    
    def unblock_ip(self, ip: str):
        """
        Desbloqueia um IP.
        
        Args:
            ip: Endereço IP
        """
        blocked = self.db.query(IPBloqueado).filter(IPBloqueado.ip == ip).first()
        
        if blocked:
            self.db.delete(blocked)
            self.db.commit()
    
    def _check_and_block_ip(self, ip: str):
        """
        Verifica tentativas recentes e bloqueia IP se necessário.
        
        Args:
            ip: Endereço IP
        """
        # Contar tentativas falhadas nos últimos X minutos
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.attempt_window_minutes)
        
        failed_attempts = self.db.query(LoginAttempt).filter(
            LoginAttempt.ip == ip,
            LoginAttempt.success == False,
            LoginAttempt.created_at >= cutoff_time
        ).count()
        
        # Bloquear se exceder limite
        if failed_attempts >= self.max_attempts:
            self.block_ip(ip, self.block_duration_minutes)
    
    def get_admin_by_id(self, admin_id: int) -> Optional[Admin]:
        """
        Busca admin por ID.
        
        Args:
            admin_id: ID do admin
            
        Returns:
            Admin object ou None
        """
        return self.db.query(Admin).filter(Admin.id == admin_id).first()
    
    def get_admin_by_email(self, email: str) -> Optional[Admin]:
        """
        Busca admin por email.
        
        Args:
            email: Email do admin
            
        Returns:
            Admin object ou None
        """
        return self.db.query(Admin).filter(Admin.email == email).first()
    
    def create_admin(self, nome: str, email: str, senha: str, role: str = "admin") -> Admin:
        """
        Cria um novo administrador.
        
        Args:
            nome: Nome do admin
            email: Email do admin
            senha: Senha em texto plano
            role: Role do admin (default: admin)
            
        Returns:
            Admin object criado
        """
        senha_hash = hash_senha(senha)
        
        admin = Admin(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            role=role,
            tema="light",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        
        return admin
