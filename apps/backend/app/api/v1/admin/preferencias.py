from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.admin import Admin


router = APIRouter()


# ==================== SCHEMAS ====================

class AtualizarTemaRequest(BaseModel):
    tema: str  # "light" ou "dark"


class PreferenciasResponse(BaseModel):
    tema: str
    
    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.get("", response_model=PreferenciasResponse)
def obter_preferencias(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Obtém preferências do admin"""
    return PreferenciasResponse(tema=admin.tema)


@router.put("", response_model=PreferenciasResponse)
def atualizar_preferencias(
    request: AtualizarTemaRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Atualiza preferências do admin (tema)"""
    
    # Validar tema
    if request.tema not in ["light", "dark"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tema deve ser 'light' ou 'dark'"
        )
    
    # Atualizar tema
    admin.tema = request.tema
    db.commit()
    
    return PreferenciasResponse(tema=admin.tema)
