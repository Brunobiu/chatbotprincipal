"""
Serviço de SMS usando AWS SNS
"""
import random
import logging
from datetime import datetime, timedelta
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session

from app.db.models.sms_verification import SMSVerification
from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Serviço para envio e verificação de SMS"""
    
    def __init__(self):
        """Inicializa cliente SNS"""
        self.sns_client = None
        
        # Inicializar SNS se credenciais disponíveis
        if hasattr(settings, 'AWS_ACCESS_KEY_ID') and settings.AWS_ACCESS_KEY_ID:
            try:
                self.sns_client = boto3.client(
                    'sns',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                logger.info("✅ AWS SNS inicializado com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar SNS: {e}")
        else:
            logger.warning("⚠️ AWS SNS não configurado - modo simulação")
    
    def gerar_codigo(self) -> str:
        """Gera código de 6 dígitos"""
        return str(random.randint(100000, 999999))
    
    def formatar_telefone(self, telefone: str) -> str:
        """
        Formata telefone para padrão internacional
        Exemplo: (11) 99999-9999 -> +5511999999999
        """
        # Remove caracteres não numéricos
        numeros = ''.join(filter(str.isdigit, telefone))
        
        # Se não tem código do país, adiciona +55 (Brasil)
        if not numeros.startswith('55'):
            numeros = '55' + numeros
        
        return '+' + numeros
    
    async def enviar_sms(self, telefone: str, db: Session) -> dict:
        """
        Envia código de verificação por SMS
        
        Args:
            telefone: Número de telefone
            db: Sessão do banco
            
        Returns:
            dict com status e mensagem
        """
        try:
            # Formatar telefone
            telefone_formatado = self.formatar_telefone(telefone)
            
            # Verificar se já existe verificação recente (últimos 2 minutos)
            dois_minutos_atras = datetime.utcnow() - timedelta(minutes=2)
            verificacao_recente = db.query(SMSVerification).filter(
                SMSVerification.telefone == telefone_formatado,
                SMSVerification.created_at >= dois_minutos_atras
            ).first()
            
            if verificacao_recente:
                return {
                    "success": False,
                    "message": "Aguarde 2 minutos antes de solicitar novo código"
                }
            
            # Gerar código
            codigo = self.gerar_codigo()
            
            # Criar registro no banco
            expira_em = datetime.utcnow() + timedelta(minutes=10)
            verificacao = SMSVerification(
                telefone=telefone_formatado,
                codigo=codigo,
                expira_em=expira_em
            )
            db.add(verificacao)
            db.commit()
            
            # Enviar SMS
            mensagem = f"Seu código de verificação é: {codigo}\n\nVálido por 10 minutos."
            
            if self.sns_client:
                # Enviar via AWS SNS
                try:
                    response = self.sns_client.publish(
                        PhoneNumber=telefone_formatado,
                        Message=mensagem,
                        MessageAttributes={
                            'AWS.SNS.SMS.SMSType': {
                                'DataType': 'String',
                                'StringValue': 'Transactional'
                            }
                        }
                    )
                    logger.info(f"✅ SMS enviado para {telefone_formatado}: {response['MessageId']}")
                    return {
                        "success": True,
                        "message": "Código enviado com sucesso",
                        "telefone": telefone_formatado
                    }
                except ClientError as e:
                    logger.error(f"❌ Erro ao enviar SMS: {e}")
                    return {
                        "success": False,
                        "message": f"Erro ao enviar SMS: {str(e)}"
                    }
            else:
                # Modo simulação (desenvolvimento)
                logger.info(f"📱 [SIMULAÇÃO] SMS para {telefone_formatado}: {codigo}")
                return {
                    "success": True,
                    "message": "Código enviado (modo simulação)",
                    "telefone": telefone_formatado,
                    "codigo_dev": codigo  # Apenas em dev
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar SMS: {e}")
            return {
                "success": False,
                "message": f"Erro ao enviar SMS: {str(e)}"
            }
    
    async def verificar_codigo(self, telefone: str, codigo: str, db: Session) -> dict:
        """
        Verifica código SMS
        
        Args:
            telefone: Número de telefone
            codigo: Código de 6 dígitos
            db: Sessão do banco
            
        Returns:
            dict com status e mensagem
        """
        try:
            # Formatar telefone
            telefone_formatado = self.formatar_telefone(telefone)
            
            # Buscar verificação mais recente
            verificacao = db.query(SMSVerification).filter(
                SMSVerification.telefone == telefone_formatado,
                SMSVerification.verificado == False
            ).order_by(SMSVerification.created_at.desc()).first()
            
            if not verificacao:
                return {
                    "success": False,
                    "message": "Nenhuma verificação pendente encontrada"
                }
            
            # Verificar se expirou
            if datetime.utcnow() > verificacao.expira_em:
                return {
                    "success": False,
                    "message": "Código expirado. Solicite um novo código"
                }
            
            # Verificar tentativas (máx 3)
            if verificacao.tentativas >= 3:
                return {
                    "success": False,
                    "message": "Número máximo de tentativas excedido. Solicite um novo código"
                }
            
            # Verificar código
            if verificacao.codigo != codigo:
                verificacao.tentativas += 1
                db.commit()
                return {
                    "success": False,
                    "message": f"Código incorreto. Tentativas restantes: {3 - verificacao.tentativas}"
                }
            
            # Código correto!
            verificacao.verificado = True
            db.commit()
            
            logger.info(f"✅ Telefone verificado: {telefone_formatado}")
            return {
                "success": True,
                "message": "Telefone verificado com sucesso",
                "telefone": telefone_formatado
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar código: {e}")
            return {
                "success": False,
                "message": f"Erro ao verificar código: {str(e)}"
            }


# Instância global
sms_service = SMSService()
