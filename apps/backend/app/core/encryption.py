"""
Criptografia de dados sensíveis (FASE 3)
Protege PII (Personally Identifiable Information)
"""
import base64
import os
from cryptography.fernet import Fernet
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DataEncryption:
    """Criptografia de dados sensíveis usando Fernet (AES-128)"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Inicializa encriptador
        
        Args:
            encryption_key: Chave de criptografia (base64). Se None, usa variável de ambiente.
        """
        if encryption_key is None:
            encryption_key = os.getenv('ENCRYPTION_KEY')
        
        if not encryption_key:
            # Gerar chave temporária para desenvolvimento
            logger.warning("⚠️ ENCRYPTION_KEY não configurada! Usando chave temporária (NÃO USE EM PRODUÇÃO)")
            encryption_key = Fernet.generate_key().decode()
        
        try:
            self.cipher = Fernet(encryption_key.encode())
        except Exception as e:
            logger.error(f"Erro ao inicializar criptografia: {e}")
            raise ValueError("Chave de criptografia inválida")
    
    def encrypt(self, data: str) -> str:
        """
        Criptografa string
        
        Args:
            data: String para criptografar
            
        Returns:
            String criptografada em base64
        """
        if not data:
            return ""
        
        try:
            encrypted = self.cipher.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Erro ao criptografar dados: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Descriptografa string
        
        Args:
            encrypted_data: String criptografada em base64
            
        Returns:
            String original
        """
        if not encrypted_data:
            return ""
        
        try:
            decoded = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Erro ao descriptografar dados: {e}")
            # Retornar vazio ao invés de falhar (dados podem estar corrompidos)
            return ""
    
    def encrypt_if_not_empty(self, data: Optional[str]) -> Optional[str]:
        """Helper para criptografar apenas se não vazio"""
        if data:
            return self.encrypt(data)
        return None
    
    def decrypt_if_not_empty(self, encrypted_data: Optional[str]) -> Optional[str]:
        """Helper para descriptografar apenas se não vazio"""
        if encrypted_data:
            return self.decrypt(encrypted_data)
        return None


# Instância global (singleton)
_encryptor_instance = None


def get_encryptor() -> DataEncryption:
    """Retorna instância global do encriptador"""
    global _encryptor_instance
    
    if _encryptor_instance is None:
        _encryptor_instance = DataEncryption()
    
    return _encryptor_instance


# Funções helper para uso rápido
def encrypt_data(data: str) -> str:
    """Helper para criptografar dados"""
    return get_encryptor().encrypt(data)


def decrypt_data(encrypted_data: str) -> str:
    """Helper para descriptografar dados"""
    return get_encryptor().decrypt(encrypted_data)


def generate_encryption_key() -> str:
    """Gera nova chave de criptografia"""
    return Fernet.generate_key().decode()


# Para uso em produção, adicione ao .env:
# ENCRYPTION_KEY=<chave_gerada_por_generate_encryption_key()>
