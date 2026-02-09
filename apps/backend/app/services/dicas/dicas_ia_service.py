"""
Service para gerar dicas da IA para o admin
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Optional

from app.db.models.dica_ia import DicaIA
from app.db.models.cliente import Cliente, ClienteStatus
from app.services.ai import AIService

logger = logging.getLogger(__name__)


class DicasIAService:
    """Service para gerar dicas da IA"""
    
    @staticmethod
    def deve_atualizar_dicas(db: Session, admin_id: int) -> bool:
        """
        Verifica se deve atualizar dicas (última atualização > 24h)
        
        Args:
            db: Sessão do banco
            admin_id: ID do admin
            
        Returns:
            bool: True se deve atualizar
        """
        ultima_dica = db.query(DicaIA).filter(
            DicaIA.admin_id == admin_id
        ).order_by(DicaIA.created_at.desc()).first()
        
        if not ultima_dica:
            return True
        
        # Verificar se passou 24h
        agora = datetime.utcnow()
        diff = agora - ultima_dica.created_at
        
        return diff.total_seconds() > 86400  # 24 horas
    
    @staticmethod
    def gerar_dicas_diarias(db: Session, admin_id: int) -> Dict:
        """
        Gera dicas diárias com análise de métricas
        
        Args:
            db: Sessão do banco
            admin_id: ID do admin
            
        Returns:
            Dict com dicas geradas
        """
        logger.info(f"🤖 Gerando dicas da IA para admin {admin_id}")
        
        try:
            # Coletar métricas
            metricas = DicasIAService._coletar_metricas(db)
            
            # Buscar objetivo mensal
            ultima_dica = db.query(DicaIA).filter(
                DicaIA.admin_id == admin_id
            ).order_by(DicaIA.created_at.desc()).first()
            
            objetivo_mensal = ultima_dica.objetivo_mensal if ultima_dica else None
            
            # Gerar dicas com IA
            dicas_conteudo = DicasIAService._gerar_dicas_com_ia(metricas, objetivo_mensal)
            
            # Salvar no banco
            dica = DicaIA(
                admin_id=admin_id,
                conteudo=dicas_conteudo,
                objetivo_mensal=objetivo_mensal
            )
            db.add(dica)
            db.commit()
            db.refresh(dica)
            
            logger.info(f"✅ Dicas geradas para admin {admin_id}")
            
            return dicas_conteudo
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar dicas: {str(e)}", exc_info=True)
            db.rollback()
            raise
    
    @staticmethod
    def _coletar_metricas(db: Session) -> Dict:
        """
        Coleta métricas do sistema
        
        Returns:
            Dict com métricas
        """
        # Total de clientes
        total_clientes = db.query(Cliente).count()
        
        # Clientes ativos
        clientes_ativos = db.query(Cliente).filter(
            Cliente.status == ClienteStatus.ATIVO
        ).count()
        
        # Novos clientes (últimos 7 dias)
        sete_dias_atras = datetime.utcnow() - timedelta(days=7)
        novos_clientes = db.query(Cliente).filter(
            Cliente.created_at >= sete_dias_atras
        ).all()
        
        # Clientes que cancelaram (últimos 30 dias)
        trinta_dias_atras = datetime.utcnow() - timedelta(days=30)
        cancelados = db.query(Cliente).filter(
            and_(
                Cliente.status.in_([ClienteStatus.INATIVO, ClienteStatus.SUSPENSO]),
                Cliente.updated_at >= trinta_dias_atras
            )
        ).all()
        
        # Clientes prestes a vencer (próximos 7 dias)
        # TODO: Implementar quando tiver campo de data de vencimento
        prestes_vencer = []
        
        return {
            "total_clientes": total_clientes,
            "clientes_ativos": clientes_ativos,
            "novos_clientes": [
                {
                    "nome": c.nome,
                    "email": c.email,
                    "data": c.created_at.strftime("%d/%m/%Y")
                } for c in novos_clientes
            ],
            "cancelados": [
                {
                    "nome": c.nome,
                    "email": c.email,
                    "data": c.updated_at.strftime("%d/%m/%Y")
                } for c in cancelados
            ],
            "prestes_vencer": prestes_vencer
        }
    
    @staticmethod
    def _gerar_dicas_com_ia(metricas: Dict, objetivo_mensal: Optional[float]) -> Dict:
        """
        Usa IA para gerar insights e dicas
        
        Args:
            metricas: Métricas coletadas
            objetivo_mensal: Objetivo de faturamento mensal
            
        Returns:
            Dict com dicas geradas
        """
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage
        from app.core.config import settings
        import json
        
        logger.info("🤖 Gerando dicas com OpenAI")
        
        try:
            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0.7,
                api_key=settings.OPENAI_API_KEY
            )
            
            system_prompt = """Você é um consultor de negócios especializado em SaaS e análise de métricas.

