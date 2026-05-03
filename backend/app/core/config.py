"""
Application configuration settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ML Diabetes Tracker"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"
    
    # CORS - Frontend domain whitelist
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100  # 100 requests per minute per user
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/ml_diabetes_tracker"
    )
    
    # ML Model Configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./ml_models")
    
    # Encryption (AES-256)
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key-32-chars-long")
    
    # Data Retention (HIPAA compliance)
    DATA_RETENTION_DAYS: int = 30  # Days before permanent deletion
    
    # Audit Logging
    AUDIT_LOG_RETENTION_YEARS: int = 7  # HIPAA requirement


settings = Settings()