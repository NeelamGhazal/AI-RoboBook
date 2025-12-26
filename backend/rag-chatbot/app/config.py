"""
Application configuration using Pydantic Settings.
All environment variables are loaded and validated here.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenRouter Configuration (for OpenAI Agents SDK)
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "gpt-4o-mini"
    BASE_URL: str = "https://openrouter.ai/api/v1"

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
    # Add your frontend deploy URL here
    CORS_ORIGINS: str = "http://localhost:3000,https://af1596ea.ai-robo-textbook.pages.dev/"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra env vars (e.g., old Gemini config, JWT vars)
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Parse CORS origins from comma-separated string.
        This will automatically allow both localhost (dev) and deployed frontend.
        """
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

        # Optional: dynamically add frontend URL from env variable if present
        frontend_url = os.environ.get("FRONTEND_URL")
        if frontend_url and frontend_url not in origins:
            origins.append(frontend_url.strip())

        return origins


# Global settings instance
settings = Settings()
