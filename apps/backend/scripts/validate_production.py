#!/usr/bin/env python3
"""
Script de validação para ambiente de produção
Verifica se todas as configurações necessárias estão corretas
"""
import os
import sys
from typing import List, Tuple


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def check_env_var(var_name: str, required: bool = True, check_value: str = None) -> Tuple[bool, str]:
    """Verifica se variável de ambiente existe e opcionalmente seu valor"""
    value = os.getenv(var_name)
    
    if not value:
        if required:
            return False, f"❌ {var_name} não está definida"
        return True, f"⚠️  {var_name} não está definida (opcional)"
    
    if check_value and value == check_value:
        return False, f"❌ {var_name} ainda está com valor de desenvolvimento: {check_value}"
    
    # Verificar se não é valor de exemplo/placeholder
    if value in ['your_key_here', 'change_me', 'example', 'test']:
        return False, f"❌ {var_name} está com valor placeholder: {value}"
    
    return True, f"✅ {var_name} está configurada"


def validate_production() -> bool:
    """Valida configurações de produção"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("🔍 VALIDAÇÃO DE AMBIENTE DE PRODUÇÃO")
    print(f"{'='*60}{Colors.END}\n")
    
    all_checks_passed = True
    warnings: List[str] = []
    
    # 1. Variáveis Críticas
    print(f"{Colors.BLUE}📋 1. VARIÁVEIS CRÍTICAS{Colors.END}")
    critical_vars = [
        ('DATABASE_URL', True, None),
        ('REDIS_URL', True, None),
        ('SECRET_KEY', True, None),
        ('OPENAI_API_KEY', True, None),
        ('STRIPE_SECRET_KEY', True, None),
    ]
    
    for var_name, required, check_value in critical_vars:
        passed, message = check_env_var(var_name, required, check_value)
        print(f"  {message}")
        if not passed:
            all_checks_passed = False
    
    # 2. Stripe
    print(f"\n{Colors.BLUE}💳 2. STRIPE{Colors.END}")
    stripe_key = os.getenv('STRIPE_SECRET_KEY', '')
    if stripe_key.startswith('sk_test_'):
        print(f"  {Colors.RED}❌ STRIPE_SECRET_KEY está em modo TEST{Colors.END}")
        print(f"     Use chave de produção (sk_live_...)")
        all_checks_passed = False
    elif stripe_key.startswith('sk_live_'):
        print(f"  {Colors.GREEN}✅ STRIPE_SECRET_KEY está em modo PRODUÇÃO{Colors.END}")
    else:
        print(f"  {Colors.RED}❌ STRIPE_SECRET_KEY inválida{Colors.END}")
        all_checks_passed = False
    
    # 3. URLs e Domínios
    print(f"\n{Colors.BLUE}🌐 3. URLs E DOMÍNIOS{Colors.END}")
    frontend_url = os.getenv('FRONTEND_URL', '')
    if 'localhost' in frontend_url or '127.0.0.1' in frontend_url:
        print(f"  {Colors.RED}❌ FRONTEND_URL aponta para localhost{Colors.END}")
        all_checks_passed = False
    else:
        print(f"  ✅ FRONTEND_URL: {frontend_url}")
    
    # 4. Email
    print(f"\n{Colors.BLUE}📧 4. EMAIL (SMTP){Colors.END}")
    smtp_vars = [
        ('SMTP_HOST', True, None),
        ('SMTP_PORT', True, None),
        ('SMTP_USER', True, None),
        ('SMTP_PASSWORD', True, None),
    ]
    
    for var_name, required, check_value in smtp_vars:
        passed, message = check_env_var(var_name, required, check_value)
        print(f"  {message}")
        if not passed:
            warnings.append(f"Email pode não funcionar: {var_name} não configurada")
    
    # 5. Evolution API
    print(f"\n{Colors.BLUE}📱 5. EVOLUTION API (WHATSAPP){Colors.END}")
    evolution_vars = [
        ('EVOLUTION_API_URL', True, None),
        ('EVOLUTION_INSTANCE_NAME', True, None),
        ('EVOLUTION_AUTHENTICATION_API_KEY', True, None),
    ]
    
    for var_name, required, check_value in evolution_vars:
        passed, message = check_env_var(var_name, required, check_value)
        print(f"  {message}")
        if not passed:
            all_checks_passed = False
    
    # 6. Segurança
    print(f"\n{Colors.BLUE}🔐 6. SEGURANÇA{Colors.END}")
    
    # Verificar SECRET_KEY
    secret_key = os.getenv('SECRET_KEY', '')
    if len(secret_key) < 32:
        print(f"  {Colors.RED}❌ SECRET_KEY muito curta (mínimo 32 caracteres){Colors.END}")
        all_checks_passed = False
    else:
        print(f"  ✅ SECRET_KEY tem tamanho adequado")
    
    # Verificar DEBUG
    debug = os.getenv('DEBUG', 'False').lower()
    if debug == 'true':
        print(f"  {Colors.RED}❌ DEBUG está ATIVADO em produção!{Colors.END}")
        all_checks_passed = False
    else:
        print(f"  ✅ DEBUG está desativado")
    
    # 7. Banco de Dados
    print(f"\n{Colors.BLUE}🗄️  7. BANCO DE DADOS{Colors.END}")
    db_url = os.getenv('DATABASE_URL', '')
    if 'localhost' in db_url or '127.0.0.1' in db_url:
        print(f"  {Colors.YELLOW}⚠️  DATABASE_URL aponta para localhost{Colors.END}")
        warnings.append("Banco de dados local - considere usar banco remoto")
    else:
        print(f"  ✅ DATABASE_URL configurada para servidor remoto")
    
    # Resumo
    print(f"\n{Colors.BLUE}{'='*60}")
    print("📊 RESUMO")
    print(f"{'='*60}{Colors.END}\n")
    
    if all_checks_passed and not warnings:
        print(f"{Colors.GREEN}✅ TODAS AS VALIDAÇÕES PASSARAM!{Colors.END}")
        print(f"{Colors.GREEN}Sistema pronto para produção.{Colors.END}\n")
        return True
    else:
        if not all_checks_passed:
            print(f"{Colors.RED}❌ VALIDAÇÃO FALHOU!{Colors.END}")
            print(f"{Colors.RED}Corrija os erros antes de fazer deploy.{Colors.END}\n")
        
        if warnings:
            print(f"{Colors.YELLOW}⚠️  AVISOS:{Colors.END}")
            for warning in warnings:
                print(f"  • {warning}")
            print()
        
        return False


if __name__ == '__main__':
    # Carregar .env se existir
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print(f"{Colors.GREEN}✅ Arquivo .env carregado{Colors.END}\n")
    except ImportError:
        print(f"{Colors.YELLOW}⚠️  python-dotenv não instalado, usando variáveis do sistema{Colors.END}\n")
    
    success = validate_production()
    sys.exit(0 if success else 1)
