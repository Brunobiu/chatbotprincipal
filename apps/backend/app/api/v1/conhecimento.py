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
    modo: str = "substituir"  # "substituir" (padrão), "mesclar"


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
    Estrutura em JSON e gera embeddings automaticamente
    
    Modos:
    - "substituir" (padrão): Sobrescreve todo o conhecimento
    - "mesclar": Mescla com conhecimento existente (atualização incremental)
    """
    import logging
    logger = logging.getLogger(__name__)
    from app.db.session import SessionLocal
    
    logger.info(f"💾 Atualizando conhecimento para cliente {cliente.id}: {len(request.conteudo_texto)} chars (modo: {request.modo})")
    
    db = SessionLocal()
    try:
        # Validar modo
        if request.modo not in ["substituir", "mesclar"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Modo inválido. Use: 'substituir' ou 'mesclar'"
            )
        
        # Atualizar conhecimento (estrutura + embeddings)
        conhecimento = ConhecimentoService.atualizar(
            db=db,
            cliente_id=cliente.id,
            conteudo=request.conteudo_texto,
            modo=request.modo
        )
        
        logger.info(f"✅ Conhecimento atualizado para cliente {cliente.id}")
        
        return {
            "conteudo_texto": conhecimento.conteudo_texto,
            "total_chars": len(conhecimento.conteudo_texto),
            "max_chars": ConhecimentoService.MAX_CHARS
        }
    except ValueError as e:
        logger.error(f"❌ Erro de validação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao atualizar conhecimento: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar conhecimento: {str(e)}"
        )
    finally:
        db.close()


async def gerar_embeddings_background(cliente_id: int, conteudo: str):
    """
    Gera embeddings em background sem bloquear a requisição HTTP
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔄 [BACKGROUND] Iniciando geração de embeddings para cliente {cliente_id}")
        
        # Gerar chunks
        chunks = ConhecimentoService.gerar_chunks(conteudo)
        logger.info(f"✅ [BACKGROUND] {len(chunks)} chunks gerados para cliente {cliente_id}")
        
        # Gerar embeddings
        from app.services.rag.vectorstore import criar_vectorstore_de_chunks
        criar_vectorstore_de_chunks(cliente_id, chunks)
        
        logger.info(f"✅ [BACKGROUND] Embeddings gerados com sucesso para cliente {cliente_id}")
        
    except Exception as e:
        logger.error(f"❌ [BACKGROUND] Erro ao gerar embeddings para cliente {cliente_id}: {e}", exc_info=True)


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
