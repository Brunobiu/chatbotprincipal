from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func

from app.db.models.admin import LoginAttempt, IPBloqueado, AuditLog


class SegurancaService:
    """Serviço para gerenciar segurança e auditoria"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== LOGIN ATTEMPTS ====================
    
    def registrar_tentativa_login(
        self,
        email: str,
        ip: str,
        success: bool,
        user_agent: Optional[str] = None
    ) -> LoginAttempt:
        """Registra tentativa de login"""
        attempt = LoginAttempt(
            email=email,
            ip=ip,
            success=success,
            user_agent=user_agent
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        
        # Verificar se deve bloquear IP
        if not success:
            self._verificar_bloqueio_ip(ip)
        
        return attempt
    
    def _verificar_bloqueio_ip(self, ip: str):
        """Verifica se IP deve ser bloqueado (5 falhas em 15 minutos)"""
        limite_tempo = datetime.utcnow() - timedelta(minutes=15)
        
        falhas = self.db.query(LoginAttempt).filter(
            LoginAttempt.ip == ip,
            LoginAttempt.success == False,
            LoginAttempt.created_at >= limite_tempo
        ).count()
        
        if falhas >= 5:
            # Bloquear IP por 1 hora
            self.bloquear_ip(
                ip=ip,
                reason="Múltiplas tentativas de login falhadas",
                duracao_horas=1
            )
    
    def listar_tentativas_login(
        self,
        limit: int = 100,
        offset: int = 0,
        email: Optional[str] = None,
        ip: Optional[str] = None,
        success: Optional[bool] = None
    ) -> tuple[List[LoginAttempt], int]:
        """Lista tentativas de login"""
        query = self.db.query(LoginAttempt)
        
        if email:
            query = query.filter(LoginAttempt.email.ilike(f"%{email}%"))
        if ip:
            query = query.filter(LoginAttempt.ip == ip)
        if success is not None:
            query = query.filter(LoginAttempt.success == success)
        
        total = query.count()
        attempts = query.order_by(desc(LoginAttempt.created_at)).limit(limit).offset(offset).all()
        
        return attempts, total
    
    # ==================== IPS BLOQUEADOS ====================
    
    def bloquear_ip(
        self,
        ip: str,
        reason: str,
        duracao_horas: int = 24
    ) -> IPBloqueado:
        """Bloqueia um IP"""
        # Verificar se já está bloqueado
        bloqueio_existente = self.db.query(IPBloqueado).filter(
            IPBloqueado.ip == ip
        ).first()
        
        if bloqueio_existente:
            # Atualizar expiração
            bloqueio_existente.expires_at = datetime.utcnow() + timedelta(hours=duracao_horas)
            bloqueio_existente.reason = reason
            self.db.commit()
            return bloqueio_existente
        
        # Criar novo bloqueio
        bloqueio = IPBloqueado(
            ip=ip,
            reason=reason,
            expires_at=datetime.utcnow() + timedelta(hours=duracao_horas)
        )
        self.db.add(bloqueio)
        self.db.commit()
        self.db.refresh(bloqueio)
        
        return bloqueio
    
    def desbloquear_ip(self, ip: str) -> bool:
        """Desbloqueia um IP"""
        bloqueio = self.db.query(IPBloqueado).filter(IPBloqueado.ip == ip).first()
        if not bloqueio:
            return False
        
        self.db.delete(bloqueio)
        self.db.commit()
        
        return True
    
    def verificar_ip_bloqueado(self, ip: str) -> bool:
        """Verifica se IP está bloqueado"""
        agora = datetime.utcnow()
        
        bloqueio = self.db.query(IPBloqueado).filter(
            IPBloqueado.ip == ip,
            IPBloqueado.expires_at > agora
        ).first()
        
        return bloqueio is not None
    
    def listar_ips_bloqueados(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[IPBloqueado], int]:
        """Lista IPs bloqueados"""
        agora = datetime.utcnow()
        
        query = self.db.query(IPBloqueado).filter(
            IPBloqueado.expires_at > agora
        )
        
        total = query.count()
        bloqueios = query.order_by(desc(IPBloqueado.blocked_at)).limit(limit).offset(offset).all()
        
        return bloqueios, total
    
    # ==================== AUDIT LOG ====================
    
    def registrar_auditoria(
        self,
        admin_id: int,
        action: str,
        entity_type: str,
        entity_id: int,
        old_data: Optional[Dict] = None,
        new_data: Optional[Dict] = None,
        ip: Optional[str] = None
    ) -> AuditLog:
        """Registra ação de auditoria"""
        log = AuditLog(
            admin_id=admin_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_data=old_data,
            new_data=new_data,
            ip=ip
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def listar_audit_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        admin_id: Optional[int] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> tuple[List[AuditLog], int]:
        """Lista logs de auditoria"""
        query = self.db.query(AuditLog)
        
        if admin_id:
            query = query.filter(AuditLog.admin_id == admin_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if data_inicio:
            query = query.filter(AuditLog.created_at >= data_inicio)
        if data_fim:
            query = query.filter(AuditLog.created_at <= data_fim)
        
        total = query.count()
        logs = query.order_by(desc(AuditLog.created_at)).limit(limit).offset(offset).all()
        
        return logs, total
    
    # ==================== ESTATÍSTICAS ====================
    
    def obter_estatisticas_seguranca(self) -> Dict[str, Any]:
        """Obtém estatísticas de segurança"""
        # Últimas 24 horas
        limite_24h = datetime.utcnow() - timedelta(hours=24)
        
        # Tentativas de login
        total_tentativas_24h = self.db.query(LoginAttempt).filter(
            LoginAttempt.created_at >= limite_24h
        ).count()
        
        falhas_24h = self.db.query(LoginAttempt).filter(
            LoginAttempt.created_at >= limite_24h,
            LoginAttempt.success == False
        ).count()
        
        # IPs bloqueados ativos
        agora = datetime.utcnow()
        ips_bloqueados_ativos = self.db.query(IPBloqueado).filter(
            IPBloqueado.expires_at > agora
        ).count()
        
        # Ações de auditoria (últimas 24h)
        acoes_24h = self.db.query(AuditLog).filter(
            AuditLog.created_at >= limite_24h
        ).count()
        
        # Top IPs com mais falhas
        top_ips_falhas = self.db.query(
            LoginAttempt.ip,
            func.count(LoginAttempt.id).label('count')
        ).filter(
            LoginAttempt.created_at >= limite_24h,
            LoginAttempt.success == False
        ).group_by(LoginAttempt.ip).order_by(desc('count')).limit(5).all()
        
        return {
            "tentativas_login_24h": total_tentativas_24h,
            "falhas_login_24h": falhas_24h,
            "taxa_falha": round((falhas_24h / total_tentativas_24h * 100) if total_tentativas_24h > 0 else 0, 2),
            "ips_bloqueados_ativos": ips_bloqueados_ativos,
            "acoes_auditoria_24h": acoes_24h,
            "top_ips_falhas": [
                {"ip": ip, "falhas": count} for ip, count in top_ips_falhas
            ]
        }
