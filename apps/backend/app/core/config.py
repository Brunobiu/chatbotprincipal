from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Configurações da aplicação com validação via Pydantic
    Garante que todas as variáveis obrigatórias existem
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    OPENAI_MODEL_TEMPERATURE: str = "0"
    
    # AI Prompts
    AI_CONTEXTUALIZE_PROMPT: str
    AI_SYSTEM_PROMPT: str
    
    # RAG
    VECTOR_STORE_PATH: str = "vectorstore"
    RAG_FILES_DIR: str = "rag_files"
    
    # ChromaDB
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000
    
    # Evolution API
    EVOLUTION_API_URL: str
    EVOLUTION_INSTANCE_NAME: str
    AUTHENTICATION_API_KEY: str  # API Key da Evolution API
    
    # Redis
    CACHE_REDIS_URI: str
    BUFFER_KEY_SUFIX: str = "_msg_buffer"
    DEBOUNCE_SECONDS: str = "10"
    BUFFER_TTL: str = "300"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/whatsapp_bot"
    
    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRICE_LOOKUP_KEY: Optional[str] = None
    
    # Security
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    RATE_LIMIT_PER_MINUTE: int = 60
    WEBHOOK_API_KEY: Optional[str] = None  # API Key para proteger webhook WhatsApp
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"  # Chave secreta para JWT
    
    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@whatsappaibot.com"
    SENDGRID_FROM_NAME: str = "WhatsApp AI Bot"
    DASHBOARD_URL: str = "http://localhost:3000/login"
    
    @property
    def REDIS_URL(self) -> str:
        """Alias para compatibilidade"""
        return self.CACHE_REDIS_URI
    
    @property
    def EVOLUTION_AUTHENTICATION_API_KEY(self) -> str:
        """Alias para compatibilidade"""
        return self.AUTHENTICATION_API_KEY
    
    def get_allowed_origins_list(self) -> list[str]:
        """Retorna lista de origens permitidas para CORS"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Instância global das configurações
settings = Settings()

# Exports para compatibilidade com código existente
OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_MODEL_NAME = settings.OPENAI_MODEL_NAME
OPENAI_MODEL_TEMPERATURE = settings.OPENAI_MODEL_TEMPERATURE
AI_CONTEXTUALIZE_PROMPT = settings.AI_CONTEXTUALIZE_PROMPT
AI_SYSTEM_PROMPT = settings.AI_SYSTEM_PROMPT
VECTOR_STORE_PATH = settings.VECTOR_STORE_PATH
RAG_FILES_DIR = settings.RAG_FILES_DIR
EVOLUTION_API_URL = settings.EVOLUTION_API_URL
EVOLUTION_INSTANCE_NAME = settings.EVOLUTION_INSTANCE_NAME
EVOLUTION_AUTHENTICATION_API_KEY = settings.EVOLUTION_AUTHENTICATION_API_KEY
REDIS_URL = settings.REDIS_URL
BUFFER_KEY_SUFIX = settings.BUFFER_KEY_SUFIX
DEBOUNCE_SECONDS = settings.DEBOUNCE_SECONDS
BUFFER_TTL = settings.BUFFER_TTL
DATABASE_URL = settings.DATABASE_URL
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET
STRIPE_PRICE_LOOKUP_KEY = settings.STRIPE_PRICE_LOOKUP_KEY