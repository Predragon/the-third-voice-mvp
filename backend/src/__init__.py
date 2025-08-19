# src/__init__.py
"""
The Third Voice AI - Backend Package
AI-powered communication assistant for difficult conversations
"""

__version__ = "1.0.0"
__author__ = "The Third Voice AI Team"
__description__ = "AI-powered communication assistant for difficult conversations"

# src/core/__init__.py
"""
Core package containing configuration, exceptions, and utilities
"""

from .config import settings, get_settings
from .exceptions import AppException, ValidationException, AuthenticationException
from .logging_config import setup_logging, get_logger

__all__ = [
    "settings",
    "get_settings", 
    "AppException",
    "ValidationException",
    "AuthenticationException",
    "setup_logging",
    "get_logger"
]

# src/data/__init__.py
"""
Data layer package containing models, database operations, and schemas
"""

from .database import db_manager, get_database_manager
from .schemas import (
    ContactCreate, ContactResponse, ContactUpdate,
    MessageCreate, MessageResponse, 
    UserCreate, UserResponse,
    FeedbackCreate, FeedbackResponse,
    AIResponse
)

__all__ = [
    "db_manager",
    "get_database_manager",
    "ContactCreate", "ContactResponse", "ContactUpdate",
    "MessageCreate", "MessageResponse",
    "UserCreate", "UserResponse", 
    "FeedbackCreate", "FeedbackResponse",
    "AIResponse"
]

# src/auth/__init__.py
"""
Authentication package containing JWT auth and user management
"""

from .auth_manager import (
    auth_manager,
    get_current_user,
    get_current_user_optional,
    TokenResponse,
    LoginRequest,
    DemoResponse
)

__all__ = [
    "auth_manager",
    "get_current_user", 
    "get_current_user_optional",
    "TokenResponse",
    "LoginRequest",
    "DemoResponse"
]

# src/ai/__init__.py
"""
AI engine package containing OpenRouter integration and message processing
"""

from .ai_engine import ai_engine, AIResponse

__all__ = [
    "ai_engine",
    "AIResponse"
]

# src/api/__init__.py
"""
API package containing FastAPI routes and endpoints
"""

# src/api/routes/__init__.py
"""
API routes package
"""

from . import auth, contacts, messages, feedback, health

__all__ = [
    "auth",
    "contacts", 
    "messages",
    "feedback",
    "health"
]
