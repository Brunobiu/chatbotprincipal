"""
Serviço de Analytics
"""
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.db.models.cliente import Cliente
from app.db.models.metrica_diaria import MetricaDiaria


class AnalyticsService:
    
    @staticmethod
    def calcular_metricas_diarias(db: Session, data: date = None):
        """Calcula e salva métricas do dia"""
        if not data:
            data = date.today()
        
        # Verificar se já existe
        metrica_existente = db.query(MetricaDiaria).filter_by(data=data).first()
        if metrica_existente:
            db.delete(metrica_existente)
        
        # Calcular métricas
        total_clientes = db.query(Cliente).count()
        clientes_ativos = db.query(Cliente).filter_by(subscription_status='active').count()
        clientes_trial = db.query(Cliente).filter_by(subscription_status='trial').count()
        clientes_cancelados = db.query(Cliente).filter_by(subscription_status='canceled').count()
        
        # Novos clientes do dia
        inicio_dia = datetime.combine(data, datetime.min.time())
        fim_dia = datetime.combine(data, datetime.max.time())
        novos_clientes = db.query(Cliente).filter(
            Cliente.created_at >= inicio_dia,
            Cliente.created_at <= fim_dia
        ).count()
        
        # Receita (soma dos planos ativos)
        receita = db.query(func.sum(Cliente.plano_preco)).filter_by(subscription_status='active').scalar() or Decimal('0')
        
        # Criar métrica
        metrica = MetricaDiaria(
            data=data,
            total_clientes=total_clientes,
            clientes_ativos=clientes_ativos,
            clientes_trial=clientes_trial,
            clientes_cancelados=clientes_cancelados,
            novos_clientes=novos_clientes,
            conversoes=0,  # TODO: Implementar
            cancelamentos=0,  # TODO: Implementar
            total_conversas=0,  # TODO: Implementar
            total_mensagens=0,  # TODO: Implementar
            receita_dia=receita,
            custo_openai_dia=Decimal('0'),  # TODO: Implementar
            created_at=datetime.utcnow()
        )
        
        db.add(metrica)
        db.commit()
        
        return metrica
    
    @staticmethod
    def get_resumo_geral(db: Session, data_inicio: date, data_fim: date):
        """Retorna resumo geral do período"""
        metricas = db.query(MetricaDiaria).filter(
            MetricaDiaria.data >= data_inicio,
            MetricaDiaria.data <= data_fim
        ).all()
        
        if not metricas:
            return {
                'total_clientes': 0,
                'clientes_ativos': 0,
                'total_conversas': 0,
                'total_mensagens': 0,
                'receita_total': 0,
                'crescimento_clientes': 0
            }
        
        ultima = metricas[-1] if metricas else None
        
        return {
            'total_clientes': ultima.total_clientes if ultima else 0,
            'clientes_ativos': ultima.clientes_ativos if ultima else 0,
            'total_conversas': sum(m.total_conversas for m in metricas),
            'total_mensagens': sum(m.total_mensagens for m in metricas),
            'receita_total': float(sum(m.receita_dia for m in metricas)),
            'crescimento_clientes': sum(m.novos_clientes for m in metricas)
        }
    
    @staticmethod
    def get_crescimento_clientes(db: Session, meses: int = 6):
        """Retorna dados para gráfico de crescimento"""
        data_inicio = date.today() - timedelta(days=30 * meses)
        
        metricas = db.query(MetricaDiaria).filter(
            MetricaDiaria.data >= data_inicio
        ).order_by(MetricaDiaria.data).all()
        
        # Agrupar por mês
        meses_dict = {}
        for m in metricas:
            mes_key = m.data.strftime('%Y-%m')
            if mes_key not in meses_dict:
                meses_dict[mes_key] = []
            meses_dict[mes_key].append(m)
        
        # Pegar último valor de cada mês
        labels = []
        data = []
        for mes_key in sorted(meses_dict.keys()):
            labels.append(mes_key)
            data.append(meses_dict[mes_key][-1].total_clientes)
        
        return {'labels': labels, 'data': data}
    
    @staticmethod
    def get_receita_mensal(db: Session, meses: int = 6):
        """Retorna dados para gráfico de receita"""
        data_inicio = date.today() - timedelta(days=30 * meses)
        
        metricas = db.query(MetricaDiaria).filter(
            MetricaDiaria.data >= data_inicio
        ).order_by(MetricaDiaria.data).all()
        
        # Agrupar por mês e somar receita
        meses_dict = {}
        for m in metricas:
            mes_key = m.data.strftime('%Y-%m')
            if mes_key not in meses_dict:
                meses_dict[mes_key] = Decimal('0')
            meses_dict[mes_key] += m.receita_dia
        
        labels = []
        data = []
        for mes_key in sorted(meses_dict.keys()):
            labels.append(mes_key)
            data.append(float(meses_dict[mes_key]))
        
        return {'labels': labels, 'data': data}
    
    @staticmethod
    def get_distribuicao_planos(db: Session):
        """Retorna distribuição de clientes por plano"""
        mensal = db.query(Cliente).filter_by(plano='mensal', subscription_status='active').count()
        trimestral = db.query(Cliente).filter_by(plano='trimestral', subscription_status='active').count()
        semestral = db.query(Cliente).filter_by(plano='semestral', subscription_status='active').count()
        
        total = mensal + trimestral + semestral
        
        return {
            'labels': ['Mensal', 'Trimestral', 'Semestral'],
            'data': [mensal, trimestral, semestral],
            'percentuais': [
                round(mensal / total * 100) if total > 0 else 0,
                round(trimestral / total * 100) if total > 0 else 0,
                round(semestral / total * 100) if total > 0 else 0
            ]
        }
