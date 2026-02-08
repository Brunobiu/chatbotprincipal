from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.admin import Admin
from app.services.seguranca.seguranca_service import SegurancaService


router = APIRouter()


# ==================== SCHEMAS ====================

class LoginAttemptResponse(BaseModel):
    id: int
    email: str
    ip: str
    success: bool
    user_agent: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class IPBloqueadoResponse(BaseModel):
    id: int
    ip: str
    reason: Optional[str]
    blocked_at: str
    expires_at: str
    
    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    admin_id: Optional[int]
    action: str
    entity_type: str
    entity_id: int
    old_data: Optional[dict]
    new_data: Optional[dict]
    ip: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class EstatisticasResponse(BaseModel):
    tentativas_login_24h: int
    falhas_login_24h: int
    taxa_falha: float
    ips_bloqueados_ativos: int
    acoes_auditoria_24h: int
    top_ips_falhas: List[dict]


class DesbloquearIPRequest(BaseModel):
    ip: str


# ==================== ENDPOINTS ====================

@router.get("/estatisticas", response_model=EstatisticasResponse)
def obter_estatisticas(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de segurança"""
    service = SegurancaService(db)
    stats = service.obter_estatisticas_seguranca()
    return EstatisticasResponse(**stats)


@router.get("/tentativas-login")
def listar_tentativas_login(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    email: Optional[str] = None,
    ip: Optional[str] = None,
    success: Optional[bool] = None,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista tentativas de login"""
    service = SegurancaService(db)
    attempts, total = service.listar_tentativas_login(
        limit=limit,
        offset=offset,
        email=email,
        ip=ip,
        success=success
    )
    
    return {
        "attempts": [
            LoginAttemptResponse(
                id=a.id,
                email=a.email,
                ip=a.ip,
                success=a.success,
                user_agent=a.user_agent,
                created_at=a.created_at.isoformat()
            ) for a in attempts
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/ips-bloqueados")
def listar_ips_bloqueados(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista IPs bloqueados"""
    service = SegurancaService(db)
    bloqueios, total = service.listar_ips_bloqueados(
        limit=limit,
        offset=offset
    )
    
    return {
        "bloqueios": [
            IPBloqueadoResponse(
                id=b.id,
                ip=b.ip,
                reason=b.reason,
                blocked_at=b.blocked_at.isoformat(),
                expires_at=b.expires_at.isoformat()
            ) for b in bloqueios
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/desbloquear-ip")
def desbloquear_ip(
    request: DesbloquearIPRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Desbloqueia um IP"""
    service = SegurancaService(db)
    sucesso = service.desbloquear_ip(request.ip)
    
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP não encontrado ou já desbloqueado"
        )
    
    return {"message": f"IP {request.ip} desbloqueado com sucesso"}


@router.get("/audit-log")
def listar_audit_logs(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    admin_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista logs de auditoria"""
    service = SegurancaService(db)
    
    inicio = datetime.fromisoformat(data_inicio) if data_inicio else None
    fim = datetime.fromisoformat(data_fim) if data_fim else None
    
    logs, total = service.listar_audit_logs(
        limit=limit,
        offset=offset,
        admin_id=admin_id,
        action=action,
        entity_type=entity_type,
        data_inicio=inicio,
        data_fim=fim
    )
    
    return {
        "logs": [
            AuditLogResponse(
                id=l.id,
                admin_id=l.admin_id,
                action=l.action,
                entity_type=l.entity_type,
                entity_id=l.entity_id,
                old_data=l.old_data,
                new_data=l.new_data,
                ip=l.ip,
                created_at=l.created_at.isoformat()
            ) for l in logs
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }
