"""
Service para gerenciar fallback para atendimento humano
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional

from app.db.models.conversa import Conversa, StatusConversa, MotivoFallback
from app.services.configuracoes import ConfiguracaoService
from app.services.email import EmailService

logger = logging.getLogger(__name__)


class FallbackService:
    """Service para gerenciar fallback e atendimento humano"""
    
    @staticmethod
    def acionar_fallback(
        db: Session,
        cliente_id: int,
        numero_whatsapp: str,
        motivo: str,
        ultima_mensagem: Optional[str] = None
    ) -> Conversa:
        """
        Aciona fallback para atendimento humano
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente
            numero_whatsapp: Número do WhatsApp
            motivo: Motivo do fallback ('baixa_confianca' ou 'solicitacao_manual')
            ultima_mensagem: Última mensagem do cliente (opcional)
            
        Returns:
            Conversa: Conversa atualizada
        """
        # Buscar ou criar conversa
        conversa = db.query(Conversa).filter(
            Conversa.cliente_id == cliente_id,
            Conversa.numero_whatsapp == numero_whatsapp
        ).first()
        
        if not conversa:
            conversa = Conversa(
                cliente_id=cliente_id,
                numero_whatsapp=numero_whatsapp,
                status="aguardando_humano",
                motivo_fallback=motivo,
                ultima_mensagem_em=datetime.utcnow()
            )
            db.add(conversa)
            logger.info(f"Nova conversa criada para fallback: {numero_whatsapp}")
        else:
            conversa.status = "aguardando_humano"
            conversa.motivo_fallback = motivo
            conversa.ultima_mensagem_em = datetime.utcnow()
            logger.info(f"Conversa {conversa.id} atualizada para aguardando_humano")
        
        db.commit()
        db.refresh(conversa)
        
        # Buscar configurações do cliente
        config = ConfiguracaoService.buscar_ou_criar(db, cliente_id)
        
        # Enviar mensagem de fallback (será implementado na integração com WhatsApp)
        logger.info(f"Fallback acionado: conversa_id={conversa.id}, motivo={motivo}")
        
        # Notificar humano
        try:
            FallbackService.notificar_humano(
                db=db,
                conversa_id=conversa.id,
                cliente_id=cliente_id,
                numero_whatsapp=numero_whatsapp,
                motivo=motivo,
                ultima_mensagem=ultima_mensagem
            )
        except Exception as e:
            logger.error(f"Erro ao notificar humano: {e}")
        
        return conversa
    
    @staticmethod
    def notificar_humano(
        db: Session,
        conversa_id: int,
        cliente_id: int,
        numero_whatsapp: str,
        motivo: str,
        ultima_mensagem: Optional[str] = None
    ):
        """
        Notifica humano sobre necessidade de atendimento
        
        Args:
            db: Sessão do banco
            conversa_id: ID da conversa
            cliente_id: ID do cliente
            numero_whatsapp: Número do WhatsApp
            motivo: Motivo do fallback
            ultima_mensagem: Última mensagem do cliente
        """
        # Buscar configurações para obter email de notificação
        config = ConfiguracaoService.buscar_ou_criar(db, cliente_id)
        
        if not hasattr(config, 'notificar_email') or not config.notificar_email:
            logger.warning(f"Email de notificação não configurado para cliente {cliente_id}")
            return
        
        # Montar mensagem de email
        motivo_texto = "Baixa confiança na resposta" if motivo == "baixa_confianca" else "Solicitação manual do cliente"
        
        assunto = f"[WhatsApp Bot] Cliente aguardando atendimento - {numero_whatsapp}"
        
        corpo = f"""
Olá,

Um cliente precisa de atendimento humano:

Cliente ID: {cliente_id}
Número WhatsApp: {numero_whatsapp}
Motivo: {motivo_texto}
Última mensagem: "{ultima_mensagem or 'N/A'}"

Acesse o dashboard para assumir a conversa:
http://localhost:3000/dashboard/conversas/{conversa_id}

---
WhatsApp AI Bot
        """
        
        try:
            EmailService.enviar_email(
                destinatario=config.notificar_email,
                assunto=assunto,
                corpo=corpo
            )
            logger.info(f"Email de notificação enviado para {config.notificar_email}")
        except Exception as e:
            logger.error(f"Erro ao enviar email de notificação: {e}")
            raise
    
    @staticmethod
    def assumir_conversa(
        db: Session,
        conversa_id: int,
        atendente_email: str
    ) -> Conversa:
        """
        Atendente assume uma conversa
        
        Args:
            db: Sessão do banco
            conversa_id: ID da conversa
            atendente_email: Email do atendente
            
        Returns:
            Conversa: Conversa atualizada
        """
        conversa = db.query(Conversa).filter(Conversa.id == conversa_id).first()
        
        if not conversa:
            raise ValueError(f"Conversa {conversa_id} não encontrada")
        
        conversa.assumida_por = atendente_email
        conversa.assumida_em = datetime.utcnow()
        
        db.commit()
        db.refresh(conversa)
        
        logger.info(f"Conversa {conversa_id} assumida por {atendente_email}")
        
        return conversa
    
    @staticmethod
    def verificar_timeout_24h(db: Session):
        """
        Verifica conversas aguardando humano há mais de 24h e envia mensagem de retorno
        
        Args:
            db: Sessão do banco
        """
        # Buscar conversas aguardando há mais de 24h
        limite = datetime.utcnow() - timedelta(hours=24)
        
        conversas = db.query(Conversa).filter(
            Conversa.status == "aguardando_humano",
            Conversa.ultima_mensagem_em < limite,
            Conversa.assumida_por == None
        ).all()
        
        logger.info(f"Verificando timeout 24h: {len(conversas)} conversas encontradas")
        
        for conversa in conversas:
            try:
                # Buscar configurações do cliente
                config = ConfiguracaoService.buscar_ou_criar(db, conversa.cliente_id)
                
                # Enviar mensagem de retorno (será implementado na integração com WhatsApp)
                logger.info(f"Enviando mensagem_retorno_24h para conversa {conversa.id}")
                # TODO: WhatsAppService.enviar_mensagem(conversa.numero_whatsapp, config.mensagem_retorno_24h)
                
                # Voltar para modo automático
                conversa.status = "ativa"
                conversa.motivo_fallback = None
                db.commit()
                
                logger.info(f"Conversa {conversa.id} voltou para modo automático após 24h")
                
            except Exception as e:
                logger.error(f"Erro ao processar timeout da conversa {conversa.id}: {e}")
                db.rollback()
        
        return len(conversas)
    
    @staticmethod
    def buscar_conversas_aguardando(db: Session, cliente_id: Optional[int] = None):
        """
        Busca conversas aguardando atendimento humano
        
        Args:
            db: Sessão do banco
            cliente_id: ID do cliente (opcional, para filtrar)
            
        Returns:
            List[Conversa]: Lista de conversas aguardando
        """
        query = db.query(Conversa).filter(
            Conversa.status == "aguardando_humano"
        )
        
        if cliente_id:
            query = query.filter(Conversa.cliente_id == cliente_id)
        
        conversas = query.order_by(Conversa.ultima_mensagem_em.asc()).all()
        
        logger.info(f"Encontradas {len(conversas)} conversas aguardando atendimento")
        
        return conversas
