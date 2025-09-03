"""
Configuration management for The Third Voice AI
Environment-based settings with validation
"""

import os
import secrets
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

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
    SECRET_KEY: str = Field(..., description="Secret key for JWT")  # Require SECRET_KEY
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
    MAX_TOKENS: int = Field(1000, description="Maximum tokens for AI responses")
    TEMPERATURE: float = Field(0.7, description="AI model temperature")
    API_TIMEOUT: float = Field(30.0, description="Timeout for OpenRouter API calls in seconds")

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
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

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

    @validator('SECRET_KEY', pre=True)
    def validate_secret_key(cls, v, values):
        if not v or v == "your-secret-key-change-in-production":
            if values.get("ENVIRONMENT") == "production":
                raise ValueError("SECRET_KEY must be set in production. Add it to .env file.")
            import warnings
            generated_key = secrets.token_hex(32)
            warnings.warn(
                f"Using generated SECRET_KEY for {values.get('ENVIRONMENT', 'unknown')} environment. "
                "Set SECRET_KEY in .env for consistent behavior."
            )
            return generated_key
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long for security.")
        return v

    @validator('DATABASE_PATH')
    def validate_database_path(cls, v):
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
    def warn_missing_api_key(cls, v, values):
        if not v and values.get("ENVIRONMENT") != "testing":
            import warnings
            warnings.warn(
                "OPENROUTER_API_KEY not set! AI features may fail with 402 (Payment Required) or 404 (Not Found) errors. "
                "Set OPENROUTER_API_KEY in .env file. Get it from https://openrouter.ai. "
                "Check account credits to avoid 402 errors."
            )
        return v

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.DATABASE_PATH}"

    @property
    def redis_url_full(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_cors_origins(self) -> List[str]:
        if self.is_production:
            return [origin for origin in self.ALLOWED_ORIGINS if not origin.startswith("http://localhost")]
        return self.ALLOWED_ORIGINS

    def get_rate_limit_per_minute(self, is_demo: bool = False) -> int:
        return self.RATE_LIMIT_DEMO_REQUESTS if is_demo else self.RATE_LIMIT_REQUESTS


class TestSettings(Settings):
    ENVIRONMENT: str = "testing"
    DATABASE_PATH: str = "test_thirdvoice.db"
    SECRET_KEY: str = secrets.token_hex(32)
    LOG_LEVEL: str = "DEBUG"

    class Config:
        env_file = ".env.test"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development")
    return TestSettings() if env == "testing" else Settings()


settings = get_settings()


def setup_logging_level():
    """Setup logging level based on settings with rotating file handler"""
    logger = logging.getLogger()

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    log_level = getattr(logging, settings.LOG_LEVEL)
    log_format = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # Rotating file handler (max 5MB, keep 5 backups)
    log_dir = Path("/data/data/com.termux/files/home/the-third-voice-mvp/backend/logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    logger.setLevel(log_level)
    # Only log configuration once per process
    if not hasattr(setup_logging_level, "configured"):
        logger.info(f"Logging configured - Level: {settings.LOG_LEVEL} | Environment: {settings.ENVIRONMENT}")
        logger.info(f"Log files: {log_dir}")
        logger.info("Note: Check disk space with 'df -h' to ensure logs don't fill storage.")
        setup_logging_level.configured = True


def validate_required_settings():
    required_for_production = [
        ("SECRET_KEY", "JWT secret key"),
        ("OPENROUTER_API_KEY", "OpenRouter API key"),
    ]

    if settings.is_production:
        missing = []
        for key, description in required_for_production:
            value = getattr(settings, key, None)
            if not value:
                missing.append(f"{key} ({description})")
        if missing:
            raise ValueError(f"Missing required production settings: {', '.join(missing)}")


def get_database_config():
    return {
        "database": settings.DATABASE_PATH,
        "pragmas": {
            "journal_mode": "wal",
            "cache_size": -64 * 1000,
            "foreign_keys": 1,
            "ignore_check_constraints": 0,
            "synchronous": 0,
        }
    }


ENVIRONMENT_CONFIGS = {
    "development": {
        "reload": True,
        "log_level": "debug",
    },
    "production": {
        "reload": False,
        "log_level": "info",
        "workers": 1,
    },
    "testing": {
        "reload": False,
        "log_level": "debug",
    }
}


def get_uvicorn_config() -> dict:
    base_config = {
        "app": "main:app",
        "host": settings.HOST,
        "port": settings.PORT,
        "log_level": settings.LOG_LEVEL.lower(),
    }
    env_config = ENVIRONMENT_CONFIGS.get(settings.ENVIRONMENT, {})
    base_config.update(env_config)
    return base_config


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