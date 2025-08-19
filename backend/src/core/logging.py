"""
Logging configuration for The Third Voice AI
Structured logging with appropriate levels and formatting
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from .config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Setup application logging with appropriate handlers and formatters
    
    Args:
        log_level: Override the log level from settings
    """
    # Determine log level
    level = log_level or settings.LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with colored output for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    if settings.is_development:
        console_formatter = ColoredFormatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
            datefmt="%H:%M:%S"
        )
    else:
        console_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for persistent logging
    log_file = logs_dir / f"thirdvoice_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    file_handler.setLevel(numeric_level)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler for errors and above
    error_file = logs_dir / f"thirdvoice_errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        filename=error_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(lineno)d | %(message)s\n%(pathname)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    configure_third_party_loggers()
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Logging configured - Level: {level} | Environment: {settings.ENVIRONMENT}")
    
    if settings.is_development:
        logger.info(f"📁 Log files: {logs_dir.absolute()}")


def configure_third_party_loggers() -> None:
    """Configure logging levels for third-party libraries"""
    
    # Reduce noise from third-party libraries
    third_party_loggers = [
        'uvicorn.access',
        'uvicorn.error', 
        'fastapi',
        'httpx',
        'asyncio',
        'peewee',
        'slowapi'
    ]
    
    for logger_name in third_party_loggers:
        logger = logging.getLogger(logger_name)
        
        if settings.is_development:
            # Show more info in development
            logger.setLevel(logging.INFO)
        else:
            # Reduce noise in production
            logger.setLevel(logging.WARNING)
    
    # Special handling for specific loggers
    if not settings.is_development:
        # Silence uvicorn access logs in production unless debug
        logging.getLogger('uvicorn.access').setLevel(logging.ERROR)
    
    # Always show errors from these critical components
    critical_loggers = ['peewee', 'fastapi']
    for logger_name in critical_loggers:
        logging.getLogger(logger_name).setLevel(logging.ERROR)


class ColoredFormatter(logging.Formatter):
    """
    Colored log formatter for better development experience
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green  
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to level name
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        # Add emoji prefixes for better visual scanning
        emoji_map = {
            'DEBUG': '🔍',
            'INFO': '📝', 
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '💥'
        }
        
        original_msg = record.getMessage()
        
        # Don't add emoji if message already starts with one
        if not any(original_msg.startswith(emoji) for emoji in emoji_map.values()):
            emoji = emoji_map.get(record.levelname.replace(level_color, '').replace(self.COLORS['RESET'], ''), '')
            if emoji:
                record.msg = f"{emoji} {record.msg}"
        
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with consistent configuration
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class APIRequestLogger:
    """
    Middleware-compatible request logger for FastAPI
    """
    
    def __init__(self):
        self.logger = get_logger("api.requests")
    
    async def log_request(self, request, response_time: float = None):
        """Log API request details"""
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        
        # Log basic request info
        self.logger.info(
            f"{method} {url} - Client: {client_ip}"
            + (f" - {response_time:.3f}s" if response_time else "")
        )
    
    async def log_error(self, request, error: Exception):
        """Log API errors"""
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        
        self.logger.error(
            f"ERROR: {method} {url} - Client: {client_ip} - {str(error)}"
        )


def log_demo_activity(user_email: str, action: str, details: str = None):
    """
    Log demo user activity for analytics
    
    Args:
        user_email: Demo user email
        action: Action performed (login, message_processed, etc.)
        details: Additional details about the action
    """
    demo_logger = get_logger("demo.activity")
    
    log_msg = f"Demo User: {user_email} - Action: {action}"
    if details:
        log_msg += f" - {details}"
    
    demo_logger.info(log_msg)


def log_ai_processing(user_id: str, message_length: int, processing_time: float, 
                     model_used: str, success: bool = True):
    """
    Log AI processing metrics for monitoring
    
    Args:
        user_id: User identifier
        message_length: Length of processed message
        processing_time: Time taken to process
        model_used: AI model that was used
        success: Whether processing was successful
    """
    ai_logger = get_logger("ai.processing")
    
    status = "SUCCESS" if success else "FAILED"
    
    ai_logger.info(
        f"AI Processing {status} - User: {user_id[:8]}... - "
        f"Length: {message_length} chars - Time: {processing_time:.3f}s - "
        f"Model: {model_used}"
    )


def log_security_event(event_type: str, client_ip: str, details: str = None):
    """
    Log security-related events
    
    Args:
        event_type: Type of security event (rate_limit, invalid_auth, etc.)
        client_ip: Client IP address
        details: Additional event details
    """
    security_logger = get_logger("security.events")
    
    log_msg = f"SECURITY EVENT: {event_type} - IP: {client_ip}"
    if details:
        log_msg += f" - {details}"
    
    security_logger.warning(log_msg)


def log_performance_metric(metric_name: str, value: float, unit: str = "ms"):
    """
    Log performance metrics
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
    """
    perf_logger = get_logger("performance.metrics")
    
    perf_logger.info(f"METRIC: {metric_name} = {value:.3f} {unit}")


# Context managers for structured logging
class LogExecutionTime:
    """
    Context manager to log execution time of code blocks
    """
    
    def __init__(self, operation_name: str, logger: logging.Logger = None):
        self.operation_name = operation_name
        self.logger = logger or get_logger("performance")
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"🚀 Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"✅ Completed: {self.operation_name} in {duration:.3f}s")
        else:
            self.logger.error(f"❌ Failed: {self.operation_name} after {duration:.3f}s - {exc_val}")


# Export commonly used functions
__all__ = [
    'setup_logging',
    'get_logger', 
    'APIRequestLogger',
    'log_demo_activity',
    'log_ai_processing', 
    'log_security_event',
    'log_performance_metric',
    'LogExecutionTime'
]
