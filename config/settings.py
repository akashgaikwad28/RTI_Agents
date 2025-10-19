"""
settings.py
------------
Centralized configuration manager for all environment variables and API keys.
Uses Pydantic for type validation and safe defaults.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application-wide configuration.
    Loads environment variables from .env file automatically.
    """

    # === LLM & MCP Clients ===
    GROQ_API_KEY: str = Field(..., description="API key for Groq LLM client")
    GOOGLE_API_KEY: str = Field(..., description="API key for Gemini (Google Generative AI) client")

    # === MongoDB ===
    MONGO_URI: str = Field("mongodb://localhost:27017/", description="MongoDB connection URI")
    MONGO_DB_NAME: str = Field("rti_db", description="Default MongoDB database name")

    # === Email ===
    SENDER_EMAIL: str | None = Field("rti-system@example.com", description="Sender email address for RTI notifications")
    SENDER_PASSWORD: str | None = Field(None, description="Sender email password or app token (optional)")
    ADMIN_EMAIL: str = Field("admin@example.com", description="Admin email for notifications or errors")

    # === Logging & System ===
    LOGS_DIR: str = Field("logs", description="Directory path for application logs")

    # === Translation ===
    DEFAULT_TRANSLATION_LANG: str = Field("en", description="Default translation target language")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()
