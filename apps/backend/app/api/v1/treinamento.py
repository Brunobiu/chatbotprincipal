"""
Rotas de Treinamento de IA
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.services.treinamento_service import TreinamentoService

router = APIRouter()


class MarcarConversaRequest(BaseModel):
    """Request para marcar conversa"""
    conversa_id: int
    avaliacao: str  # 'boa' ou 'ruim'


@router.get("/conversas")
def get_conversas(
    cliente_id: int = None,
    avaliacao: str = None,
    busca: str = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Lista todas as conversas com filtros"""
    resultado = TreinamentoService.get_todas_conversas(
        db, cliente_id, avaliacao, busca, page, limit
    )
    
    # Formatar resposta
    conversas_formatadas = []
    for conv in resultado['conversas']:
        conversas_formatadas.append({
            'id': conv.id,
            'cliente_id': conv.cliente_id,
            'cliente_nome': conv.cliente.nome if conv.cliente else 'Desconhecido',
            'whatsapp': conv.numero_usuario,
            'status': conv.estado,
            'avaliacao': conv.avaliacao,
            'created_at': conv.created_at.isoformat(),
            'mensagens_count': 0  # TODO: Contar mensagens
        })
    
    return {
        'conversas': conversas_formatadas,
        'total': resultado['total'],
        'page': resultado['page'],
        'pages': resultado['pages']
    }


@router.post("/marcar")
def marcar_conversa(
    request: MarcarConversaRequest,
    db: Session = Depends(get_db)
):
    """Marca conversa como boa ou ruim"""
    try:
        conversa = TreinamentoService.marcar_conversa(
            db, request.conversa_id, request.avaliacao
        )
        return {
            'message': f'Conversa marcada como {request.avaliacao}',
            'conversa_id': conversa.id
        }
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/analise")
def get_analise(db: Session = Depends(get_db)):
    """Retorna análise de treinamento"""
    return TreinamentoService.get_analise_treinamento(db)
