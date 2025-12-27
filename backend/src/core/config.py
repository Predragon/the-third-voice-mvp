"""
Configuration management for The Third Voice AI
Environment-based settings with validation
"""

import os
import secrets
import platform
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import logging
from logging.handlers import RotatingFileHandler
import warnings


# ------------------------
# Settings
# ------------------------
class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    APP_NAME: str = "The Third Voice AI"
    ENVIRONMENT: str = Field("development", description="Environment: development, production, testing")
    DEBUG: bool = Field(False, description="Enable debug mode")
    HOST: str = Field("0.0.0.0", description="Host to bind to")
    PORT: int = Field(8000, description="Port to bind to")
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    # Backend Identification
    BACKEND_ID: Optional[str] = Field(None, description="Backend identifier (b1=Pi, b2=Render)")
    HOSTNAME: str = Field(default_factory=platform.node, description="System hostname")
    PLATFORM: str = Field(default_factory=platform.system, description="System platform")

    # Security
    SECRET_KEY: str = Field(..., description="Secret key for JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="JWT access token expiry in minutes")
    DEMO_TOKEN_EXPIRE_HOURS: int = Field(24, description="Demo user token expiry in hours")

    # Demo User (should be set via environment variables in production)
    DEMO_EMAIL: str = Field("demo@thethirdvoice.ai", description="Demo user email")
    DEMO_PASSWORD: str = Field("demo123", description="Demo user password")

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://100.71.78.118:3000",
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
    AI_MODEL_FALLBACK: str = Field("meta-llama/llama-3.1-8b-instruct:free", description="Fallback AI model if primary fails")
    AI_RETRY_ATTEMPTS: int = Field(3, description="Number of retry attempts for AI requests")
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

    # Health Check & Monitoring
    HEALTH_CHECK_ENABLED: bool = Field(True, description="Enable health check endpoint")
    METRICS_ENABLED: bool = Field(False, description="Enable Prometheus metrics")

    # Email
    SMTP_HOST: Optional[str] = Field(None, description="SMTP server host")
    SMTP_PORT: int = Field(587, description="SMTP server port")
    SMTP_USERNAME: Optional[str] = Field(None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(None, description="SMTP password")
    SMTP_FROM_EMAIL: Optional[str] = Field(None, description="From email address")

    # Redis
    REDIS_URL: Optional[str] = Field(None, description="Redis URL for caching")
    REDIS_HOST: str = Field("localhost", description="Redis host")
    REDIS_PORT: int = Field(6379, description="Redis port")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis password")
    REDIS_DB: int = Field(0, description="Redis database number")

    # Monitoring & Analytics
    ENABLE_METRICS: bool = Field(False, description="Enable application metrics")
    SENTRY_DSN: Optional[str] = Field(None, description="Sentry DSN for error tracking")

    # Demo Mode
    DEMO_MAX_CONTACTS: int = Field(5, description="Max contacts for demo users")
    DEMO_MAX_MESSAGES: int = Field(20, description="Max messages for demo users")
    DEMO_SESSION_HOURS: int = Field(24, description="Demo session duration in hours")

    # Background Tasks
    CLEANUP_INTERVAL_HOURS: int = Field(6, description="How often to run cleanup tasks")
    MAX_BACKGROUND_TASKS: int = Field(10, description="Maximum concurrent background tasks")

    class Config:
        env_file_encoding = "utf-8"
        case_sensitive = False

    # ------------------------
    # Validators
    # ------------------------
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

    @validator('BACKEND_ID', pre=True, always=True)
    def set_backend_id(cls, v, values):
        """Auto-detect backend ID if not explicitly set"""
        if v:  # If explicitly set in environment, use it
            return v
            
        # Auto-detection logic
        if os.getenv('RENDER'):
            return 'b2'  # Render deployment
        elif os.getenv('HEROKU_APP_NAME'):
            return 'heroku'
        elif os.getenv('VERCEL'):
            return 'vercel'
        elif os.getenv('RAILWAY_ENVIRONMENT'):
            return 'railway'
        elif os.getenv('FLY_APP_NAME'):
            return 'fly'
        elif os.getenv('GOOGLE_CLOUD_PROJECT'):
            return 'gcp'
        elif os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
            return 'aws'
        elif os.getenv('AZURE_FUNCTIONS_ENVIRONMENT'):
            return 'azure'
        else:
            # Check hostname for Pi server or local development
            hostname = platform.node().lower()
            if any(keyword in hostname for keyword in ['pi', 'raspberry', 'thirdvoice']):
                return 'b1'  # Pi server
            elif any(keyword in hostname for keyword in ['local', 'dev', 'localhost']):
                return 'dev'  # Development environment
            else:
                return 'b1'  # Default to Pi server

    @validator('SECRET_KEY', pre=True)
    def validate_secret_key(cls, v, values):
        # Get environment from values or fallback to env var
        env = values.get("ENVIRONMENT") or os.getenv("ENVIRONMENT", "development")
        
        # Handle missing or default values
        if not v or v == "your-secret-key-change-in-production":
            if env == "production":
                raise ValueError(
                    "SECRET_KEY must be set in production. Add it to .env.production or set as environment variable."
                )
            
            # Generate a key for development/testing
            generated_key = secrets.token_hex(32)
            if env != "testing":  # Don't spam warnings during tests
                warnings.warn(
                    f"Using generated SECRET_KEY for {env} environment. "
                    "Set SECRET_KEY in your .env file for consistent behavior."
                )
            return generated_key
        
        # Validate length
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long for security.")
        
        return v

    @validator('DATABASE_PATH')
    def ensure_database_directory(cls, v):
        """Enhanced database path validation"""
        db_path = Path(v)
        
        # Ensure parent directory exists and is writable
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check write permissions on parent directory
        if not os.access(db_path.parent, os.W_OK):
            raise ValueError(f"No write permission for database directory: {db_path.parent}")
        
        return str(db_path.absolute())

    @validator('PORT')
    def validate_port(cls, v):
        """Ensure port is in valid range"""
        if not (1024 <= v <= 65535):
            if v < 1024:
                warnings.warn("Using privileged port (<1024). Ensure proper permissions.")
            elif v > 65535:
                raise ValueError("Port must be <= 65535")
        return v

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

    @validator('AI_MODEL')
    def validate_ai_model(cls, v):
        """Ensure AI model is not empty and follows expected format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("AI_MODEL cannot be empty")
        return v.strip()

    @validator('OPENROUTER_API_KEY')
    def warn_missing_api_key(cls, v, values):
        if not v and values.get("ENVIRONMENT") != "testing":
            warnings.warn(
                "OPENROUTER_API_KEY not set! AI features may fail. "
                "Set OPENROUTER_API_KEY in your .env file."
            )
        return v

    # ------------------------
    # Properties
    # ------------------------
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

    def get_backend_info(self) -> dict:
        """Get comprehensive backend information for debugging and monitoring"""
        return {
            'backend_id': self.BACKEND_ID,
            'hostname': self.HOSTNAME,
            'platform': self.PLATFORM,
            'environment': self.ENVIRONMENT,
            'debug': self.DEBUG,
            'app_name': self.APP_NAME,
            'detection_hints': {
                'render': bool(os.getenv('RENDER')),
                'heroku': bool(os.getenv('HEROKU_APP_NAME')),
                'vercel': bool(os.getenv('VERCEL')),
                'railway': bool(os.getenv('RAILWAY_ENVIRONMENT')),
                'fly': bool(os.getenv('FLY_APP_NAME')),
                'is_pi': any(keyword in self.HOSTNAME.lower() 
                           for keyword in ['pi', 'raspberry', 'thirdvoice']),
                'is_local': any(keyword in self.HOSTNAME.lower() 
                              for keyword in ['local', 'dev', 'localhost'])
            }
        }

    def log_loaded_settings(self):
        """Log key settings on startup (without secrets)"""
        logger = logging.getLogger(__name__)
        logger.info(f"🚀 Starting {self.APP_NAME}")
        logger.info(f"Environment: {self.ENVIRONMENT}")
        logger.info(f"Backend ID: {self.BACKEND_ID}")
        logger.info(f"Hostname: {self.HOSTNAME}")
        logger.info(f"Platform: {self.PLATFORM}")
        logger.info(f"Debug mode: {self.DEBUG}")
        logger.info(f"Host:Port: {self.HOST}:{self.PORT}")
        logger.info(f"Database: {self.DATABASE_PATH}")
        logger.info(f"AI Model: {self.AI_MODEL}")
        logger.info(f"CORS Origins: {len(self.ALLOWED_ORIGINS)} configured")
        
        if self.OPENROUTER_API_KEY:
            logger.info("✅ OpenRouter API key configured")
        else:
            logger.warning("⚠️ OpenRouter API key not set")


# ------------------------
# Test settings
# ------------------------
class TestSettings(Settings):
    ENVIRONMENT: str = "testing"
    DATABASE_PATH: str = "test_thirdvoice.db"
    SECRET_KEY: str = secrets.token_hex(32)
    LOG_LEVEL: str = "DEBUG"


# ------------------------
# Dynamic env file selection
# ------------------------
env_name = os.getenv("ENVIRONMENT", "development")
env_file_map = {
    "development": ".env",
    "production": ".env.production",
    "testing": ".env.testing",
}
BASE_DIR = Path(__file__).parent.parent.parent
env_file_path = BASE_DIR / env_file_map.get(env_name, ".env")


def get_settings() -> Settings:
    """Enhanced settings loader with better error handling"""
    
    if env_name == "testing":
        return TestSettings()
    
    # Load the environment file manually first
    if env_file_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file_path, override=True)
        logger = logging.getLogger(__name__)
        logger.info(f"✅ Loaded environment from {env_file_path}")
    else:
        if env_name == "production":
            raise FileNotFoundError(f"❌ Required file not found: {env_file_path}")
        else:
            warnings.warn(f"⚠️ Env file {env_file_path} not found.")
    
    # Create settings instance (will pick up loaded environment variables)
    settings_instance = Settings()
    settings_instance.log_loaded_settings()
    
    return settings_instance


settings = get_settings()


# ------------------------
# Logging setup
# ------------------------
def setup_logging_level():
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()

    log_level = getattr(logging, settings.LOG_LEVEL)
    log_format = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # Rotating file handler
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    logger.setLevel(log_level)
    if not hasattr(setup_logging_level, "configured"):
        logger.info(f"Logging configured - Level: {settings.LOG_LEVEL} | Environment: {settings.ENVIRONMENT}")
        logger.info(f"Log files: {log_dir}")
        setup_logging_level.configured = True


# ------------------------
# Validation
# ------------------------
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


# ------------------------
# Database config
# ------------------------
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


# ------------------------
# Uvicorn config
# ------------------------
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


# ------------------------
# Exports
# ------------------------
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