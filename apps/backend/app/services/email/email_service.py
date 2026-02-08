"""
Serviço de envio de emails
Suporta SendGrid e modo de desenvolvimento (apenas log)
"""
import logging
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Serviço para envio de emails"""
    
    @staticmethod
    def enviar_email_boas_vindas(
        email_destino: str,
        nome_cliente: str,
        senha: str,
        dashboard_url: str = "http://localhost:3000/login"
    ) -> bool:
        """
        Envia email de boas-vindas com credenciais de acesso
        
        Args:
            email_destino: Email do cliente
            nome_cliente: Nome do cliente
            senha: Senha gerada
            dashboard_url: URL do dashboard
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        assunto = "🎉 Bem-vindo ao WhatsApp AI Bot - Suas Credenciais de Acesso"
        
        corpo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .credentials {{ background: white; padding: 20px; border-left: 4px solid #667eea; margin: 20px 0; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Bem-vindo!</h1>
                    <p>Sua conta foi criada com sucesso</p>
                </div>
                <div class="content">
                    <p>Olá <strong>{nome_cliente}</strong>,</p>
                    
                    <p>Seu pagamento foi aprovado e sua conta no <strong>WhatsApp AI Bot</strong> está pronta para uso!</p>
                    
                    <div class="credentials">
                        <h3>🔑 Suas Credenciais de Acesso:</h3>
                        <p><strong>Email:</strong> {email_destino}</p>
                        <p><strong>Senha:</strong> {senha}</p>
                    </div>
                    
                    <p><strong>⚠️ Importante:</strong> Guarde esta senha em um local seguro. Você pode alterá-la após o primeiro login.</p>
                    
                    <center>
                        <a href="{dashboard_url}" class="button">Acessar Dashboard</a>
                    </center>
                    
                    <h3>📋 Próximos Passos:</h3>
                    <ol>
                        <li>Faça login no dashboard</li>
                        <li>Configure seu conhecimento (base de dados do bot)</li>
                        <li>Conecte seu WhatsApp via QR Code</li>
                        <li>Comece a atender seus clientes com IA!</li>
                    </ol>
                    
                    <p>Se tiver alguma dúvida, estamos aqui para ajudar!</p>
                    
                    <p>Atenciosamente,<br><strong>Equipe WhatsApp AI Bot</strong></p>
                </div>
                <div class="footer">
                    <p>Este é um email automático. Por favor, não responda.</p>
                    <p>© 2026 WhatsApp AI Bot. Todos os direitos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        corpo_texto = f"""
        Bem-vindo ao WhatsApp AI Bot!
        
        Olá {nome_cliente},
        
        Seu pagamento foi aprovado e sua conta está pronta para uso!
        
        SUAS CREDENCIAIS DE ACESSO:
        Email: {email_destino}
        Senha: {senha}
        
        IMPORTANTE: Guarde esta senha em um local seguro.
        
        Acesse o dashboard: {dashboard_url}
        
        Próximos Passos:
        1. Faça login no dashboard
        2. Configure seu conhecimento (base de dados do bot)
        3. Conecte seu WhatsApp via QR Code
        4. Comece a atender seus clientes com IA!
        
        Atenciosamente,
        Equipe WhatsApp AI Bot
        """
        
        return EmailService._enviar_email(
            email_destino=email_destino,
            assunto=assunto,
            corpo_html=corpo_html,
            corpo_texto=corpo_texto
        )
    
    @staticmethod
    def _enviar_email(
        email_destino: str,
        assunto: str,
        corpo_html: str,
        corpo_texto: str
    ) -> bool:
        """
        Envia email usando SendGrid ou modo de desenvolvimento
        
        Args:
            email_destino: Email do destinatário
            assunto: Assunto do email
            corpo_html: Corpo do email em HTML
            corpo_texto: Corpo do email em texto plano
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        # Modo de desenvolvimento: apenas loga o email
        if not hasattr(settings, 'SENDGRID_API_KEY') or not settings.SENDGRID_API_KEY:
            logger.info("=" * 80)
            logger.info("📧 MODO DESENVOLVIMENTO - Email não enviado (SendGrid não configurado)")
            logger.info("=" * 80)
            logger.info(f"Para: {email_destino}")
            logger.info(f"Assunto: {assunto}")
            logger.info("-" * 80)
            logger.info("Corpo (texto):")
            logger.info(corpo_texto)
            logger.info("=" * 80)
            return True
        
        # Modo produção: envia via SendGrid
        try:
            email_remetente = getattr(settings, 'SENDGRID_FROM_EMAIL', 'noreply@whatsappaibot.com')
            nome_remetente = getattr(settings, 'SENDGRID_FROM_NAME', 'WhatsApp AI Bot')
            
            message = Mail(
                from_email=Email(email_remetente, nome_remetente),
                to_emails=To(email_destino),
                subject=assunto,
                plain_text_content=Content("text/plain", corpo_texto),
                html_content=Content("text/html", corpo_html)
            )
            
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Email enviado com sucesso para {email_destino}")
                return True
            else:
                logger.error(f"❌ Erro ao enviar email: Status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email via SendGrid: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def enviar_reset_senha_admin(
        email: str,
        nome: str,
        nova_senha: str,
        dashboard_url: str = "http://localhost:3000/login"
    ) -> bool:
        """
        Envia email com nova senha resetada pelo admin
        
        Args:
            email: Email do cliente
            nome: Nome do cliente
            nova_senha: Nova senha gerada
            dashboard_url: URL do dashboard
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        assunto = "🔐 Sua senha foi resetada - WhatsApp AI Bot"
        
        corpo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .credentials {{ background: white; padding: 20px; border-left: 4px solid #667eea; margin: 20px 0; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Senha Resetada</h1>
                    <p>Sua senha foi alterada pelo administrador</p>
                </div>
                <div class="content">
                    <p>Olá <strong>{nome}</strong>,</p>
                    
                    <p>Sua senha foi resetada pelo administrador do sistema.</p>
                    
                    <div class="credentials">
                        <h3>🔑 Suas Novas Credenciais:</h3>
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Nova Senha:</strong> {nova_senha}</p>
                    </div>
                    
                    <div class="alert">
                        <p><strong>⚠️ Importante:</strong></p>
                        <ul>
                            <li>Esta é uma senha temporária gerada automaticamente</li>
                            <li>Recomendamos que você altere sua senha após o login</li>
                            <li>Guarde esta senha em um local seguro</li>
                        </ul>
                    </div>
                    
                    <center>
                        <a href="{dashboard_url}" class="button">Fazer Login</a>
                    </center>
                    
                    <p>Se você não solicitou esta alteração, entre em contato com o suporte imediatamente.</p>
                    
                    <p>Atenciosamente,<br><strong>Equipe WhatsApp AI Bot</strong></p>
                </div>
                <div class="footer">
                    <p>Este é um email automático. Por favor, não responda.</p>
                    <p>© 2026 WhatsApp AI Bot. Todos os direitos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        corpo_texto = f"""
        Senha Resetada - WhatsApp AI Bot
        
        Olá {nome},
        
        Sua senha foi resetada pelo administrador do sistema.
        
        SUAS NOVAS CREDENCIAIS:
        Email: {email}
        Nova Senha: {nova_senha}
        
        IMPORTANTE:
        - Esta é uma senha temporária gerada automaticamente
        - Recomendamos que você altere sua senha após o login
        - Guarde esta senha em um local seguro
        
        Acesse o dashboard: {dashboard_url}
        
        Se você não solicitou esta alteração, entre em contato com o suporte imediatamente.
        
        Atenciosamente,
        Equipe WhatsApp AI Bot
        """
        
        return EmailService._enviar_email(
            email_destino=email,
            assunto=assunto,
            corpo_html=corpo_html,
            corpo_texto=corpo_texto
        )
