"""
Serviço de Bloqueio de IPs (FASE 5)
Gerencia lista negra de IPs com comportamento suspeito
"""
from sqlalchemy.orm import Session
from app.db.models.blocked_ip import BlockedIP
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging
import json

logger = logging.getLogger("security")


class IPBlocker:
    """Gerencia bloqueio de IPs suspeitos"""
    
    @staticmethod
    def is_blocked(db: Session, ip: str) -> Tuple[bool, str]:
        """
        Verifica se IP está bloqueado
        
        Args:
            db: Sessão do banco
            ip: Endereço IP
            
        Returns:
            (is_blocked, reason)
        """
        blocked = db.query(BlockedIP).filter(
            BlockedIP.ip_address == ip
        ).first()
        
        if not blocked:
            return False, ""
        
        # Bloqueio permanente
        if blocked.is_permanent:
            logger.warning(f"🚫 IP bloqueado permanentemente tentou acessar: {ip}")
            return True, blocked.reason
        
        # Bloqueio temporário expirado
        if blocked.blocked_until and datetime.utcnow() > blocked.blocked_until:
            logger.info(f"✅ Bloqueio temporário expirado para IP: {ip}")
            db.delete(blocked)
            db.commit()
            return False, ""
        
        # Bloqueio temporário ainda ativo
        return True, blocked.reason
    
    @staticmethod
    def block_ip(
        db: Session,
        ip: str,
        reason: str,
        duration_minutes: Optional[int] = None,
        details: Optional[dict] = None
    ) -> BlockedIP:
        """
        Bloqueia IP
        
        Args:
            db: Sessão do banco
            ip: Endereço IP
            reason: Motivo do bloqueio
            duration_minutes: Duração em minutos (None = permanente)
            details: Detalhes adicionais (dict)
            
        Returns:
            BlockedIP criado/atualizado
        """
        blocked = db.query(BlockedIP).filter(
            BlockedIP.ip_address == ip
        ).first()
        
        if blocked:
            # Já bloqueado, incrementar contador
            blocked.attempts_count += 1
            blocked.last_attempt = datetime.utcnow()
            blocked.reason = reason  # Atualizar razão
            
            # Bloqueio progressivo: após 5 tentativas, tornar permanente
            if blocked.attempts_count >= 5:
                blocked.is_permanent = True
                blocked.blocked_until = None
                logger.error(
                    f"🚨 IP {ip} bloqueado PERMANENTEMENTE após {blocked.attempts_count} tentativas. "
                    f"Razão: {reason}"
                )
            else:
                # Aumentar duração do bloqueio
                if duration_minutes:
                    # Dobrar duração a cada tentativa
                    new_duration = duration_minutes * (2 ** (blocked.attempts_count - 1))
                    blocked.blocked_until = datetime.utcnow() + timedelta(minutes=new_duration)
                    logger.warning(
                        f"⚠️ IP {ip} bloqueado por {new_duration} minutos (tentativa {blocked.attempts_count}). "
                        f"Razão: {reason}"
                    )
        else:
            # Novo bloqueio
            blocked_until = None
            is_permanent = False
            
            if duration_minutes:
                blocked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
            else:
                is_permanent = True
            
            blocked = BlockedIP(
                ip_address=ip,
                reason=reason,
                blocked_until=blocked_until,
                is_permanent=is_permanent,
                details=json.dumps(details) if details else None
            )
            db.add(blocked)
            
            duration_str = f"{duration_minutes} minutos" if duration_minutes else "PERMANENTE"
            logger.warning(f"🔒 IP {ip} bloqueado por {duration_str}. Razão: {reason}")
        
        db.commit()
        db.refresh(blocked)
        return blocked
    
    @staticmethod
    def unblock_ip(db: Session, ip: str) -> bool:
        """
        Remove bloqueio de IP
        
        Args:
            db: Sessão do banco
            ip: Endereço IP
            
        Returns:
            True se desbloqueou, False se não estava bloqueado
        """
        blocked = db.query(BlockedIP).filter(
            BlockedIP.ip_address == ip
        ).first()
        
        if blocked:
            db.delete(blocked)
            db.commit()
            logger.info(f"✅ IP {ip} desbloqueado manualmente")
            return True
        
        return False
    
    @staticmethod
    def get_blocked_ips(db: Session, limit: int = 100) -> list:
        """
        Lista IPs bloqueados
        
        Args:
            db: Sessão do banco
            limit: Limite de resultados
            
        Returns:
            Lista de BlockedIP
        """
        return db.query(BlockedIP).order_by(
            BlockedIP.blocked_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def cleanup_expired(db: Session) -> int:
        """
        Remove bloqueios temporários expirados
        
        Returns:
            Número de IPs desbloqueados
        """
        expired = db.query(BlockedIP).filter(
            BlockedIP.is_permanent == False,
            BlockedIP.blocked_until < datetime.utcnow()
        ).all()
        
        count = len(expired)
        
        for blocked in expired:
            db.delete(blocked)
        
        db.commit()
        
        if count > 0:
            logger.info(f"🧹 Limpeza: {count} bloqueios temporários expirados removidos")
        
        return count
