"""
Configuration management for The Third Voice AI
Environment-based settings with validation
"""

import os
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "The Third Voice AI"
    ENVIRONMENT: str = Field("development", description="Environment: development, production, testing")
    DEBUG: bool = Field(False, description="Enable debug mode")
    HOST: str = Field("0.0.0.0", description="Host to bind to")
    PORT: int = Field(8000, description="Port to bind to")
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    
    # Security
    SECRET_KEY: str = Field("your-secret-key-change-in-production", description="Secret key for JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="JWT access token expiry in minutes")
    DEMO_TOKEN_EXPIRE_HOURS: int = Field(24, description="Demo user token expiry in hours")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        [
            "http://localhost:3000", 
            "http://127.0.0.1:3000",
            "http://100.71.78.118:3000",  # Pi IP address for frontend
        ],
        description="Allowed CORS origins"
    )
    ALLOWED_HOSTS: List[str] = Field(
        ["localhost", "127.0.0.1", "100.71.78.118"],
        description="Allowed hosts for production"
    )
    
    # Database
    DATABASE_PATH: str = Field("thirdvoice.db", description="SQLite database path")
    CACHE_EXPIRY_DAYS: int = Field(7, description="AI response cache expiry in days")
    
    # AI Configuration
    OPENROUTER_API_KEY: Optional[str] = Field(None, description="OpenRouter API key")
    OPENROUTER_BASE_URL: str = Field("https://openrouter.ai/api/v1", description="OpenRouter API base URL")
    AI_MODEL: str = Field("meta-llama/llama-3.1-8b-instruct:free", description="Default AI model")
    MAX_TOKENS: int = Field(1000, description="Maximum tokens for AI responses")
    TEMPERATURE: float = Field(0.7, description="AI model temperature")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(100, description="Requests per minute per IP")
    RATE_LIMIT_DEMO_REQUESTS: int = Field(50, description="Requests per minute for demo users")
    
    # File Storage
    UPLOAD_MAX_SIZE: int = Field(5 * 1024 * 1024, description="Max upload size in bytes (5MB)")
    ALLOWED_FILE_TYPES: List[str] = Field(
        [".txt", ".md", ".json", ".csv"],
        description="Allowed file extensions"
    )
    
    # Email (if you plan to add email features)
    SMTP_HOST: Optional[str] = Field(None, description="SMTP server host")
    SMTP_PORT: int = Field(587, description="SMTP server port")
    SMTP_USERNAME: Optional[str] = Field(None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(None, description="SMTP password")
    SMTP_FROM_EMAIL: Optional[str] = Field(None, description="From email address")
    
    # Redis (optional - for advanced caching)
    REDIS_URL: Optional[str] = Field(None, description="Redis URL for caching")
    REDIS_HOST: str = Field("localhost", description="Redis host")
    REDIS_PORT: int = Field(6379, description="Redis port")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis password")
    REDIS_DB: int = Field(0, description="Redis database number")
    
    # Monitoring & Analytics
    ENABLE_METRICS: bool = Field(False, description="Enable application metrics")
    SENTRY_DSN: Optional[str] = Field(None, description="Sentry DSN for error tracking")
    
    # Demo Mode Settings
    DEMO_MAX_CONTACTS: int = Field(5, description="Max contacts for demo users")
    DEMO_MAX_MESSAGES: int = Field(20, description="Max messages for demo users")
    DEMO_SESSION_HOURS: int = Field(24, description="Demo session duration in hours")
    
    # Background Tasks
    CLEANUP_INTERVAL_HOURS: int = Field(6, description="How often to run cleanup tasks")
    MAX_BACKGROUND_TASKS: int = Field(10, description="Maximum concurrent background tasks")
    
    class Config:
        env_file = "/home/thirdvoice/the-third-voice-mvp/backend/.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('ENVIRONMENT')
    def validate_environment(cls, v):
        allowed = ['development', 'production', 'testing']
        if v not in allowed:
            raise ValueError(f'Environment must be one of: {allowed}')
        return v
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f'Log level must be one of: {allowed}')
        return v.upper()
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if v == "your-secret-key-change-in-production":
            import warnings
            warnings.warn("Using default secret key! Change this in production!")
        return v
    
    @validator('DATABASE_PATH')
    def validate_database_path(cls, v):
        # Ensure database directory exists
        db_path = Path(v)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return str(db_path.absolute())
    
    @validator('ALLOWED_ORIGINS', pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('ALLOWED_HOSTS', pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    @validator('OPENROUTER_API_KEY')
    def warn_missing_api_key(cls, v):
        if not v:
            import warnings
            warnings.warn(
                "OPENROUTER_API_KEY not set! AI features will use fallback responses. "
                "Set this environment variable for full functionality."
            )
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.ENVIRONMENT == "testing"
    
    @property
    def database_url(self) -> str:
        """Get database URL for SQLAlchemy (if needed)"""
        return f"sqlite:///{self.DATABASE_PATH}"
    
    @property
    def redis_url_full(self) -> str:
        """Get full Redis URL"""
        if self.REDIS_URL:
            return self.REDIS_URL
        
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment"""
        if self.is_production:
            # In production, be more restrictive
            return [origin for origin in self.ALLOWED_ORIGINS if not origin.startswith("http://localhost")]
        return self.ALLOWED_ORIGINS
    
    def get_rate_limit_per_minute(self, is_demo: bool = False) -> int:
        """Get rate limit based on user type"""
        return self.RATE_LIMIT_DEMO_REQUESTS if is_demo else self.RATE_LIMIT_REQUESTS


class TestSettings(Settings):
    """Settings for testing environment"""
    ENVIRONMENT: str = "testing"
    DATABASE_PATH: str = "test_thirdvoice.db"
    SECRET_KEY: str = "test-secret-key"
    LOG_LEVEL: str = "DEBUG"
    
    class Config:
        env_file = "/home/thirdvoice/the-third-voice-mvp/backend/.env.test"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create settings instance
def get_settings() -> Settings:
    """Get settings instance based on environment"""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "testing":
        return TestSettings()
    else:
        return Settings()


# Global settings instance
settings = get_settings()


# Utility functions for common configuration tasks
def setup_logging_level():
    """Setup logging level based on settings"""
    import logging
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))


def validate_required_settings():
    """Validate that all required settings are present"""
    required_for_production = [
        ("SECRET_KEY", "JWT secret key"),
        ("OPENROUTER_API_KEY", "OpenRouter API key"),
    ]
    
    if settings.is_production:
        missing = []
        for key, description in required_for_production:
            value = getattr(settings, key, None)
            if not value or (key == "SECRET_KEY" and value == "your-secret-key-change-in-production"):
                missing.append(f"{key} ({description})")
        
        if missing:
            raise ValueError(
                f"Missing required production settings: {', '.join(missing)}"
            )


def get_database_config():
    """Get database configuration dictionary"""
    return {
        "database": settings.DATABASE_PATH,
        "pragmas": {
            "journal_mode": "wal",
            "cache_size": -64 * 1000,  # 64MB
            "foreign_keys": 1,
            "ignore_check_constraints": 0,
            "synchronous": 0,
        }
    }


# Configuration for different environments
ENVIRONMENT_CONFIGS = {
    "development": {
        "reload": True,
        "debug": True,
        "log_level": "DEBUG",
    },
    "production": {
        "reload": False,
        "debug": False,
        "log_level": "INFO",
        "workers": 1,  # Single worker for Raspberry Pi
    },
    "testing": {
        "reload": False,
        "debug": True,
        "log_level": "DEBUG",
    }
}


def get_uvicorn_config() -> dict:
    """Get Uvicorn configuration based on environment"""
    base_config = {
        "app": "main:app",
        "host": settings.HOST,
        "port": settings.PORT,
        "log_level": settings.LOG_LEVEL.lower(),
    }
    
    env_config = ENVIRONMENT_CONFIGS.get(settings.ENVIRONMENT, {})
    base_config.update(env_config)
    
    return base_config


# Export commonly used settings
__all__ = [
    "settings",
    "Settings",
    "TestSettings", 
    "get_settings",
    "validate_required_settings",
    "get_database_config",
    "get_uvicorn_config",
    "setup_logging_level"
]