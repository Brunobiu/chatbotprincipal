"""
Endpoints de Agendamentos
Task 10.4
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.cliente import Cliente
from app.services.auth.auth_service import AuthService
from app.services.agendamentos.agendamento_service import AgendamentoService


router = APIRouter()


# Schemas
class ConfigurarHorariosRequest(BaseModel):
    horarios_disponiveis: dict  # {"segunda": [{"inicio": "09:00", "fim": "18:00"}], ...}
    duracao_slot_minutos: int = 30
    tipos_servico: Optional[List[str]] = None


class AgendamentoResponse(BaseModel):
    id: int
    numero_usuario: str
    nome_usuario: Optional[str]
    data_hora: datetime
    tipo_servico: Optional[str]
    observacoes: Optional[str]
    status: str
    mensagem_original: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConfiguracaoHorariosResponse(BaseModel):
    id: int
    horarios_disponiveis: dict
    duracao_slot_minutos: int
    tipos_servico: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/configurar-horarios", response_model=ConfiguracaoHorariosResponse)
def configurar_horarios(
    request: ConfigurarHorariosRequest,
    db: Session = Depends(get_db),
    current_cliente: Cliente = Depends(AuthService.get_current_cliente)
):
    """
    Configura horários disponíveis para agendamentos
    """
    try:
        config = AgendamentoService.configurar_horarios(
            db=db,
            cliente_id=current_cliente.id,
            horarios_disponiveis=request.horarios_disponiveis,
            duracao_slot_minutos=request.duracao_slot_minutos,
            tipos_servico=request.tipos_servico
        )
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao configurar horários: {str(e)}")


@router.get("/configuracao", response_model=Optional[ConfiguracaoHorariosResponse])
def obter_configuracao(
    db: Session = Depends(get_db),
    current_cliente: Cliente = Depends(AuthService.get_current_cliente)
):
    """
    Retorna configuração de horários do cliente
    """
    config = AgendamentoService.obter_configuracao(db, current_cliente.id)
    return config


@router.get("/pendentes", response_model=List[AgendamentoResponse])
def listar_pendentes(
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_cliente: Cliente = Depends(AuthService.get_current_cliente)
):
    """
    Lista agendamentos pendentes
    """
    agendamentos = AgendamentoService.listar_agendamentos_pendentes(
        db=db,
        cliente_id=current_cliente.id,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    return agendamentos


@router.get("/", response_model=List[AgendamentoResponse])
def listar_agendamentos(
    status: Optional[str] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_cliente: Cliente = Depends(AuthService.get_current_cliente)
):
    """
    Lista agendamentos com filtros
    """
    from app.db.models.agendamento import AgendamentoStatus
    
    status_enum = None
    if status:
        try:
            status_enum = AgendamentoStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Status inválido")
    
    agendamentos = AgendamentoService.listar_agendamentos(
        db=db,
        cliente_id=current_cliente.id,
        status=status_enum,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limit=limit,
        offset=offset
    )
    return agendamentos


@router.post("/{agendamento_id}/aprovar", response_model=AgendamentoResponse)
def aprovar_agendamento(
    agendamento_id: int,
    db: Session = Depends(get_db),
    current_cliente: Cliente = Depends(AuthService.get_current_cliente)
):
    """
    Aprova agendamento
    """
    try:
        agendamento = AgendamentoService.aprovar_agendamento(
            db=db,
            agendamento_id=agendamento_id,
            cliente_id=current_cliente.id
        )
        return agendamento
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao aprovar agendamento: {str(e)}")


@router.post("/{agendamento_id}/recusar", response_model=AgendamentoResponse)
def recusar_agendamento(
    agendamento_id: int,
    db: Session = Depends(get_db),
    current_cliente: Cliente = Depends(AuthService.get_current_cliente)
):
    """
    Recusa agendamento
    """
    try:
        agendamento = AgendamentoService.recusar_agendamento(
            db=db,
            agendamento_id=agendamento_id,
            cliente_id=current_cliente.id
        )
        return agendamento
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recusar agendamento: {str(e)}")


@router.post("/{agendamento_id}/cancelar", response_model=AgendamentoResponse)
def cancelar_agendamento(
    agendamento_id: int,
    db: Session = Depends(get_db),
    current_cliente: Cliente = Depends(AuthService.get_current_cliente)
):
    """
    Cancela agendamento
    """
    try:
        agendamento = AgendamentoService.cancelar_agendamento(
            db=db,
            agendamento_id=agendamento_id,
            cliente_id=current_cliente.id
        )
        return agendamento
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cancelar agendamento: {str(e)}")


@router.get("/dia/{data}", response_model=List[AgendamentoResponse])
def agendamentos_do_dia(
    data: datetime,
    db: Session = Depends(get_db),
    current_cliente: Cliente = Depends(AuthService.get_current_cliente)
):
    """
    Retorna agendamentos de um dia específico
    """
    agendamentos = AgendamentoService.agendamentos_do_dia(
        db=db,
        cliente_id=current_cliente.id,
        data=data
    )
    return agendamentos
