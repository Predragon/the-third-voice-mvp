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
