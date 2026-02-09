"""
Serviço para gerenciar configurações de IA
"""
from sqlalchemy.orm import Session
import base64

from app.db.models.ia_configuracao import IAConfiguracao


class IAConfigService:
    
    @staticmethod
    def get_provedor_ativo(db: Session) -> IAConfiguracao | None:
        """Retorna o provedor ativo"""
        return db.query(IAConfiguracao).filter_by(ativo=True, configurado=True).first()
    
    @staticmethod
    def decrypt_key(encrypted: str) -> str:
        """Descriptografa API key"""
        return base64.b64decode(encrypted.encode()).decode()
    
    @staticmethod
    def get_api_key_ativa(db: Session) -> tuple[str, str, str] | None:
        """
        Retorna (provedor, modelo, api_key) do provedor ativo
        Retorna None se nenhum configurado
        """
        config = IAConfigService.get_provedor_ativo(db)
        
        if not config or not config.api_key_encrypted:
            return None
        
        api_key = IAConfigService.decrypt_key(config.api_key_encrypted)
        
        return (config.provedor, config.modelo, api_key)
