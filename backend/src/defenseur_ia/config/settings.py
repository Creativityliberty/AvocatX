"""
Configuration settings pour DEFENSEUR-IA
"""

from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings (via variables d'environnement et .env)"""

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "defenseur_ia"
    POSTGRES_USER: str = "defenseur"
    POSTGRES_PASSWORD: str  # REQUIRED: Must be set via environment variable

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # API Keys (compat: deux variantes)
    LEGIFRANCE_API_KEY: str = ""
    LEGIFRANCE_API_SECRET: str = ""
    LEGIFRANCE_CLIENT_ID: str = ""
    LEGIFRANCE_CLIENT_SECRET: str = ""

    # Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 50  # mégaoctets

    # Pipeline
    MAX_CONCURRENT_PIPELINES: int = 5
    PIPELINE_TIMEOUT: int = 3600  # secondes

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30

    # Sécurité & logging
    SECRET_KEY: str  # REQUIRED: Must be set via environment variable (use: python -c "import secrets; print(secrets.token_urlsafe(32))")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LOG_LEVEL: str = "INFO"
    # Environnement d'exécution (dev, staging, production)
    environment: str = "development"

    @property
    def MAX_FILE_SIZE(self) -> int:
        """Taille maximale des fichiers en octets"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @model_validator(mode='after')
    def validate_production_secrets(self):
        """Valide que les secrets critiques sont définis en production"""
        if self.environment == "production":
            if not self.POSTGRES_PASSWORD:
                raise ValueError("POSTGRES_PASSWORD must be set in production environment")
            if not self.SECRET_KEY:
                raise ValueError("SECRET_KEY must be set in production environment")
            if self.SECRET_KEY and len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters long in production")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # ignorer les variables d'environnement non déclarées
    )


settings = Settings()
