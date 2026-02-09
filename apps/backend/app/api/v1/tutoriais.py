"""
Endpoints de tutoriais para clientes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.services.tutoriais.tutorial_service import TutorialService
from app.services.clientes.cliente_service import ClienteService
from app.services.auth.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()


# Dependency para pegar cliente autenticado
def get_current_cliente(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency que valida o token JWT e retorna o cliente autenticado
    """
    token = credentials.credentials
    payload = AuthService.validar_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    cliente_id = int(payload.get("sub"))
    cliente = ClienteService.buscar_por_id(db, cliente_id)
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cliente não encontrado"
        )
    
    return cliente


# ==================== SCHEMAS ====================

class TutorialListaResponse(BaseModel):
    """Schema para lista de tutoriais"""
    id: int
    titulo: str
    descricao: Optional[str]
    video_url: str
    thumbnail_url: Optional[str]
    visualizado: bool
    created_at: str


class ComentarioResponse(BaseModel):
    """Schema para comentário"""
    id: int
    cliente_nome: str
    comentario: str
    created_at: str


class TutorialDetalheResponse(BaseModel):
    """Schema para detalhes do tutorial"""
    id: int
    titulo: str
    descricao: Optional[str]
    video_url: str
    thumbnail_url: Optional[str]
    visualizado: bool
    created_at: str
    comentarios: List[ComentarioResponse]


class AdicionarComentarioRequest(BaseModel):
    """Schema para adicionar comentário"""
    comentario: str = Field(..., min_length=1, max_length=1000)


# ==================== ENDPOINTS ====================

@router.get("/", response_model=List[TutorialListaResponse])
def listar_tutoriais(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Lista todos os tutoriais ativos para o cliente
    
    Requer token JWT válido no header Authorization: Bearer <token>
    Retorna tutoriais com status de visualização
    """
    service = TutorialService(db)
    tutoriais = service.listar_tutoriais_cliente(cliente.id)
    
    return tutoriais


@router.get("/{tutorial_id}", response_model=TutorialDetalheResponse)
def obter_tutorial(
    tutorial_id: int,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de um tutorial específico
    
    Requer token JWT válido no header Authorization: Bearer <token>
    Retorna tutorial com comentários
    """
    service = TutorialService(db)
    tutorial = service.obter_tutorial_cliente(tutorial_id, cliente.id)
    
    if not tutorial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutorial não encontrado"
        )
    
    return tutorial


@router.post("/{tutorial_id}/visualizar", status_code=status.HTTP_204_NO_CONTENT)
def marcar_visualizado(
    tutorial_id: int,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Marca tutorial como visualizado
    
    Requer token JWT válido no header Authorization: Bearer <token>
    """
    service = TutorialService(db)
    sucesso = service.marcar_visualizado(tutorial_id, cliente.id)
    
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao marcar como visualizado"
        )
    
    return None


@router.post("/{tutorial_id}/comentarios", response_model=ComentarioResponse, status_code=status.HTTP_201_CREATED)
def adicionar_comentario(
    tutorial_id: int,
    request: AdicionarComentarioRequest,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Adiciona comentário a um tutorial
    
    Requer token JWT válido no header Authorization: Bearer <token>
    """
    service = TutorialService(db)
    comentario = service.adicionar_comentario(
        tutorial_id=tutorial_id,
        cliente_id=cliente.id,
        comentario=request.comentario
    )
    
    if not comentario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutorial não encontrado"
        )
    
    return {
        "id": comentario.id,
        "cliente_nome": cliente.nome,
        "comentario": comentario.comentario,
        "created_at": comentario.created_at.isoformat()
    }


@router.get("/{tutorial_id}/comentarios", response_model=List[ComentarioResponse])
def listar_comentarios(
    tutorial_id: int,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Lista comentários de um tutorial
    
    Requer token JWT válido no header Authorization: Bearer <token>
    """
    service = TutorialService(db)
    comentarios = service.listar_comentarios(tutorial_id)
    
    return comentarios
