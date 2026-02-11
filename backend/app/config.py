"""Application configuration settings."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Friday.AI - AI Project Management Platform"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "An intelligent project management platform for AI research lifecycle"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./friday_ai.db")

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "friday-ai-super-secret-key-change-in-production-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    # File uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    REPORT_DIR: str = os.getenv("REPORT_DIR", "./generated_reports")

    class Config:
        env_file = ".env"


settings = Settings()
