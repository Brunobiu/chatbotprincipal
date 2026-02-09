"""
Testes de Segurança - FASE 3
Valida proteções contra SQL Injection e criptografia
"""
import pytest
from app.core.validators import (
    EmailValidator,
    StringValidator,
    SQLSafeValidator,
    PhoneValidator,
    sanitize_string,
    validate_sql_safe
)
from app.core.encryption import DataEncryption, generate_encryption_key


class TestSQLInjectionProtection:
    """Testes de proteção contra SQL Injection"""
    
    def test_sql_injection_or_equals(self):
        """Testa detecção de OR 1=1"""
        malicious = "test' OR 1=1 --"
        
        with pytest.raises(ValueError, match="SQL injection"):
            SQLSafeValidator.validate(malicious)
    
    def test_sql_injection_union_select(self):
        """Testa detecção de UNION SELECT"""
        malicious = "test' UNION SELECT * FROM users --"
        
        with pytest.raises(ValueError, match="SQL injection"):
            SQLSafeValidator.validate(malicious)
    
    def test_sql_injection_drop_table(self):
        """Testa detecção de DROP TABLE"""
        malicious = "test'; DROP TABLE users; --"
        
        with pytest.raises(ValueError, match="SQL injection"):
            SQLSafeValidator.validate(malicious)
    
    def test_sql_injection_comment(self):
        """Testa detecção de comentários SQL"""
        malicious = "test' -- comment"
        
        with pytest.raises(ValueError, match="SQL injection"):
            SQLSafeValidator.validate(malicious)
    
    def test_safe_string_passes(self):
        """Testa que string segura passa"""
        safe = "Este é um texto normal"
        result = SQLSafeValidator.validate(safe)
        assert result == safe
    
    def test_email_with_sql_injection(self):
        """Testa email com SQL injection"""
        malicious_email = "test@test.com' OR '1'='1"
        
        with pytest.raises(ValueError):
            EmailValidator.validate(malicious_email)


class TestStringValidation:
    """Testes de validação de strings"""
    
    def test_sanitize_removes_null_bytes(self):
        """Testa remoção de null bytes"""
        text = "test\x00data"
        result = StringValidator.sanitize(text)
        assert '\x00' not in result
    
    def test_sanitize_limits_length(self):
        """Testa limite de tamanho"""
        long_text = "A" * 1000
        result = StringValidator.sanitize(long_text, max_length=100)
        assert len(result) == 100
    
    def test_sanitize_removes_control_chars(self):
        """Testa remoção de caracteres de controle"""
        text = "test\x01\x02data"
        result = StringValidator.sanitize(text)
        assert '\x01' not in result
        assert '\x02' not in result
    
    def test_sanitize_filename_removes_path_traversal(self):
        """Testa remoção de path traversal"""
        filename = "../../../etc/passwd"
        result = StringValidator.sanitize_filename(filename)
        assert '..' not in result
        assert '/' not in result
    
    def test_sanitize_empty_string(self):
        """Testa string vazia"""
        result = StringValidator.sanitize("")
        assert result == ""


class TestEmailValidation:
    """Testes de validação de email"""
    
    def test_valid_email(self):
        """Testa email válido"""
        email = "test@example.com"
        result = EmailValidator.validate(email)
        assert result == email
    
    def test_email_normalization(self):
        """Testa normalização de email"""
        email = "  TEST@EXAMPLE.COM  "
        result = EmailValidator.validate(email)
        assert result == "test@example.com"
    
    def test_email_too_long(self):
        """Testa email muito longo"""
        long_email = "a" * 250 + "@test.com"
        
        with pytest.raises(ValueError, match="muito longo"):
            EmailValidator.validate(long_email)
    
    def test_invalid_email_format(self):
        """Testa formato inválido"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "test@",
            "test@@example.com",
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValueError, match="inválido"):
                EmailValidator.validate(email)


class TestPhoneValidation:
    """Testes de validação de telefone"""
    
    def test_valid_phone(self):
        """Testa telefone válido"""
        phone = "+5511999999999"
        result = PhoneValidator.validate(phone)
        assert result == "+5511999999999"
    
    def test_phone_removes_non_digits(self):
        """Testa remoção de caracteres não numéricos"""
        phone = "(11) 99999-9999"
        result = PhoneValidator.validate(phone)
        assert result == "11999999999"
    
    def test_phone_too_short(self):
        """Testa telefone muito curto"""
        phone = "123"
        
        with pytest.raises(ValueError, match="inválido"):
            PhoneValidator.validate(phone)
    
    def test_phone_too_long(self):
        """Testa telefone muito longo"""
        phone = "1234567890123456"
        
        with pytest.raises(ValueError, match="inválido"):
            PhoneValidator.validate(phone)


class TestEncryption:
    """Testes de criptografia"""
    
    def test_encrypt_decrypt(self):
        """Testa criptografia e descriptografia"""
        key = generate_encryption_key()
        encryptor = DataEncryption(key)
        
        original = "dados sensíveis"
        encrypted = encryptor.encrypt(original)
        decrypted = encryptor.decrypt(encrypted)
        
        assert encrypted != original
        assert decrypted == original
    
    def test_encrypt_empty_string(self):
        """Testa criptografia de string vazia"""
        key = generate_encryption_key()
        encryptor = DataEncryption(key)
        
        result = encryptor.encrypt("")
        assert result == ""
    
    def test_decrypt_empty_string(self):
        """Testa descriptografia de string vazia"""
        key = generate_encryption_key()
        encryptor = DataEncryption(key)
        
        result = encryptor.decrypt("")
        assert result == ""
    
    def test_encrypt_unicode(self):
        """Testa criptografia de unicode"""
        key = generate_encryption_key()
        encryptor = DataEncryption(key)
        
        original = "Olá! 你好 🎉"
        encrypted = encryptor.encrypt(original)
        decrypted = encryptor.decrypt(encrypted)
        
        assert decrypted == original
    
    def test_different_keys_produce_different_results(self):
        """Testa que chaves diferentes produzem resultados diferentes"""
        key1 = generate_encryption_key()
        key2 = generate_encryption_key()
        
        encryptor1 = DataEncryption(key1)
        encryptor2 = DataEncryption(key2)
        
        original = "dados"
        encrypted1 = encryptor1.encrypt(original)
        encrypted2 = encryptor2.encrypt(original)
        
        assert encrypted1 != encrypted2
    
    def test_decrypt_with_wrong_key_fails(self):
        """Testa que descriptografar com chave errada falha"""
        key1 = generate_encryption_key()
        key2 = generate_encryption_key()
        
        encryptor1 = DataEncryption(key1)
        encryptor2 = DataEncryption(key2)
        
        original = "dados"
        encrypted = encryptor1.encrypt(original)
        
        # Descriptografar com chave errada deve retornar vazio (não falhar)
        decrypted = encryptor2.decrypt(encrypted)
        assert decrypted == ""


class TestHelperFunctions:
    """Testes de funções helper"""
    
    def test_sanitize_string_helper(self):
        """Testa helper sanitize_string"""
        text = "test\x00data"
        result = sanitize_string(text)
        assert '\x00' not in result
    
    def test_validate_sql_safe_helper(self):
        """Testa helper validate_sql_safe"""
        safe = "texto normal"
        result = validate_sql_safe(safe)
        assert result == safe
        
        malicious = "test' OR 1=1 --"
        with pytest.raises(ValueError):
            validate_sql_safe(malicious)


# Para rodar os testes:
# pytest apps/backend/tests/test_security_fase3.py -v
