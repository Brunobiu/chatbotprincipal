from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.admin import Admin
from app.services.avisos.aviso_service import AvisoService


router = APIRouter()


# ==================== SCHEMAS ====================

class CriarAvisoRequest(BaseModel):
    tipo: str = Field(..., pattern="^(info|warning|error|success)$")
    titulo: str = Field(..., min_length=5, max_length=200)
    mensagem: str = Field(..., min_length=10)
    dismissivel: bool = True
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None


class AtualizarAvisoRequest(BaseModel):
    tipo: Optional[str] = Field(None, pattern="^(info|warning|error|success)$")
    titulo: Optional[str] = Field(None, min_length=5, max_length=200)
    mensagem: Optional[str] = Field(None, min_length=10)
    dismissivel: Optional[bool] = None
    ativo: Optional[bool] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None


class AvisoResponse(BaseModel):
    id: int
    tipo: str
    titulo: str
    mensagem: str
    ativo: bool
    dismissivel: bool
    data_inicio: Optional[str]
    data_fim: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.post("/", response_model=AvisoResponse, status_code=status.HTTP_201_CREATED)
def criar_aviso(
    request: CriarAvisoRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Cria um novo aviso"""
    service = AvisoService(db)
    
    data_inicio = datetime.fromisoformat(request.data_inicio) if request.data_inicio else None
    data_fim = datetime.fromisoformat(request.data_fim) if request.data_fim else None
    
    aviso = service.criar_aviso(
        tipo=request.tipo,
        titulo=request.titulo,
        mensagem=request.mensagem,
        dismissivel=request.dismissivel,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    return AvisoResponse(
        id=aviso.id,
        tipo=aviso.tipo,
        titulo=aviso.titulo,
        mensagem=aviso.mensagem,
        ativo=aviso.ativo,
        dismissivel=aviso.dismissivel,
        data_inicio=aviso.data_inicio.isoformat() if aviso.data_inicio else None,
        data_fim=aviso.data_fim.isoformat() if aviso.data_fim else None,
        created_at=aviso.created_at.isoformat()
    )


@router.get("/", response_model=List[AvisoResponse])
def listar_avisos(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista todos os avisos"""
    service = AvisoService(db)
    avisos = service.listar_avisos_admin()
    
    return [
        AvisoResponse(
            id=a.id,
            tipo=a.tipo,
            titulo=a.titulo,
            mensagem=a.mensagem,
            ativo=a.ativo,
            dismissivel=a.dismissivel,
            data_inicio=a.data_inicio.isoformat() if a.data_inicio else None,
            data_fim=a.data_fim.isoformat() if a.data_fim else None,
            created_at=a.created_at.isoformat()
        ) for a in avisos
    ]


@router.get("/{aviso_id}", response_model=AvisoResponse)
def obter_aviso(
    aviso_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Obtém um aviso"""
    service = AvisoService(db)
    aviso = service.obter_aviso_admin(aviso_id)
    
    if not aviso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso não encontrado"
        )
    
    return AvisoResponse(
        id=aviso.id,
        tipo=aviso.tipo,
        titulo=aviso.titulo,
        mensagem=aviso.mensagem,
        ativo=aviso.ativo,
        dismissivel=aviso.dismissivel,
        data_inicio=aviso.data_inicio.isoformat() if aviso.data_inicio else None,
        data_fim=aviso.data_fim.isoformat() if aviso.data_fim else None,
        created_at=aviso.created_at.isoformat()
    )


@router.put("/{aviso_id}", response_model=AvisoResponse)
def atualizar_aviso(
    aviso_id: int,
    request: AtualizarAvisoRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Atualiza um aviso"""
    service = AvisoService(db)
    
    data_inicio = datetime.fromisoformat(request.data_inicio) if request.data_inicio else None
    data_fim = datetime.fromisoformat(request.data_fim) if request.data_fim else None
    
    aviso = service.atualizar_aviso(
        aviso_id=aviso_id,
        tipo=request.tipo,
        titulo=request.titulo,
        mensagem=request.mensagem,
        dismissivel=request.dismissivel,
        ativo=request.ativo,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    if not aviso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso não encontrado"
        )
    
    return AvisoResponse(
        id=aviso.id,
        tipo=aviso.tipo,
        titulo=aviso.titulo,
        mensagem=aviso.mensagem,
        ativo=aviso.ativo,
        dismissivel=aviso.dismissivel,
        data_inicio=aviso.data_inicio.isoformat() if aviso.data_inicio else None,
        data_fim=aviso.data_fim.isoformat() if aviso.data_fim else None,
        created_at=aviso.created_at.isoformat()
    )


@router.delete("/{aviso_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_aviso(
    aviso_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Deleta um aviso"""
    service = AvisoService(db)
    sucesso = service.deletar_aviso(aviso_id)
    
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso não encontrado"
        )
    
    return None
