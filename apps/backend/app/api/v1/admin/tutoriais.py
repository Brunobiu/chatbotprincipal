from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.core.security import get_current_admin
from app.db.models.admin import Admin
from app.services.tutoriais.tutorial_service import TutorialService


router = APIRouter()


# ==================== SCHEMAS ====================

class CriarTutorialRequest(BaseModel):
    titulo: str = Field(..., min_length=5, max_length=200)
    descricao: Optional[str] = None
    video_url: str = Field(..., min_length=10, max_length=500)
    thumbnail_url: Optional[str] = None


class AtualizarTutorialRequest(BaseModel):
    titulo: Optional[str] = Field(None, min_length=5, max_length=200)
    descricao: Optional[str] = None
    video_url: Optional[str] = Field(None, min_length=10, max_length=500)
    thumbnail_url: Optional[str] = None
    ativo: Optional[bool] = None


class ReordenarRequest(BaseModel):
    ordem: List[int]


class TutorialResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    video_url: str
    thumbnail_url: Optional[str]
    ordem: int
    ativo: bool
    created_at: str
    
    class Config:
        from_attributes = True


class TutorialComEstatisticasResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    video_url: str
    thumbnail_url: Optional[str]
    ordem: int
    ativo: bool
    created_at: str
    total_visualizacoes: int
    total_comentarios: int


# ==================== ENDPOINTS ====================

@router.post("/", response_model=TutorialResponse, status_code=status.HTTP_201_CREATED)
def criar_tutorial(
    request: CriarTutorialRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Cria um novo tutorial"""
    service = TutorialService(db)
    tutorial = service.criar_tutorial(
        titulo=request.titulo,
        descricao=request.descricao,
        video_url=request.video_url,
        thumbnail_url=request.thumbnail_url
    )
    
    return TutorialResponse(
        id=tutorial.id,
        titulo=tutorial.titulo,
        descricao=tutorial.descricao,
        video_url=tutorial.video_url,
        thumbnail_url=tutorial.thumbnail_url,
        ordem=tutorial.ordem,
        ativo=tutorial.ativo,
        created_at=tutorial.created_at.isoformat()
    )


@router.get("/", response_model=List[TutorialResponse])
def listar_tutoriais(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista todos os tutoriais"""
    service = TutorialService(db)
    tutoriais = service.listar_tutoriais_admin()
    
    return [
        TutorialResponse(
            id=t.id,
            titulo=t.titulo,
            descricao=t.descricao,
            video_url=t.video_url,
            thumbnail_url=t.thumbnail_url,
            ordem=t.ordem,
            ativo=t.ativo,
            created_at=t.created_at.isoformat()
        ) for t in tutoriais
    ]


@router.get("/{tutorial_id}", response_model=TutorialComEstatisticasResponse)
def obter_tutorial(
    tutorial_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Obtém um tutorial com estatísticas"""
    service = TutorialService(db)
    tutorial = service.obter_tutorial_admin(tutorial_id)
    
    if not tutorial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutorial não encontrado"
        )
    
    stats = service.obter_estatisticas_tutorial(tutorial_id)
    
    return TutorialComEstatisticasResponse(
        id=tutorial.id,
        titulo=tutorial.titulo,
        descricao=tutorial.descricao,
        video_url=tutorial.video_url,
        thumbnail_url=tutorial.thumbnail_url,
        ordem=tutorial.ordem,
        ativo=tutorial.ativo,
        created_at=tutorial.created_at.isoformat(),
        total_visualizacoes=stats["total_visualizacoes"],
        total_comentarios=stats["total_comentarios"]
    )


@router.put("/{tutorial_id}", response_model=TutorialResponse)
def atualizar_tutorial(
    tutorial_id: int,
    request: AtualizarTutorialRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Atualiza um tutorial"""
    service = TutorialService(db)
    tutorial = service.atualizar_tutorial(
        tutorial_id=tutorial_id,
        titulo=request.titulo,
        descricao=request.descricao,
        video_url=request.video_url,
        thumbnail_url=request.thumbnail_url,
        ativo=request.ativo
    )
    
    if not tutorial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutorial não encontrado"
        )
    
    return TutorialResponse(
        id=tutorial.id,
        titulo=tutorial.titulo,
        descricao=tutorial.descricao,
        video_url=tutorial.video_url,
        thumbnail_url=tutorial.thumbnail_url,
        ordem=tutorial.ordem,
        ativo=tutorial.ativo,
        created_at=tutorial.created_at.isoformat()
    )


@router.delete("/{tutorial_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_tutorial(
    tutorial_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Deleta um tutorial"""
    service = TutorialService(db)
    sucesso = service.deletar_tutorial(tutorial_id)
    
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutorial não encontrado"
        )
    
    return None


@router.put("/reordenar", status_code=status.HTTP_200_OK)
def reordenar_tutoriais(
    request: ReordenarRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reordena tutoriais"""
    service = TutorialService(db)
    sucesso = service.reordenar_tutoriais(request.ordem)
    
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao reordenar tutoriais"
        )
    
    return {"message": "Tutoriais reordenados com sucesso"}
