# config/settings.py
"""
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
    GEMINI_API_KEY: str = Field(..., description="API key for Gemini (Google Generative AI) client")
    TRANSLATOR_API_KEY: str | None = Field(None, description="API key for translator client (optional)")
    TRANSLATOR_API_ENDPOINT: str = Field("https://libretranslate.de", description="Endpoint for LibreTranslate API")

    # === MongoDB ===
    MONGO_URI: str = Field("mongodb://localhost:27017/", description="MongoDB connection URI")
    MONGO_DB_NAME: str = Field("rti_db", description="Default MongoDB database name")

    # === Email ===
    SENDER_EMAIL: str = Field("rti-system@example.com", description="Sender email address for RTI notifications")
    SENDER_PASSWORD: str | None = Field(None, description="Sender email password or app token (optional)")
    ADMIN_EMAIL: str = Field("admin@rti-system.com", description="Admin email for escalations and alerts")

    # === Logging ===
    LOG_LEVEL: str = Field("DEBUG", description="Logging level for application")

    class Config:
        env_file = ".env"
        extra = "ignore"  # Allows extra fields in .env without crashing



settings = Settings()