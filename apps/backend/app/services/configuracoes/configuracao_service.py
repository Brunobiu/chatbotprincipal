"""
Service para gerenciar configurações do bot
"""
from sqlalchemy.orm import Session
from typing import Optional

from app.db.models.configuracao_bot import ConfiguracaoBot, TomEnum


class ConfiguracaoService:
    """Service para CRUD de configurações do bot"""
    
    # Mensagens padrão
    DEFAULTS = {
        "mensagem_saudacao": "Olá! 👋 Como posso ajudar você hoje?",
        "mensagem_fallback": "Desculpe, não tenho informações sobre isso no momento. Um atendente humano irá te responder em breve! 🙋",
        "mensagem_espera": "Aguarde um momento, estou processando sua solicitação... ⏳",
        "mensagem_retorno_24h": "Olá! Notei que você tinha uma dúvida. Posso ajudar agora? 😊"
    }
    
    @staticmethod
    def buscar_ou_criar(db: Session, cliente_id: int) -> ConfiguracaoBot:
        """
        Busca configuração do cliente ou cria uma nova com valores padrão
        """
        config = db.query(ConfiguracaoBot).filter(
            ConfiguracaoBot.cliente_id == cliente_id
        ).first()
        
        if not config:
            config = ConfiguracaoBot(
                cliente_id=cliente_id,
                tom=TomEnum.CASUAL,
                mensagem_saudacao=ConfiguracaoService.DEFAULTS["mensagem_saudacao"],
                mensagem_fallback=ConfiguracaoService.DEFAULTS["mensagem_fallback"],
                mensagem_espera=ConfiguracaoService.DEFAULTS["mensagem_espera"],
                mensagem_retorno_24h=ConfiguracaoService.DEFAULTS["mensagem_retorno_24h"]
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        
        return config
    
    @staticmethod
    def atualizar(
        db: Session,
        cliente_id: int,
        tom: Optional[str] = None,
        mensagem_saudacao: Optional[str] = None,
        mensagem_fallback: Optional[str] = None,
        mensagem_espera: Optional[str] = None,
        mensagem_retorno_24h: Optional[str] = None
    ) -> ConfiguracaoBot:
        """
        Atualiza configurações do bot
        """
        config = ConfiguracaoService.buscar_ou_criar(db, cliente_id)
        
        if tom is not None:
            # Converter string para enum (case-insensitive)
            tom_lower = tom.lower()
            if tom_lower == "formal":
                config.tom = TomEnum.FORMAL
            elif tom_lower == "casual":
                config.tom = TomEnum.CASUAL
            elif tom_lower == "tecnico":
                config.tom = TomEnum.TECNICO
        
        if mensagem_saudacao is not None:
            config.mensagem_saudacao = mensagem_saudacao
        if mensagem_fallback is not None:
            config.mensagem_fallback = mensagem_fallback
        if mensagem_espera is not None:
            config.mensagem_espera = mensagem_espera
        if mensagem_retorno_24h is not None:
            config.mensagem_retorno_24h = mensagem_retorno_24h
        
        db.commit()
        db.refresh(config)
        
        return config