Sua tarefa é analisar as métricas fornecidas e gerar insights acionáveis para o admin.

Retorne um JSON com a seguinte estrutura:
{
  "resumo": "Resumo geral em 1-2 frases",
  "dicas_conversao": ["dica 1", "dica 2", "dica 3"],
  "sugestoes_roi": ["sugestão 1", "sugestão 2"],
  "percentual_anuncios": 15,
  "analise_lucro": "Análise do lucro atual e projeções",
  "progresso_objetivo": 65.5
}

Seja específico, prático e baseado nos dados reais fornecidos."""

            metricas_texto = f"""
Métricas do sistema:
- Total de clientes: {metricas['total_clientes']}
- Clientes ativos: {metricas['clientes_ativos']}
- Novos clientes (7 dias): {len(metricas['novos_clientes'])}
- Cancelamentos (30 dias): {len(metricas['cancelados'])}

Novos clientes:
{json.dumps(metricas['novos_clientes'], indent=2, ensure_ascii=False)}

Cancelamentos:
{json.dumps(metricas['cancelados'], indent=2, ensure_ascii=False)}
"""

            if objetivo_mensal:
                metricas_texto += f"\nObjetivo mensal de faturamento: R$ {objetivo_mensal:,.2f}"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=metricas_texto)
            ]
            
            response = llm.invoke(messages)
            
            # Parse JSON da resposta
            dicas = json.loads(response.content)
            
            # Adicionar métricas brutas
            dicas["metricas"] = metricas
            
            logger.info("✅ Dicas geradas com sucesso")
            
            return dicas
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar dicas com IA: {str(e)}", exc_info=True)
            # Retornar dicas padrão em caso de erro
            return {
                "resumo": "Não foi possível gerar dicas no momento.",
                "dicas_conversao": [],
                "sugestoes_roi": [],
                "percentual_anuncios": 10,
                "analise_lucro": "Análise indisponível",
                "progresso_objetivo": 0,
                "metricas": metricas
            }
    
    @staticmethod
    def configurar_objetivo_mensal(db: Session, admin_id: int, objetivo: float) -> bool:
        """
        Configura objetivo mensal de faturamento
        
        Args:
            db: Sessão do banco
            admin_id: ID do admin
            objetivo: Valor do objetivo
            
        Returns:
            bool: True se configurado com sucesso
        """
        try:
            # Buscar última dica
            ultima_dica = db.query(DicaIA).filter(
                DicaIA.admin_id == admin_id
            ).order_by(DicaIA.created_at.desc()).first()
            
            if ultima_dica:
                ultima_dica.objetivo_mensal = objetivo
            else:
                # Criar nova dica com objetivo
                dica = DicaIA(
                    admin_id=admin_id,
                    conteudo={},
                    objetivo_mensal=objetivo
                )
                db.add(dica)
            
            db.commit()
            
            logger.info(f"✅ Objetivo mensal configurado: R$ {objetivo:,.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar objetivo: {str(e)}", exc_info=True)
            db.rollback()
            return False
    
    @staticmethod
    def obter_dicas_atuais(db: Session, admin_id: int) -> Optional[Dict]:
        """
        Obtém dicas atuais (última gerada)
        
        Args:
            db: Sessão do banco
            admin_id: ID do admin
            
        Returns:
            Dict com dicas ou None
        """
        dica = db.query(DicaIA).filter(
            DicaIA.admin_id == admin_id
        ).order_by(DicaIA.created_at.desc()).first()
        
        if not dica:
            return None
        
        return {
            "conteudo": dica.conteudo,
            "objetivo_mensal": dica.objetivo_mensal,
            "created_at": dica.created_at.isoformat()
        }
