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
    cliente = Depends(get_current_cliente)
):
    """
    Retorna conhecimento do cliente autenticado
    Busca do banco de dados
    """
    from app.db.session import SessionLocal
    
    db = SessionLocal()
    try:
        conhecimento = ConhecimentoService.buscar_ou_criar(db, cliente.id)
        return {
            "conteudo_texto": conhecimento.conteudo_texto or "",
            "total_chars": len(conhecimento.conteudo_texto or ""),
            "max_chars": ConhecimentoService.MAX_CHARS
        }
    finally:
        db.close()


@router.put("/knowledge", response_model=ConhecimentoResponse)
async def update_conhecimento(
    request: ConhecimentoUpdateRequest,
    cliente = Depends(get_current_cliente)
):
    """
    Atualiza conhecimento do cliente autenticado
    Salva direto no banco SEM gerar embeddings (temporário)
    """
    import logging
    logger = logging.getLogger(__name__)
    from app.db.session import SessionLocal
    
    # Validar tamanho
    if len(request.conteudo_texto) > ConhecimentoService.MAX_CHARS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Conteúdo excede o limite de {ConhecimentoService.MAX_CHARS} caracteres"
        )
    
    logger.info(f"💾 Salvando conhecimento para cliente {cliente.id}: {len(request.conteudo_texto)} chars")
    
    db = SessionLocal()
    try:
        # Buscar ou criar conhecimento
        conhecimento = ConhecimentoService.buscar_ou_criar(db, cliente.id)
        
        # Atualizar conteúdo
        conhecimento.conteudo_texto = request.conteudo_texto
        
        # Salvar no banco
        db.commit()
        db.refresh(conhecimento)
        
        logger.info(f"✅ Conhecimento salvo com sucesso para cliente {cliente.id}")
        
        return {
            "conteudo_texto": conhecimento.conteudo_texto,
            "total_chars": len(conhecimento.conteudo_texto),
            "max_chars": ConhecimentoService.MAX_CHARS
        }
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao salvar conhecimento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar conhecimento: {str(e)}"
        )
    finally:
        db.close()


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
