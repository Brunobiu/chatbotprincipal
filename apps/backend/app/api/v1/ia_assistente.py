"""
Rotas de IA Assistente para Admin
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.services.ia_assistente_service import IAAssistenteService
from app.db.models.ia_mensagem import IAMensagem
from app.db.models.admin_objetivos import AdminObjetivos

router = APIRouter()


class ResumoAtualResponse(BaseModel):
    """Response do resumo atual"""
    novos_clientes: list
    trials_expirando: list
    cancelamentos: list
    dicas: list
    financeiro: dict
    ultima_atualizacao: str


class ObjetivosResponse(BaseModel):
    """Response dos objetivos"""
    meta_clientes_mes: int
    meta_receita_mes: float
    max_anuncios_percent: int
    max_openai_percent: int
    taxa_conversao_esperada: int


class UpdateObjetivosRequest(BaseModel):
    """Request para atualizar objetivos"""
    meta_clientes_mes: int | None = None
    meta_receita_mes: float | None = None
    max_anuncios_percent: int | None = None
    max_openai_percent: int | None = None
    taxa_conversao_esperada: int | None = None


@router.get("/resumo-atual", response_model=ResumoAtualResponse)
def get_resumo_atual(db: Session = Depends(get_db)):
    """
    Retorna resumo atual da IA
    """
    resumo = IAAssistenteService.get_resumo_atual(db)
    
    return {
        **resumo,
        'ultima_atualizacao': datetime.utcnow().isoformat()
    }


@router.post("/gerar-resumo")
def gerar_resumo(db: Session = Depends(get_db)):
    """
    Força geração de novo resumo
    """
    resumo = IAAssistenteService.gerar_resumo_diario(db)
    return {'message': 'Resumo gerado com sucesso', 'resumo': resumo}


@router.get("/historico")
def get_historico(
    tipo: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Retorna histórico de mensagens da IA
    """
    query = db.query(IAMensagem)
    
    if tipo:
        query = query.filter(IAMensagem.tipo == tipo)
    
    total = query.count()
    
    mensagens = query.order_by(IAMensagem.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return {
        'mensagens': [
            {
                'id': m.id,
                'tipo': m.tipo,
                'conteudo': m.conteudo,
                'dados': m.dados_json,
                'created_at': m.created_at.isoformat()
            }
            for m in mensagens
        ],
        'total': total,
        'page': page,
        'pages': (total + limit - 1) // limit
    }


@router.get("/objetivos", response_model=ObjetivosResponse)
def get_objetivos(db: Session = Depends(get_db)):
    """
    Retorna objetivos do admin
    """
    objetivos = db.query(AdminObjetivos).filter_by(id=1).first()
    
    if not objetivos:
        # Criar padrão
        objetivos = AdminObjetivos(id=1)
        db.add(objetivos)
        db.commit()
        db.refresh(objetivos)
    
    return {
        'meta_clientes_mes': objetivos.meta_clientes_mes,
        'meta_receita_mes': float(objetivos.meta_receita_mes),
        'max_anuncios_percent': objetivos.max_anuncios_percent,
        'max_openai_percent': objetivos.max_openai_percent,
        'taxa_conversao_esperada': objetivos.taxa_conversao_esperada
    }


@router.put("/objetivos")
def update_objetivos(
    request: UpdateObjetivosRequest,
    db: Session = Depends(get_db)
):
    """
    Atualiza objetivos do admin
    """
    from datetime import datetime
    
    objetivos = db.query(AdminObjetivos).filter_by(id=1).first()
    
    if not objetivos:
        objetivos = AdminObjetivos(id=1)
        db.add(objetivos)
    
    if request.meta_clientes_mes is not None:
        objetivos.meta_clientes_mes = request.meta_clientes_mes
    if request.meta_receita_mes is not None:
        objetivos.meta_receita_mes = request.meta_receita_mes
    if request.max_anuncios_percent is not None:
        objetivos.max_anuncios_percent = request.max_anuncios_percent
    if request.max_openai_percent is not None:
        objetivos.max_openai_percent = request.max_openai_percent
    if request.taxa_conversao_esperada is not None:
        objetivos.taxa_conversao_esperada = request.taxa_conversao_esperada
    
    objetivos.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {'message': 'Objetivos atualizados com sucesso'}


from datetime import datetime
