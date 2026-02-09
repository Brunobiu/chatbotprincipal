"""
Endpoints de dicas da IA para admin
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.admin import Admin
from app.services.dicas.dicas_ia_service import DicasIAService


router = APIRouter()


# ==================== SCHEMAS ====================

class ObjetivoMensalRequest(BaseModel):
    """Schema para configurar objetivo mensal"""
    objetivo: float


class DicasResponse(BaseModel):
    """Schema para response de dicas"""
    conteudo: dict
    objetivo_mensal: float | None
    created_at: str
    deve_atualizar: bool


# ==================== ENDPOINTS ====================

@router.get("/", response_model=DicasResponse)
def obter_dicas(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Obtém dicas da IA para o admin
    
    Se passou 24h desde última atualização, gera novas dicas automaticamente
    """
    try:
        # Verificar se deve atualizar
        deve_atualizar = DicasIAService.deve_atualizar_dicas(db, admin.id)
        
        if deve_atualizar:
            # Gerar novas dicas
            conteudo = DicasIAService.gerar_dicas_diarias(db, admin.id)
            dicas = DicasIAService.obter_dicas_atuais(db, admin.id)
        else:
            # Buscar dicas existentes
            dicas = DicasIAService.obter_dicas_atuais(db, admin.id)
            
            if not dicas:
                # Gerar primeira vez
                conteudo = DicasIAService.gerar_dicas_diarias(db, admin.id)
                dicas = DicasIAService.obter_dicas_atuais(db, admin.id)
        
        if not dicas:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao obter dicas"
            )
        
        return {
            "conteudo": dicas["conteudo"],
            "objetivo_mensal": dicas["objetivo_mensal"],
            "created_at": dicas["created_at"],
            "deve_atualizar": deve_atualizar
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter dicas: {str(e)}"
        )


@router.post("/objetivo-mensal")
def configurar_objetivo(
    request: ObjetivoMensalRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Configura objetivo mensal de faturamento
    """
    try:
        sucesso = DicasIAService.configurar_objetivo_mensal(
            db=db,
            admin_id=admin.id,
            objetivo=request.objetivo
        )
        
        if not sucesso:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao configurar objetivo"
            )
        
        return {"message": "Objetivo configurado com sucesso"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao configurar objetivo: {str(e)}"
        )
