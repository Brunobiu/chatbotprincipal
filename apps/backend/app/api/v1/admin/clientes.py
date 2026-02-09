"""
Rotas de gestão de clientes para admin
FASE 16.3 - Gestão de Clientes (CRUD Completo)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime
import secrets
import string

from app.db.session import get_db
from app.db.models.cliente import Cliente, ClienteStatus
from app.api.v1.admin.auth import get_current_admin
from app.core.security import get_password_hash
from app.services.email import EmailService


router = APIRouter()


# Schemas
class ClienteListItem(BaseModel):
    """Schema para item da lista de clientes"""
    id: int
    nome: str
    nome_empresa: Optional[str]
    email: str
    telefone: Optional[str]
    status: str
    stripe_status: Optional[str]
    ultimo_login: Optional[datetime]
    total_mensagens_enviadas: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClienteListResponse(BaseModel):
    """Schema para resposta paginada"""
    total: int
    page: int
    per_page: int
    total_pages: int
    clientes: List[ClienteListItem]


class ClienteDetalhes(BaseModel):
    """Schema para detalhes completos do cliente"""
    id: int
    nome: str
    nome_empresa: Optional[str]
    email: str
    telefone: Optional[str]
    status: str
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    stripe_status: Optional[str]
    ultimo_login: Optional[datetime]
    ip_ultimo_login: Optional[str]
    total_mensagens_enviadas: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClienteUpdate(BaseModel):
    """Schema para atualização de cliente"""
    nome: Optional[str] = None
    nome_empresa: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None


class ResetarSenhaResponse(BaseModel):
    """Schema para resposta de reset de senha"""
    success: bool
    nova_senha: str
    message: str


@router.get("/clientes", response_model=ClienteListResponse)
def listar_clientes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Lista todos os clientes com filtros e paginação
    
    Filtros:
    - status: ativo, inativo, pendente, suspenso
    - search: busca por nome, email ou empresa
    """
    query = db.query(Cliente)
    
    # Filtro por status
    if status:
        try:
            status_enum = ClienteStatus(status.lower())
            query = query.filter(Cliente.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status inválido. Use: {', '.join([s.value for s in ClienteStatus])}"
            )
    
    # Filtro de busca
    if search:
        search_filter = or_(
            Cliente.nome.ilike(f"%{search}%"),
            Cliente.email.ilike(f"%{search}%"),
            Cliente.nome_empresa.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Total de registros
    total = query.count()
    
    # Paginação
    offset = (page - 1) * per_page
    clientes = query.order_by(Cliente.created_at.desc()).offset(offset).limit(per_page).all()
    
    # Calcular total de páginas
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "clientes": clientes
    }


@router.get("/clientes/{cliente_id}", response_model=ClienteDetalhes)
def obter_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Obtém detalhes completos de um cliente
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return cliente


@router.put("/clientes/{cliente_id}", response_model=ClienteDetalhes)
def atualizar_cliente(
    cliente_id: int,
    dados: ClienteUpdate,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Atualiza dados de um cliente
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Verificar se email já existe (se estiver mudando)
    if dados.email and dados.email != cliente.email:
        email_existe = db.query(Cliente).filter(
            Cliente.email == dados.email,
            Cliente.id != cliente_id
        ).first()
        
        if email_existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado para outro cliente"
            )
    
    # Atualizar campos
    if dados.nome is not None:
        cliente.nome = dados.nome
    if dados.nome_empresa is not None:
        cliente.nome_empresa = dados.nome_empresa
    if dados.email is not None:
        cliente.email = dados.email
    if dados.telefone is not None:
        cliente.telefone = dados.telefone
    
    cliente.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(cliente)
    
    return cliente


@router.post("/clientes/{cliente_id}/suspender")
def suspender_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Suspende um cliente (bloqueia acesso)
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    if cliente.status == ClienteStatus.SUSPENSO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente já está suspenso"
        )
    
    cliente.status = ClienteStatus.SUSPENSO
    cliente.updated_at = datetime.utcnow()
    
    db.commit()
    
    # TODO: Enviar email notificando suspensão
    
    return {
        "success": True,
        "message": f"Cliente {cliente.nome} suspenso com sucesso"
    }


@router.post("/clientes/{cliente_id}/ativar")
def ativar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Ativa um cliente suspenso
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    if cliente.status == ClienteStatus.ATIVO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente já está ativo"
        )
    
    cliente.status = ClienteStatus.ATIVO
    cliente.updated_at = datetime.utcnow()
    
    db.commit()
    
    # TODO: Enviar email notificando reativação
    
    return {
        "success": True,
        "message": f"Cliente {cliente.nome} ativado com sucesso"
    }


@router.post("/clientes/{cliente_id}/resetar-senha", response_model=ResetarSenhaResponse)
def resetar_senha(
    cliente_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Reseta a senha do cliente e envia por email
    Gera senha aleatória segura
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Gerar senha aleatória segura (12 caracteres)
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    nova_senha = ''.join(secrets.choice(caracteres) for _ in range(12))
    
    # Atualizar senha
    cliente.senha_hash = get_password_hash(nova_senha)
    cliente.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Enviar email com nova senha
    try:
        EmailService.enviar_reset_senha_admin(
            email=cliente.email,
            nome=cliente.nome,
            nova_senha=nova_senha
        )
        email_enviado = True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        email_enviado = False
    
    return {
        "success": True,
        "nova_senha": nova_senha,
        "message": f"Senha resetada com sucesso. {'Email enviado para o cliente.' if email_enviado else 'ATENÇÃO: Falha ao enviar email. Informe a senha manualmente.'}"
    }


@router.get("/clientes/{cliente_id}/historico-completo")
def obter_historico_completo(
    cliente_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Obtém histórico completo do cliente incluindo:
    - Dados cadastrais
    - Histórico de pagamentos (Stripe)
    - Conversas WhatsApp (últimas 100)
    - Tickets abertos/resolvidos
    - Uso OpenAI (últimos 30 dias)
    - Logins (últimos 30 dias)
    - Timeline de eventos
    """
    from app.services.historico import HistoricoService
    
    historico = HistoricoService.obter_historico_completo(db, cliente_id)
    
    if "erro" in historico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=historico["erro"]
        )
    
    return historico
