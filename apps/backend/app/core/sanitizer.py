"""
Sanitizadores para prevenir XSS (FASE 4)
Remove código malicioso de inputs HTML/JavaScript
"""
import re
from typing import Optional
import html


class HTMLSanitizer:
    """Sanitiza HTML para prevenir XSS"""
    
    # Tags HTML perigosas
    DANGEROUS_TAGS = [
        'script', 'iframe', 'object', 'embed', 'applet',
        'meta', 'link', 'style', 'base', 'form'
    ]
    
    # Atributos perigosos
    DANGEROUS_ATTRIBUTES = [
        'onerror', 'onload', 'onclick', 'onmouseover', 'onmouseout',
        'onkeydown', 'onkeyup', 'onfocus', 'onblur', 'onchange',
        'onsubmit', 'onreset', 'onselect', 'onabort'
    ]
    
    @staticmethod
    def strip_all_tags(text: str) -> str:
        """Remove TODAS as tags HTML"""
        if not text:
            return ""
        
        # Remove tags HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decodifica entidades HTML
        text = html.unescape(text)
        
        return text.strip()
    
    @staticmethod
    def sanitize(text: str) -> str:
        """Remove tags e atributos perigosos"""
        if not text:
            return ""
        
        # Remove tags perigosas
        for tag in HTMLSanitizer.DANGEROUS_TAGS:
            # Remove tag de abertura e fechamento
            text = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', text, flags=re.IGNORECASE | re.DOTALL)
            text = re.sub(f'<{tag}[^>]*/?>', '', text, flags=re.IGNORECASE)
        
        # Remove atributos perigosos
        for attr in HTMLSanitizer.DANGEROUS_ATTRIBUTES:
            text = re.sub(f'{attr}\\s*=\\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
            text = re.sub(f'{attr}\\s*=\\s*[^\\s>]*', '', text, flags=re.IGNORECASE)
        
        # Remove javascript: protocol
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        # Remove data: protocol (pode conter base64 malicioso)
        text = re.sub(r'data:[^,]*,', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    @staticmethod
    def escape_html(text: str) -> str:
        """Escapa caracteres HTML especiais"""
        if not text:
            return ""
        
        return html.escape(text)


class JavaScriptSanitizer:
    """Detecta tentativas de injeção de JavaScript"""
    
    # Padrões perigosos
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>',
        r'javascript:',
        r'onerror\s*=',
        r'onload\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<applet[^>]*>',
        r'eval\s*\(',
        r'expression\s*\(',
        r'vbscript:',
        r'data:text/html',
    ]
    
    @staticmethod
    def is_safe(text: str) -> bool:
        """Verifica se texto não contém JS malicioso"""
        if not text:
            return True
        
        text_lower = text.lower()
        
        for pattern in JavaScriptSanitizer.DANGEROUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def sanitize(text: str, field_name: str = "campo") -> str:
        """Remove padrões perigosos ou lança erro"""
        if not text:
            return ""
        
        if not JavaScriptSanitizer.is_safe(text):
            raise ValueError(f"{field_name} contém código potencialmente malicioso (XSS)")
        
        return text


class URLSanitizer:
    """Sanitiza URLs para prevenir ataques"""
    
    # Protocolos permitidos
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto', 'tel']
    
    @staticmethod
    def is_safe_url(url: str) -> bool:
        """Verifica se URL é segura"""
        if not url:
            return True
        
        url_lower = url.lower().strip()
        
        # Verificar protocolo
        if ':' in url_lower:
            protocol = url_lower.split(':')[0]
            if protocol not in URLSanitizer.ALLOWED_PROTOCOLS:
                return False
        
        # Verificar padrões perigosos
        dangerous = ['javascript:', 'data:', 'vbscript:', 'file:']
        for pattern in dangerous:
            if pattern in url_lower:
                return False
        
        return True
    
    @staticmethod
    def sanitize(url: str, field_name: str = "URL") -> str:
        """Valida e sanitiza URL"""
        if not url:
            return ""
        
        if not URLSanitizer.is_safe_url(url):
            raise ValueError(f"{field_name} contém protocolo não permitido")
        
        return url.strip()


# Funções helper para uso rápido
def strip_html_tags(text: str) -> str:
    """Remove todas as tags HTML"""
    return HTMLSanitizer.strip_all_tags(text)


def sanitize_html(text: str) -> str:
    """Sanitiza HTML removendo tags perigosas"""
    return HTMLSanitizer.sanitize(text)


def escape_html(text: str) -> str:
    """Escapa caracteres HTML"""
    return HTMLSanitizer.escape_html(text)


def validate_no_xss(text: str, field_name: str = "campo") -> str:
    """Valida que não contém XSS"""
    return JavaScriptSanitizer.sanitize(text, field_name)


def validate_safe_url(url: str, field_name: str = "URL") -> str:
    """Valida que URL é segura"""
    return URLSanitizer.sanitize(url, field_name)
