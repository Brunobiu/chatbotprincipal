"""
Script para testar envio de email de boas-vindas
USO: python testar_email.py
"""
from app.services.email.email_service import EmailService

def testar_email():
    """Testa envio de email de boas-vindas"""
    print("\n" + "="*80)
    print("🧪 TESTANDO ENVIO DE EMAIL DE BOAS-VINDAS")
    print("="*80 + "\n")
    
    # Dados de teste
    email_destino = "cliente@exemplo.com"
    nome_cliente = "João Silva"
    senha = "SenhaSegura123!"
    dashboard_url = "http://localhost:3000/login"
    
    print(f"📧 Enviando email para: {email_destino}")
    print(f"👤 Nome: {nome_cliente}")
    print(f"🔑 Senha: {senha}")
    print(f"🔗 Dashboard: {dashboard_url}\n")
    
    # Enviar email
    sucesso = EmailService.enviar_email_boas_vindas(
        email_destino=email_destino,
        nome_cliente=nome_cliente,
        senha=senha,
        dashboard_url=dashboard_url
    )
    
    if sucesso:
        print("\n✅ Email enviado/logado com sucesso!")
        print("\n💡 NOTA: Como SendGrid não está configurado, o email foi apenas logado.")
        print("   Para enviar emails reais, configure SENDGRID_API_KEY no .env")
    else:
        print("\n❌ Erro ao enviar email!")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    testar_email()
