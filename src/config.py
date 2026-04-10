"""
Configuration management for Smart Escalation API.

This module defines the Settings class using Pydantic for environment variable
management with validation and default values.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables or .env file.
    """
    
    # LLM API Configuration
    google_api_key: str
    
    # Embedding Model Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Escalation Logic Configuration
    relevance_threshold: float = 0.5
    top_k_chunks: int = 3
    
    # Chunking Configuration
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # LLM Configuration
    llm_model: str = "gemini-1.5-flash"
    llm_temperature: float = 0.3
    
    # Server Configuration
    port: int = 8000
    host: str = "0.0.0.0"
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
