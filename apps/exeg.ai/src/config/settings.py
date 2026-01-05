"""
Configuration using Pydantic Settings.
"""
import secrets
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    API_PORT: int = 8000
    DEBUG: bool = False

    # Bible API
    BIBLIA_API_URL: str = "http://localhost:3001"
    BIBLIA_API_TIMEOUT: int = 30

    # Ollama
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:4b"
    OLLAMA_TIMEOUT: int = 120

    # OpenAI (optional)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Anthropic (optional)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"

    # FAISS
    FAISS_INDEX_PATH: str = "./indexes/faiss/bible_index.faiss"
    USE_FAISS_GPU: bool = True

    # SentenceTransformers
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_CACHE_DIR: str = "./models/sentence-transformers"

    # Paths
    DATA_DIR: str = "./data"

    # JWT Authentication
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./database/exeg.db"

    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_STARTER: Optional[str] = None
    STRIPE_PRICE_PRO: Optional[str] = None

    # Encryption (for BYOK API keys)
    ENCRYPTION_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
