"""
Serviço de IA Assistente para o Admin
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.db.models.cliente import Cliente
from app.db.models.pagamento import Pagamento
from app.db.models.ia_mensagem import IAMensagem


class IAAssistenteService:
    
    @staticmethod
    def gerar_resumo_diario(db: Session) -> dict:
        """Gera resumo diário para o admin"""
        hoje = datetime.utcnow().date()
        inicio_dia = datetime.combine(hoje, datetime.min.time())
        fim_dia = datetime.combine(hoje, datetime.max.time())
        
        # Novos clientes hoje
        novos_clientes = db.query(Cliente).filter(
            Cliente.created_at >= inicio_dia,
            Cliente.created_at <= fim_dia
        ).all()
        
        # Trials expirando nos próximos 3 dias
        daqui_3_dias = datetime.utcnow() + timedelta(days=3)
        trials_expirando = db.query(Cliente).filter(
            Cliente.subscription_status == 'trial',
            Cliente.trial_ends_at <= daqui_3_dias,
            Cliente.trial_ends_at >= datetime.utcnow()
        ).all()
        
        # Cancelamentos hoje
        cancelamentos = db.query(Cliente).filter(
            Cliente.subscription_status == 'canceled',
            Cliente.updated_at >= inicio_dia,
            Cliente.updated_at <= fim_dia
        ).all()
        
        # Métricas financeiras
        clientes_ativos = db.query(Cliente).filter(
            Cliente.subscription_status == 'active'
        ).count()
        
        receita_total = db.query(func.sum(Cliente.plano_preco)).filter(
            Cliente.subscription_status == 'active'
        ).scalar() or Decimal('0')
        
        # Gerar dicas
        dicas = []
        
        # Taxa de conversão
        total_trials = db.query(Cliente).filter(Cliente.subscription_status == 'trial').count()
        if total_trials > 0:
            taxa_conversao = (clientes_ativos / (clientes_ativos + total_trials)) * 100
            if taxa_conversao < 20:
                dicas.append(f"Sua taxa de conversão está em {taxa_conversao:.0f}% (média: 20%). Recomendação: Envie email para trials expirando")
        
        # Clientes sem configurar bot
        # TODO: Implementar quando tiver essa métrica
        
        # Trials expirando sem contato
        if len(trials_expirando) > 0:
            dicas.append(f"{len(trials_expirando)} trials expirando em breve. Entre em contato!")
        
        resumo = {
            'novos_clientes': [{'nome': c.nome, 'email': c.email, 'hora': c.created_at.strftime('%H:%M')} for c in novos_clientes],
            'trials_expirando': [{'nome': c.nome, 'dias': (c.trial_ends_at - datetime.utcnow()).days} for c in trials_expirando],
            'cancelamentos': [{'nome': c.nome, 'hora': c.updated_at.strftime('%H:%M')} for c in cancelamentos],
            'dicas': dicas,
            'financeiro': {
                'receita_mensal': float(receita_total),
                'clientes_pagos': clientes_ativos,
                'custo_openai': 0,  # TODO: Implementar rastreamento
                'lucro': float(receita_total),
                'margem': 100 if receita_total > 0 else 0
            }
        }
        
        # Salvar mensagem
        mensagem = IAMensagem(
            tipo='resumo_diario',
            conteudo=f"Resumo do dia {hoje.strftime('%d/%m/%Y')}",
            dados_json=resumo,
            created_at=datetime.utcnow()
        )
        db.add(mensagem)
        db.commit()
        
        return resumo
    
    @staticmethod
    def get_resumo_atual(db: Session) -> dict:
        """Retorna resumo mais recente ou gera novo"""
        # Buscar resumo de hoje
        hoje = datetime.utcnow().date()
        inicio_dia = datetime.combine(hoje, datetime.min.time())
        
        mensagem = db.query(IAMensagem).filter(
            IAMensagem.tipo == 'resumo_diario',
            IAMensagem.created_at >= inicio_dia
        ).order_by(IAMensagem.created_at.desc()).first()
        
        if mensagem:
            return mensagem.dados_json
        
        # Gerar novo
        return IAAssistenteService.gerar_resumo_diario(db)
