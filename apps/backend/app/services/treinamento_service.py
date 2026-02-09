"""
Serviço de Treinamento de IA
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models.conversa import Conversa
from app.db.models.cliente import Cliente


class TreinamentoService:
    
    @staticmethod
    def get_todas_conversas(
        db: Session,
        cliente_id: int = None,
        avaliacao: str = None,
        busca: str = None,
        page: int = 1,
        limit: int = 20
    ):
        """Lista todas as conversas com filtros"""
        query = db.query(Conversa).join(Cliente)
        
        if cliente_id:
            query = query.filter(Conversa.cliente_id == cliente_id)
        
        if avaliacao:
            query = query.filter(Conversa.avaliacao == avaliacao)
        
        if busca:
            # Buscar em mensagens (simplificado)
            query = query.filter(Conversa.id.isnot(None))  # TODO: Implementar busca em mensagens
        
        total = query.count()
        
        conversas = query.order_by(Conversa.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        
        return {
            'conversas': conversas,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }
    
    @staticmethod
    def marcar_conversa(db: Session, conversa_id: int, avaliacao: str):
        """Marca conversa como boa ou ruim"""
        if avaliacao not in ['boa', 'ruim']:
            raise ValueError("Avaliação deve ser 'boa' ou 'ruim'")
        
        conversa = db.query(Conversa).filter_by(id=conversa_id).first()
        if not conversa:
            raise ValueError("Conversa não encontrada")
        
        conversa.avaliacao = avaliacao
        conversa.avaliado_em = datetime.utcnow()
        conversa.avaliado_por = 'admin'
        
        db.commit()
        
        return conversa
    
    @staticmethod
    def get_analise_treinamento(db: Session):
        """Retorna análise das conversas marcadas"""
        total = db.query(Conversa).count()
        boas = db.query(Conversa).filter_by(avaliacao='boa').count()
        ruins = db.query(Conversa).filter_by(avaliacao='ruim').count()
        sem_avaliacao = total - boas - ruins
        
        # Verificar se pode fazer fine-tuning
        pode_fine_tuning = (boas + ruins) >= 50 and boas >= 30 and ruins >= 10
        
        return {
            'total': total,
            'boas': boas,
            'ruins': ruins,
            'sem_avaliacao': sem_avaliacao,
            'pode_fine_tuning': pode_fine_tuning,
            'minimo_necessario': 50,
            'progresso': round((boas + ruins) / 50 * 100) if (boas + ruins) < 50 else 100
        }
