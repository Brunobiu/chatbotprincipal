"""
Rotas para conhecimento do bot
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict

from app.db.session import get_db
from app.api.v1.auth import get_current_cliente
from app.services.conhecimento import ConhecimentoService


router = APIRouter()


# Schemas
class ConhecimentoResponse(BaseModel):
    """Schema para response de conhecimento"""
    conteudo_texto: str
    total_chars: int
    max_chars: int
    
    class Config:
        from_attributes = True


class ConhecimentoUpdateRequest(BaseModel):
    """Schema para request de atualização"""
    conteudo_texto: str


class ChunkResponse(BaseModel):
    """Schema para response de chunks (debug)"""
    total_chunks: int
    chunks: List[Dict]


@router.get("/knowledge", response_model=ConhecimentoResponse)
def get_conhecimento(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Retorna conhecimento do cliente autenticado
    Se não existir, cria vazio
    """
    conhecimento = ConhecimentoService.buscar_ou_criar(db, cliente.id)
    
    return {
        "conteudo_texto": conhecimento.conteudo_texto or "",
        "total_chars": len(conhecimento.conteudo_texto or ""),
        "max_chars": ConhecimentoService.MAX_CHARS
    }


@router.put("/knowledge", response_model=ConhecimentoResponse)
def update_conhecimento(
    request: ConhecimentoUpdateRequest,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Atualiza conhecimento do cliente autenticado
    Valida limite de 50.000 caracteres
    """
    try:
        conhecimento = ConhecimentoService.atualizar(
            db=db,
            cliente_id=cliente.id,
            conteudo=request.conteudo_texto
        )
        
        return {
            "conteudo_texto": conhecimento.conteudo_texto or "",
            "total_chars": len(conhecimento.conteudo_texto or ""),
            "max_chars": ConhecimentoService.MAX_CHARS
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/knowledge/chunks", response_model=ChunkResponse)
def get_chunks(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Retorna chunks do conhecimento (para debug/visualização)
    """
    conhecimento = ConhecimentoService.buscar_ou_criar(db, cliente.id)
    chunks = ConhecimentoService.gerar_chunks(conhecimento.conteudo_texto or "")
    
    return {
        "total_chunks": len(chunks),
        "chunks": chunks
    }


@router.get("/knowledge/search")
def search_conhecimento(
    q: str,
    k: int = 5,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Busca semântica no conhecimento do cliente
    
    Query params:
    - q: texto da busca
    - k: número de resultados (default: 5)
    """
    from app.services.rag.vectorstore import buscar_no_vectorstore
    
    results = buscar_no_vectorstore(cliente.id, q, k)
    
    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }
