"""
Validadores de segurança (FASE 3)
Protege contra SQL Injection e valida inputs
"""
import re
from typing import Optional


class EmailValidator:
    """Validador de emails"""
    
    @staticmethod
    def validate(email: str) -> str:
        """Valida e normaliza email"""
        if not email:
            raise ValueError("Email não pode ser vazio")
        
        if len(email) > 255:
            raise ValueError("Email muito longo (máx 255 caracteres)")
        
        # Normalizar
        email = email.lower().strip()
        
        # Validação básica de formato
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Formato de email inválido")
        
        return email


class StringValidator:
    """Validador e sanitizador de strings"""
    
    @staticmethod
    def sanitize(text: str, max_length: int = 500) -> str:
        """Remove caracteres perigosos e limita tamanho"""
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Limita tamanho
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove caracteres de controle (exceto \n, \r, \t)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitiza nome de arquivo"""
        if not filename:
            return ""
        
        # Remove path traversal
        filename = filename.replace('..', '')
        filename = filename.replace('/', '')
        filename = filename.replace('\\', '')
        
        # Remove caracteres especiais
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Limita tamanho
        if len(filename) > 255:
            filename = filename[:255]
        
        return filename.strip()


class SQLSafeValidator:
    """Valida que string não contém padrões de SQL injection"""
    
    # Padrões perigosos de SQL injection
    DANGEROUS_PATTERNS = [
        r"(\bOR\b\s+\d+\s*=\s*\d+)",  # OR 1=1
        r"(\bAND\b\s+\d+\s*=\s*\d+)",  # AND 1=1
        r"(--)",  # Comentário SQL
        r"(;.*\bDROP\b)",  # DROP table
        r"(;.*\bDELETE\b)",  # DELETE
        r"(;.*\bUPDATE\b)",  # UPDATE
        r"(\bUNION\b.*\bSELECT\b)",  # UNION SELECT
        r"(\/\*.*\*\/)",  # Comentário /* */
        r"(\bEXEC\b|\bEXECUTE\b)",  # EXEC
        r"(\bINSERT\b.*\bINTO\b)",  # INSERT INTO
        r"(\bSELECT\b.*\bFROM\b)",  # SELECT FROM
    ]
    
    @staticmethod
    def validate(text: str, field_name: str = "campo") -> str:
        """Valida que não contém SQL injection"""
        if not text:
            return text
        
        text_upper = text.upper()
        
        for pattern in SQLSafeValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                raise ValueError(f"{field_name} contém padrão suspeito de SQL injection")
        
        return text


class IntegerValidator:
    """Validador de inteiros"""
    
    @staticmethod
    def validate(value: int, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
        """Valida range de inteiro"""
        if not isinstance(value, int):
            raise ValueError("Valor deve ser um inteiro")
        
        if min_value is not None and value < min_value:
            raise ValueError(f"Valor deve ser >= {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValueError(f"Valor deve ser <= {max_value}")
        
        return value


class PhoneValidator:
    """Validador de telefone"""
    
    @staticmethod
    def validate(phone: str) -> str:
        """Valida e normaliza telefone"""
        if not phone:
            return ""
        
        # Remove caracteres não numéricos
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Valida tamanho (mínimo 10, máximo 15 com código país)
        if len(phone) < 10 or len(phone) > 15:
            raise ValueError("Telefone inválido (deve ter entre 10 e 15 dígitos)")
        
        return phone


# Funções helper para uso rápido
def sanitize_string(text: str, max_length: int = 500) -> str:
    """Helper para sanitizar string"""
    return StringValidator.sanitize(text, max_length)


def validate_sql_safe(text: str, field_name: str = "campo") -> str:
    """Helper para validar SQL injection"""
    return SQLSafeValidator.validate(text, field_name)


def validate_email(email: str) -> str:
    """Helper para validar email"""
    return EmailValidator.validate(email)


def validate_phone(phone: str) -> str:
    """Helper para validar telefone"""
    return PhoneValidator.validate(phone)
