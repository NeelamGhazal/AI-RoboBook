"""
Application configuration using Pydantic Settings.
All environment variables are loaded and validated here.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Gemini Configuration (Free Tier)
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"  # Fast, free tier
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"  # 768 dimensions, free

    # Qdrant Cloud Configuration
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "textbook_chunks"

    # Neon Serverless Postgres
    NEON_DATABASE_URL: str

    # Database Pool Configuration
    DB_POOL_MIN_SIZE: int = 5
    DB_POOL_MAX_SIZE: int = 20

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False

    # CORS Configuration (comma-separated origins)
    CORS_ORIGINS: str = "http://localhost:3000"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
