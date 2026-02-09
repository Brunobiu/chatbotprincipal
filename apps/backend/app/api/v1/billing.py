"""
Rotas de billing (planos e pagamentos)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal

from app.db.session import get_db
from app.api.v1.auth import get_current_cliente

router = APIRouter()


# Schemas
class PlanoInfo(BaseModel):
    """Informações de um plano"""
    id: str
    nome: str
    preco_mensal: float
    valor_total: float
    periodo_meses: int
    desconto_percent: int
    economia: float


class CreateCheckoutRequest(BaseModel):
    """Request para criar checkout"""
    plano: str  # 'mensal', 'trimestral', 'semestral'


class CreateCheckoutResponse(BaseModel):
    """Response com URL do checkout"""
    checkout_url: str


class MeuPlanoResponse(BaseModel):
    """Response com informações do plano atual"""
    subscription_status: str
    plano: str | None
    plano_preco: float | None
    plano_valor_total: float | None
    proxima_cobranca: str | None
    cartao_ultimos_digitos: str | None
    trial_days_remaining: int | None


class PagamentoHistorico(BaseModel):
    """Histórico de pagamento"""
    id: int
    data: str
    plano: str
    valor: float
    status: str


# Configuração dos planos
PLANOS = {
    'mensal': {
        'nome': 'Mensal',
        'preco_mensal': 147.00,
        'valor_total': 147.00,
        'periodo_meses': 1,
        'desconto_percent': 0,
        'stripe_price_id': 'price_mensal_xxx'  # Substituir pelo ID real do Stripe
    },
    'trimestral': {
        'nome': 'Trimestral',
        'preco_mensal': 127.00,
        'valor_total': 381.00,
        'periodo_meses': 3,
        'desconto_percent': 14,
        'stripe_price_id': 'price_trimestral_xxx'
    },
    'semestral': {
        'nome': 'Semestral',
        'preco_mensal': 97.00,
        'valor_total': 582.00,
        'periodo_meses': 6,
        'desconto_percent': 34,
        'stripe_price_id': 'price_semestral_xxx'
    }
}


@router.get("/planos", response_model=list[PlanoInfo])
def listar_planos():
    """
    Lista todos os planos disponíveis
    """
    planos_list = []
    
    for plano_id, info in PLANOS.items():
        economia = (147.00 * info['periodo_meses']) - info['valor_total']
        
        planos_list.append({
            'id': plano_id,
            'nome': info['nome'],
            'preco_mensal': info['preco_mensal'],
            'valor_total': info['valor_total'],
            'periodo_meses': info['periodo_meses'],
            'desconto_percent': info['desconto_percent'],
            'economia': economia
        })
    
    return planos_list


@router.post("/create-checkout", response_model=CreateCheckoutResponse)
def create_checkout(
    request: CreateCheckoutRequest,
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Cria sessão de checkout do Stripe
    """
    if request.plano not in PLANOS:
        raise HTTPException(400, "Plano inválido")
    
    plano_info = PLANOS[request.plano]
    
    # TODO: Integrar com Stripe real
    # Por enquanto, simular ativação direta
    
    # Ativar assinatura
    now = datetime.utcnow()
    proxima_cobranca = now + timedelta(days=30 * plano_info['periodo_meses'])
    
    cliente.subscription_status = 'active'
    cliente.plano = request.plano
    cliente.plano_preco = Decimal(str(plano_info['preco_mensal']))
    cliente.plano_valor_total = Decimal(str(plano_info['valor_total']))
    cliente.proxima_cobranca = proxima_cobranca
    cliente.updated_at = now
    
    # Registrar pagamento
    from app.db.models.pagamento import Pagamento
    pagamento = Pagamento(
        cliente_id=cliente.id,
        plano=request.plano,
        valor=Decimal(str(plano_info['valor_total'])),
        status='succeeded',
        data_pagamento=now,
        created_at=now
    )
    db.add(pagamento)
    
    db.commit()
    
    # Retornar URL fake (em produção seria URL do Stripe)
    return {
        'checkout_url': f'/dashboard?plano_ativado={request.plano}'
    }


@router.get("/meu-plano", response_model=MeuPlanoResponse)
def get_meu_plano(
    cliente = Depends(get_current_cliente)
):
    """
    Retorna informações do plano atual do cliente
    """
    trial_days = None
    if cliente.subscription_status == 'trial' and cliente.trial_ends_at:
        delta = cliente.trial_ends_at - datetime.utcnow()
        trial_days = max(0, delta.days)
    
    return {
        'subscription_status': cliente.subscription_status,
        'plano': cliente.plano,
        'plano_preco': float(cliente.plano_preco) if cliente.plano_preco else None,
        'plano_valor_total': float(cliente.plano_valor_total) if cliente.plano_valor_total else None,
        'proxima_cobranca': cliente.proxima_cobranca.isoformat() if cliente.proxima_cobranca else None,
        'cartao_ultimos_digitos': None,  # TODO: Buscar do Stripe
        'trial_days_remaining': trial_days
    }


@router.get("/historico-pagamentos", response_model=list[PagamentoHistorico])
def get_historico_pagamentos(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Retorna histórico de pagamentos do cliente
    """
    from app.db.models.pagamento import Pagamento
    
    pagamentos = db.query(Pagamento).filter_by(cliente_id=cliente.id).order_by(Pagamento.created_at.desc()).all()
    
    return [
        {
            'id': p.id,
            'data': p.data_pagamento.isoformat() if p.data_pagamento else p.created_at.isoformat(),
            'plano': p.plano,
            'valor': float(p.valor),
            'status': p.status
        }
        for p in pagamentos
    ]


@router.post("/cancelar-assinatura")
def cancelar_assinatura(
    cliente = Depends(get_current_cliente),
    db: Session = Depends(get_db)
):
    """
    Cancela assinatura (mantém acesso até fim do período pago)
    """
    if cliente.subscription_status != 'active':
        raise HTTPException(400, "Você não tem uma assinatura ativa")
    
    # Marcar como cancelado mas manter acesso até proxima_cobranca
    cliente.subscription_status = 'canceled'
    cliente.updated_at = datetime.utcnow()
    
    # TODO: Cancelar no Stripe
    
    db.commit()
    
    return {
        'message': 'Assinatura cancelada. Você manterá acesso até ' + 
                   (cliente.proxima_cobranca.strftime('%d/%m/%Y') if cliente.proxima_cobranca else 'o fim do período')
    }
