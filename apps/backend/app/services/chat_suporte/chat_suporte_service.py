"""
ChatSuporteService - Serviço de chat suporte com IA
Task 11.2
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.db.models.chat_suporte import ChatSuporteMensagem
from app.services.ai import AIService

logger = logging.getLogger(__name__)


class ChatSuporteService:
    """Serviço para gerenciar chat de suporte com IA"""
    
    @staticmethod
    def enviar_mensagem(db: Session, cliente_id: int, mensagem: str) -> Dict[str, Any]:
        """
        Envia mensagem no chat suporte e recebe resposta automática da IA
        
        Args:
            db: Session do banco de dados
            cliente_id: ID do cliente
            mensagem: Mensagem do cliente
        
        Returns:
            Dict com resposta da IA e confiança
            {
                "resposta": str,
                "confianca": float,
                "deve_abrir_ticket": bool
            }
        """
        try:
            # Salvar mensagem do cliente
            mensagem_cliente = ChatSuporteMensagem(
                cliente_id=cliente_id,
                remetente_tipo='cliente',
                mensagem=mensagem,
                confianca=None
            )
            db.add(mensagem_cliente)
            db.commit()
            
            logger.info(f'[CHAT SUPORTE] Mensagem recebida do cliente {cliente_id}')
            
            # Gerar resposta com IA usando conhecimento do admin
            resultado = ChatSuporteService.responder_com_ia(db, cliente_id, mensagem)
            
            resposta = resultado['resposta']
            confianca = resultado['confianca']
            
            # Salvar resposta da IA
            mensagem_ia = ChatSuporteMensagem(
                cliente_id=cliente_id,
                remetente_tipo='ia',
                mensagem=resposta,
                confianca=confianca
            )
            db.add(mensagem_ia)
            db.commit()
            
            logger.info(f'[CHAT SUPORTE] Resposta IA gerada com confiança {confianca:.2f}')
            
            # Verificar se deve sugerir abrir ticket (confiança < 0.7)
            deve_abrir_ticket = confianca < 0.7
            
            return {
                "resposta": resposta,
                "confianca": confianca,
                "deve_abrir_ticket": deve_abrir_ticket
            }
            
        except Exception as e:
            logger.error(f'[CHAT SUPORTE] Erro ao processar mensagem: {e}')
            raise
    
    @staticmethod
    def responder_com_ia(db: Session, cliente_id: int, mensagem: str) -> Dict[str, Any]:
        """
        Gera resposta usando IA com conhecimento do admin
        
        Args:
            db: Session do banco de dados
            cliente_id: ID do cliente
            mensagem: Mensagem do cliente
        
        Returns:
            Dict com resposta e confiança
        """
        try:
            # Buscar conhecimento do admin (ID 1 - admin principal)
            # Nota: Em produção, buscar conhecimento específico de suporte
            from app.db.models.conhecimento import Conhecimento
            
            conhecimento_admin = db.query(Conhecimento).filter(
                Conhecimento.cliente_id == 1  # Admin principal
            ).first()
            
            if not conhecimento_admin or not conhecimento_admin.conteudo:
                # Se não tem conhecimento, resposta genérica
                return {
                    "resposta": "Desculpe, não encontrei informações sobre isso. Por favor, abra um ticket para que possamos ajudá-lo melhor.",
                    "confianca": 0.3
                }
            
            # Usar AIService para gerar resposta
            # Criar session_id único para chat suporte
            session_id = f'suporte_cliente_{cliente_id}'
            
            resultado = AIService.processar_mensagem(
                cliente_id=1,  # Usar conhecimento do admin
                chat_id=session_id,
                mensagem=mensagem,
                tom='profissional',
                nome_empresa='Suporte',
                primeira_mensagem=False
            )
            
            return {
                "resposta": resultado['resposta'],
                "confianca": resultado['confianca']
            }
            
        except Exception as e:
            logger.error(f'[CHAT SUPORTE] Erro ao gerar resposta IA: {e}')
            return {
                "resposta": "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.",
                "confianca": 0.0
            }
    
    @staticmethod
    def obter_historico(db: Session, cliente_id: int, limit: int = 50) -> List[ChatSuporteMensagem]:
        """
        Retorna histórico de mensagens do chat suporte
        
        Args:
            db: Session do banco de dados
            cliente_id: ID do cliente
            limit: Limite de mensagens
        
        Returns:
            Lista de mensagens ordenadas por data
        """
        return db.query(ChatSuporteMensagem).filter(
            ChatSuporteMensagem.cliente_id == cliente_id
        ).order_by(ChatSuporteMensagem.created_at.asc()).limit(limit).all()
    
    @staticmethod
    def limpar_historico(db: Session, cliente_id: int) -> bool:
        """
        Limpa histórico de mensagens do cliente
        
        Args:
            db: Session do banco de dados
            cliente_id: ID do cliente
        
        Returns:
            True se limpou com sucesso
        """
        try:
            db.query(ChatSuporteMensagem).filter(
                ChatSuporteMensagem.cliente_id == cliente_id
            ).delete()
            db.commit()
            return True
        except Exception as e:
            logger.error(f'[CHAT SUPORTE] Erro ao limpar histórico: {e}')
            return False
