"""
Service para rastrear uso da OpenAI
FASE 16.4 - Monitoramento de Uso (Créditos OpenAI)
"""
import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.db.models.uso_openai import UsoOpenAI
from app.db.models.cliente import Cliente

logger = logging.getLogger(__name__)


class UsoOpenAIService:
    """Service para rastrear e analisar uso da OpenAI"""
    
    # Custos por 1K tokens (valores aproximados - ajustar conforme modelo)
    CUSTOS_POR_MODELO = {
        "gpt-4": {
            "prompt": 0.03,      # $0.03 por 1K tokens
            "completion": 0.06   # $0.06 por 1K tokens
        },
        "gpt-4-turbo": {
            "prompt": 0.01,
            "completion": 0.03
        },
        "gpt-3.5-turbo": {
            "prompt": 0.0015,
            "completion": 0.002
        },
        "gpt-3.5-turbo-16k": {
            "prompt": 0.003,
            "completion": 0.004
        }
    }
    
    # Threshold padrão de alerta (em dólares por dia)
    THRESHOLD_ALERTA_DIARIO = 10.0  # $10/dia
    
    @staticmethod
    def calcular_custo(modelo: str, tokens_prompt: int, tokens_completion: int) -> float:
        """
        Calcula custo estimado baseado no modelo e tokens usados
        
        Args:
            modelo: Nome do modelo OpenAI
            tokens_prompt: Tokens do prompt
            tokens_completion: Tokens da resposta
            
        Returns:
            Custo em dólares
        """
        custos = UsoOpenAIService.CUSTOS_POR_MODELO.get(modelo, {
            "prompt": 0.002,
            "completion": 0.002
        })
        
        custo_prompt = (tokens_prompt / 1000) * custos["prompt"]
        custo_completion = (tokens_completion / 1000) * custos["completion"]
        
        return custo_prompt + custo_completion
    
    @staticmethod
    def registrar_uso(
        db: Session,
        cliente_id: int,
        modelo: str,
        tokens_prompt: int,
        tokens_completion: int
    ) -> UsoOpenAI:
        """
        Registra uso da OpenAI para um cliente
        Atualiza registro existente do dia ou cria novo
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            modelo: Modelo usado
            tokens_prompt: Tokens do prompt
            tokens_completion: Tokens da resposta
            
        Returns:
            Registro de uso atualizado
        """
        hoje = date.today()
        tokens_total = tokens_prompt + tokens_completion
        custo = UsoOpenAIService.calcular_custo(modelo, tokens_prompt, tokens_completion)
        
        # Buscar registro existente do dia
        uso = db.query(UsoOpenAI).filter(
            UsoOpenAI.cliente_id == cliente_id,
            UsoOpenAI.data == hoje
        ).first()
        
        if uso:
            # Atualizar registro existente
            uso.tokens_prompt += tokens_prompt
            uso.tokens_completion += tokens_completion
            uso.tokens_total += tokens_total
            uso.custo_estimado += custo
            uso.mensagens_processadas += 1
            uso.updated_at = datetime.utcnow()
        else:
            # Criar novo registro
            uso = UsoOpenAI(
                cliente_id=cliente_id,
                data=hoje,
                tokens_prompt=tokens_prompt,
                tokens_completion=tokens_completion,
                tokens_total=tokens_total,
                custo_estimado=custo,
                mensagens_processadas=1,
                modelo=modelo
            )
            db.add(uso)
        
        db.commit()
        db.refresh(uso)
        
        logger.info(f"📊 Uso registrado: Cliente {cliente_id} | {tokens_total} tokens | R$ {custo:.4f}")
        
        return uso
    
    @staticmethod
    def obter_top_gastadores(
        db: Session,
        limite: int = 10,
        dias: int = 30
    ) -> List[Dict]:
        """
        Retorna top clientes que mais gastam
        
        Args:
            db: Sessão do banco
            limite: Número de clientes a retornar
            dias: Período em dias
            
        Returns:
            Lista de dicts com cliente e estatísticas
        """
        data_inicio = date.today() - timedelta(days=dias)
        
        # Query agregada
        resultados = db.query(
            Cliente.id,
            Cliente.nome,
            Cliente.email,
            func.sum(UsoOpenAI.tokens_total).label('tokens_total'),
            func.sum(UsoOpenAI.custo_estimado).label('custo_total'),
            func.sum(UsoOpenAI.mensagens_processadas).label('mensagens_total')
        ).join(
            UsoOpenAI, Cliente.id == UsoOpenAI.cliente_id
        ).filter(
            UsoOpenAI.data >= data_inicio
        ).group_by(
            Cliente.id, Cliente.nome, Cliente.email
        ).order_by(
            desc('custo_total')
        ).limit(limite).all()
        
        return [
            {
                "cliente_id": r.id,
                "nome": r.nome,
                "email": r.email,
                "tokens_total": r.tokens_total or 0,
                "custo_total": r.custo_total or 0.0,
                "mensagens_total": r.mensagens_total or 0,
                "custo_medio_por_mensagem": (r.custo_total / r.mensagens_total) if r.mensagens_total > 0 else 0.0
            }
            for r in resultados
        ]
    
    @staticmethod
    def obter_historico_cliente(
        db: Session,
        cliente_id: int,
        dias: int = 30
    ) -> List[Dict]:
        """
        Retorna histórico de uso de um cliente
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            dias: Período em dias
            
        Returns:
            Lista de dicts com uso diário
        """
        data_inicio = date.today() - timedelta(days=dias)
        
        registros = db.query(UsoOpenAI).filter(
            UsoOpenAI.cliente_id == cliente_id,
            UsoOpenAI.data >= data_inicio
        ).order_by(UsoOpenAI.data.desc()).all()
        
        return [
            {
                "data": r.data.isoformat(),
                "tokens_prompt": r.tokens_prompt,
                "tokens_completion": r.tokens_completion,
                "tokens_total": r.tokens_total,
                "custo_estimado": r.custo_estimado,
                "mensagens_processadas": r.mensagens_processadas,
                "modelo": r.modelo
            }
            for r in registros
        ]
    
    @staticmethod
    def obter_alertas(
        db: Session,
        threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Retorna clientes que ultrapassaram o threshold de custo hoje
        
        Args:
            db: Sessão do banco
            threshold: Limite de custo diário (usa padrão se None)
            
        Returns:
            Lista de dicts com clientes em alerta
        """
        if threshold is None:
            threshold = UsoOpenAIService.THRESHOLD_ALERTA_DIARIO
        
        hoje = date.today()
        
        # Buscar uso de hoje acima do threshold
        registros = db.query(
            UsoOpenAI, Cliente
        ).join(
            Cliente, UsoOpenAI.cliente_id == Cliente.id
        ).filter(
            UsoOpenAI.data == hoje,
            UsoOpenAI.custo_estimado >= threshold
        ).order_by(
            desc(UsoOpenAI.custo_estimado)
        ).all()
        
        return [
            {
                "cliente_id": cliente.id,
                "nome": cliente.nome,
                "email": cliente.email,
                "custo_hoje": uso.custo_estimado,
                "tokens_hoje": uso.tokens_total,
                "mensagens_hoje": uso.mensagens_processadas,
                "threshold": threshold,
                "percentual_acima": ((uso.custo_estimado - threshold) / threshold) * 100
            }
            for uso, cliente in registros
        ]
    
    @staticmethod
    def obter_resumo_geral(db: Session, dias: int = 30) -> Dict:
        """
        Retorna resumo geral de uso de todos os clientes
        
        Args:
            db: Sessão do banco
            dias: Período em dias
            
        Returns:
            Dict com estatísticas gerais
        """
        data_inicio = date.today() - timedelta(days=dias)
        
        # Agregações
        resultado = db.query(
            func.sum(UsoOpenAI.tokens_total).label('tokens_total'),
            func.sum(UsoOpenAI.custo_estimado).label('custo_total'),
            func.sum(UsoOpenAI.mensagens_processadas).label('mensagens_total'),
            func.count(func.distinct(UsoOpenAI.cliente_id)).label('clientes_ativos')
        ).filter(
            UsoOpenAI.data >= data_inicio
        ).first()
        
        # Custo hoje
        hoje = date.today()
        custo_hoje = db.query(
            func.sum(UsoOpenAI.custo_estimado)
        ).filter(
            UsoOpenAI.data == hoje
        ).scalar() or 0.0
        
        return {
            "periodo_dias": dias,
            "tokens_total": resultado.tokens_total or 0,
            "custo_total": resultado.custo_total or 0.0,
            "mensagens_total": resultado.mensagens_total or 0,
            "clientes_ativos": resultado.clientes_ativos or 0,
            "custo_hoje": custo_hoje,
            "custo_medio_por_mensagem": (resultado.custo_total / resultado.mensagens_total) if resultado.mensagens_total > 0 else 0.0
        }
