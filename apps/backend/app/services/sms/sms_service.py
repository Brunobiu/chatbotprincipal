"""
Serviço para envio e verificação de SMS
Proteção Anti-Abuso - FASE 4

IMPORTANTE: Para usar em produção, configure:
- Twilio: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
- AWS SNS: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.models.sms_verification import SMSVerification
from app.db.models.cliente import Cliente
from app.db.models.trial_history import TrialHistory
import random
import logging
import os

logger = logging.getLogger(__name__)


class SMSService:
    
    @staticmethod
    def gerar_codigo() -> str:
        """Gera código de 6 dígitos"""
        return str(random.randint(100000, 999999))
    
    @staticmethod
    def enviar_sms_twilio(telefone: str, codigo: str) -> bool:
        """
        Envia SMS via Twilio
        
        Requer variáveis de ambiente:
        - TWILIO_ACCOUNT_SID
        - TWILIO_AUTH_TOKEN
        - TWILIO_PHONE_NUMBER
        """
        try:
            from twilio.rest import Client
            
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_phone = os.getenv('TWILIO_PHONE_NUMBER')
            
            if not all([account_sid, auth_token, from_phone]):
                logger.error("❌ Credenciais Twilio não configuradas")
                return False
            
            client = Client(account_sid, auth_token)
            
            message = client.messages.create(
                body=f"Seu código de verificação é: {codigo}",
                from_=from_phone,
                to=telefone
            )
            
            logger.info(f"✅ SMS enviado via Twilio: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar SMS via Twilio: {e}")
            return False
    
    @staticmethod
    def enviar_sms_aws_sns(telefone: str, codigo: str) -> bool:
        """
        Envia SMS via AWS SNS
        
        Requer variáveis de ambiente:
        - AWS_ACCESS_KEY_ID
        - AWS_SECRET_ACCESS_KEY
        - AWS_REGION
        """
        try:
            import boto3
            
            sns = boto3.client('sns', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            
            response = sns.publish(
                PhoneNumber=telefone,
                Message=f"Seu código de verificação é: {codigo}"
            )
            
            logger.info(f"✅ SMS enviado via AWS SNS: {response['MessageId']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar SMS via AWS SNS: {e}")
            return False
    
    @staticmethod
    def enviar_codigo(db: Session, telefone: str) -> dict:
        """
        Envia código de verificação por SMS
        
        Args:
            db: Sessão do banco
            telefone: Número de telefone (formato: +5511999999999)
            
        Returns:
            dict com status e mensagem
        """
        # Validar formato do telefone
        if not telefone.startswith('+'):
            return {"success": False, "message": "Telefone deve estar no formato internacional (+5511999999999)"}
        
        # PROTEÇÃO: Verificar se telefone já foi usado em trial
        trial_usado = db.query(TrialHistory).filter(
            TrialHistory.whatsapp_number == telefone  # Reutilizando campo
        ).first()
        
        if trial_usado:
            return {
                "success": False,
                "code": "PHONE_ALREADY_USED",
                "message": "Este telefone já foi utilizado em um trial."
            }
        
        # Verificar se já existe código válido (não expirado)
        verificacao_existente = db.query(SMSVerification).filter(
            SMSVerification.telefone == telefone,
            SMSVerification.expires_at > datetime.utcnow(),
            SMSVerification.verificado == False
        ).first()
        
        if verificacao_existente:
            # Já tem código válido, não enviar outro
            tempo_restante = (verificacao_existente.expires_at - datetime.utcnow()).seconds // 60
            return {
                "success": False,
                "message": f"Código já enviado. Aguarde {tempo_restante} minutos para solicitar novo código."
            }
        
        # Gerar novo código
        codigo = SMSService.gerar_codigo()
        expires_at = datetime.utcnow() + timedelta(minutes=10)  # Expira em 10 minutos
        
        # Salvar no banco
        verificacao = SMSVerification(
            telefone=telefone,
            codigo=codigo,
            expires_at=expires_at,
            verificado=False,
            tentativas=0,
            created_at=datetime.utcnow()
        )
        db.add(verificacao)
        db.commit()
        
        # Enviar SMS (tentar Twilio primeiro, depois AWS SNS)
        sms_enviado = SMSService.enviar_sms_twilio(telefone, codigo)
        
        if not sms_enviado:
            sms_enviado = SMSService.enviar_sms_aws_sns(telefone, codigo)
        
        if not sms_enviado:
            # Modo desenvolvimento: retornar código no response (REMOVER EM PRODUÇÃO)
            if os.getenv('ENVIRONMENT') == 'development':
                logger.warning(f"⚠️ MODO DEV: Código SMS = {codigo}")
                return {
                    "success": True,
                    "message": "Código gerado (modo desenvolvimento)",
                    "dev_code": codigo  # REMOVER EM PRODUÇÃO
                }
            
            return {"success": False, "message": "Erro ao enviar SMS. Tente novamente."}
        
        return {"success": True, "message": "Código enviado por SMS"}
    
    @staticmethod
    def verificar_codigo(db: Session, telefone: str, codigo: str) -> dict:
        """
        Verifica código SMS
        
        Args:
            db: Sessão do banco
            telefone: Número de telefone
            codigo: Código de 6 dígitos
            
        Returns:
            dict com status e mensagem
        """
        # Buscar verificação
        verificacao = db.query(SMSVerification).filter(
            SMSVerification.telefone == telefone,
            SMSVerification.verificado == False
        ).order_by(SMSVerification.created_at.desc()).first()
        
        if not verificacao:
            return {"success": False, "message": "Código não encontrado. Solicite um novo código."}
        
        # Verificar se expirou
        if verificacao.expires_at < datetime.utcnow():
            return {"success": False, "message": "Código expirado. Solicite um novo código."}
        
        # Verificar tentativas (máx 3)
        if verificacao.tentativas >= 3:
            return {"success": False, "message": "Número máximo de tentativas excedido. Solicite um novo código."}
        
        # Verificar código
        if verificacao.codigo != codigo:
            verificacao.tentativas += 1
            db.commit()
            tentativas_restantes = 3 - verificacao.tentativas
            return {
                "success": False,
                "message": f"Código incorreto. {tentativas_restantes} tentativas restantes."
            }
        
        # Código correto!
        verificacao.verificado = True
        db.commit()
        
        logger.info(f"✅ Telefone verificado: {telefone}")
        return {"success": True, "message": "Telefone verificado com sucesso!"}
