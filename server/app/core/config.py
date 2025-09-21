from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost:5432/jobtracker"
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN: int = 900  # 15 minutes
    JWT_REFRESH_EXPIRES_IN: int = 2592000  # 30 days
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    EMAIL_FROM: str = "Job Tracker <noreply@jobtracker.com>"
    
    # App
    APP_BASE_URL: str = "http://localhost:5173"
    REMINDER_DEFAULT_TIME: str = "07:30"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
